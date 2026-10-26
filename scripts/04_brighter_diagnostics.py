from pathlib import Path
import itertools
import numpy as np
import pandas as pd

BRIGHTER_PATH = "eng.csv"
ITEM_COL = "id"  # change if needed
OUTPUT_DIR = Path("outputs/brighter")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EMOTIONS = ["anger", "fearanx", "happiness", "sadness", "social_warmth", "surprise"]

def binary_entropy(p):
    if p <= 0 or p >= 1: return 0.0
    return -(p*np.log2(p) + (1-p)*np.log2(1-p))

def mean_pairwise_abs(values):
    values = np.asarray(values, float)
    if len(values) < 2: return np.nan
    d = np.abs(values[:,None] - values[None,:])
    iu = np.triu_indices(len(values), 1)
    return d[iu].mean()

if __name__ == "__main__":
    df = pd.read_csv(BRIGHTER_PATH)
    presence = (df[EMOTIONS] > 0).astype(int)
    rows = []
    for a,b in itertools.combinations(EMOTIONS,2):
        pa,pb = presence[a].mean(), presence[b].mean()
        pab = ((presence[a] == 1) & (presence[b] == 1)).mean()
        rows.append({"emotion1":a,"emotion2":b,"lift":pab/(pa*pb) if pa>0 and pb>0 else np.nan,"p_joint":pab})
    lift = pd.DataFrame(rows).sort_values("lift", ascending=False)
    lift.to_csv(OUTPUT_DIR / "brighter_lift.csv", index=False)
    print(lift.to_string(index=False))

    item_rows = []
    for item_id,g in df.groupby(ITEM_COL, sort=False):
        for emotion in EMOTIONS:
            vals = pd.to_numeric(g[emotion], errors="coerce").dropna().to_numpy()
            if not len(vals): continue
            p = np.mean(vals > 0)
            pos = vals[vals > 0]
            cond = mean_pairwise_abs(pos)/2.0 if len(pos) >= 3 else np.nan
            item_rows.append({"item_id":item_id,"emotion":emotion,"n_ratings":len(vals),"n_positive":len(pos),"presence_entropy":binary_entropy(p),"conditional_intensity_distance":cond})
    item = pd.DataFrame(item_rows)
    item.to_csv(OUTPUT_DIR / "brighter_item_emotion_disagreement.csv", index=False)
    summary = item.groupby("emotion").agg(
        mean_presence_entropy=("presence_entropy","mean"),
        mean_conditional_intensity=("conditional_intensity_distance","mean"),
        n_items=("item_id","nunique"),
        n_items_conditional=("conditional_intensity_distance", lambda x: x.notna().sum())
    ).reset_index()
    summary.to_csv(OUTPUT_DIR / "brighter_presence_intensity_summary.csv", index=False)
    print(summary.to_string(index=False))
