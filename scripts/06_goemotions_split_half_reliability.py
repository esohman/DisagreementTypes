from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, pearsonr

DATA_DIR = Path("goemotions_raw")
FILES = ["goemotions_1.csv", "goemotions_2.csv", "goemotions_3.csv"]
ITEM_COL = "id"
RATER_COL = "rater_id"
UNCLEAR_COL = "example_very_unclear"
OUTPUT_DIR = Path("outputs/goemotions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EMOTIONS = ["admiration","amusement","anger","annoyance","approval","caring","confusion","curiosity","desire","disappointment","disapproval","disgust","embarrassment","excitement","fear","gratitude","grief","joy","love","nervousness","optimism","pride","realization","relief","remorse","sadness","surprise","neutral"]
MIN_MATCHED = 100
N_SPLITS = 1000
SEED = 20261026

def load_data():
    return pd.concat([pd.read_csv(DATA_DIR/f) for f in FILES], ignore_index=True)

def unclear_bool(s):
    if pd.api.types.is_bool_dtype(s): return s.fillna(False)
    return s.fillna(0).astype(int).astype(bool)

def row_deltas(df):
    clear = df.loc[~unclear_bool(df[UNCLEAR_COL])].copy()
    clear["label_count"] = clear[EMOTIONS].fillna(0).astype(float).sum(axis=1)
    grp = clear.groupby(ITEM_COL)["label_count"].agg(["sum","count"])
    clear = clear.join(grp, on=ITEM_COL, rsuffix="_item")
    n_other = clear["count"] - 1
    clear["other_mean_labels"] = np.where(n_other>0,(clear["sum"]-clear["label_count"])/n_other,np.nan)
    clear["cardinality_delta"] = clear["label_count"] - clear["other_mean_labels"]
    return clear[clear["cardinality_delta"].notna()].copy()

def spearman_brown(r):
    return (2*r)/(1+r) if np.isfinite(r) and r > -1 else np.nan

if __name__ == "__main__":
    rows = row_deltas(load_data())
    counts = rows.groupby(RATER_COL).size()
    eligible = counts[counts >= MIN_MATCHED].index
    rows = rows[rows[RATER_COL].isin(eligible)].copy()
    grouped = {rid:g.copy() for rid,g in rows.groupby(RATER_COL)}
    print(f"Eligible raters: {len(grouped)}")

    rng = np.random.default_rng(SEED)
    reps = []
    for rep in range(N_SPLITS):
        h1, h2 = {}, {}
        for rid,g in grouped.items():
            idx = rng.permutation(len(g))
            cut = len(idx)//2
            a,b = g.iloc[idx[:cut]], g.iloc[idx[cut:]]
            if len(a) and len(b):
                h1[rid] = a["cardinality_delta"].mean()
                h2[rid] = b["cardinality_delta"].mean()
        common = sorted(set(h1)&set(h2))
        x = np.array([h1[r] for r in common], float)
        y = np.array([h2[r] for r in common], float)
        sr = spearmanr(x,y).statistic
        pr = pearsonr(x,y).statistic
        reps.append({"rep":rep,"n_raters":len(common),"spearman_r":sr,"spearman_brown_spearman":spearman_brown(sr),"pearson_r":pr,"spearman_brown_pearson":spearman_brown(pr)})

    out = pd.DataFrame(reps)
    out.to_csv(OUTPUT_DIR / "goemotions_split_half_reliability_repetitions.csv", index=False)
    summary=[]
    for col in ["spearman_r","spearman_brown_spearman","pearson_r","spearman_brown_pearson"]:
        v=out[col].dropna()
        summary.append({"metric":col,"median":v.median(),"mean":v.mean(),"q025":v.quantile(.025),"q975":v.quantile(.975),"min":v.min(),"max":v.max()})
    summary=pd.DataFrame(summary)
    summary.to_csv(OUTPUT_DIR / "goemotions_split_half_reliability_summary.csv", index=False)
    print(summary.to_string(index=False))
