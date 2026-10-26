from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path("goemotions_raw")
FILES = ["goemotions_1.csv", "goemotions_2.csv", "goemotions_3.csv"]
ITEM_COL = "id"
RATER_COL = "rater_id"
UNCLEAR_COL = "example_very_unclear"
OUTPUT_DIR = Path("outputs/goemotions")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EMOTIONS = ["admiration","amusement","anger","annoyance","approval","caring","confusion","curiosity","desire","disappointment","disapproval","disgust","embarrassment","excitement","fear","gratitude","grief","joy","love","nervousness","optimism","pride","realization","relief","remorse","sadness","surprise","neutral"]
PAIRS = [("anger","annoyance"),("fear","nervousness"),("joy","excitement"),("sadness","grief"),("gratitude","admiration"),("surprise","realization")]
MIN_MATCHED = 100
MIN_PAIR_MATCHED = 20

def load_data():
    return pd.concat([pd.read_csv(DATA_DIR/f) for f in FILES], ignore_index=True)

def unclear_bool(s):
    if pd.api.types.is_bool_dtype(s): return s.fillna(False)
    return s.fillna(0).astype(int).astype(bool)

def add_cardinality_delta(clear):
    clear = clear.copy()
    clear["label_count"] = clear[EMOTIONS].fillna(0).astype(float).sum(axis=1)
    grp = clear.groupby(ITEM_COL)["label_count"].agg(["sum","count"])
    clear = clear.join(grp, on=ITEM_COL, rsuffix="_item")
    n_other = clear["count"] - 1
    clear["other_mean_labels"] = np.where(n_other > 0, (clear["sum"]-clear["label_count"])/n_other, np.nan)
    clear["cardinality_delta"] = clear["label_count"] - clear["other_mean_labels"]
    return clear

def pair_tendency(clear,a,b):
    x = clear.copy()
    x["both"] = ((x[a]>0)&(x[b]>0)).astype(float)
    grp = x.groupby(ITEM_COL)["both"].agg(["sum","count"])
    x = x.join(grp, on=ITEM_COL, rsuffix="_item")
    n_other = x["count"] - 1
    x["other_mean_both"] = np.where(n_other>0,(x["sum"]-x["both"])/n_other,np.nan)
    x["pair_delta"] = x["both"] - x["other_mean_both"]
    return x[x["pair_delta"].notna()].groupby(RATER_COL).agg(n_pair_matched=("pair_delta","size"),merge_tendency=("pair_delta","mean")).reset_index()

if __name__ == "__main__":
    df = load_data()
    unclear = unclear_bool(df[UNCLEAR_COL])
    rates = pd.DataFrame({RATER_COL:df[RATER_COL],"unclear":unclear}).groupby(RATER_COL).agg(n_annotations=("unclear","size"),unclear_rate=("unclear","mean")).reset_index()
    rates.to_csv(OUTPUT_DIR / "goemotions_unclear_rates.csv", index=False)
    active_rates = rates[rates["n_annotations"] >= 100]
    print("Unclear range >=100 annotations:", active_rates["unclear_rate"].min(), active_rates["unclear_rate"].max())

    clear = add_cardinality_delta(df.loc[~unclear].copy())
    breadth = clear[clear["cardinality_delta"].notna()].groupby(RATER_COL).agg(
        n_matched=("cardinality_delta","size"),
        item_adjusted_cardinality=("cardinality_delta","mean"),
        mean_labels_clear=("label_count","mean")
    ).reset_index()
    active = breadth[breadth["n_matched"] >= MIN_MATCHED].copy()
    active.to_csv(OUTPUT_DIR / "goemotions_rater_breadth.csv", index=False)
    print(active["item_adjusted_cardinality"].describe().to_string())

    all_pairs = []
    for a,b in PAIRS:
        p = pair_tendency(clear,a,b).merge(active[[RATER_COL,"item_adjusted_cardinality"]], on=RATER_COL, how="inner")
        p = p[p["n_pair_matched"] >= MIN_PAIR_MATCHED].copy()
        p["pair"] = f"{a}--{b}"
        if len(p) >= 3:
            slope, intercept = np.polyfit(p["item_adjusted_cardinality"], p["merge_tendency"], 1)
            p["predicted_merge"] = intercept + slope*p["item_adjusted_cardinality"]
            p["boundary_residual"] = p["merge_tendency"] - p["predicted_merge"]
        else:
            p["boundary_residual"] = np.nan
        print(f"{a}--{b}: {len(p)} raters")
        all_pairs.append(p)
    pd.concat(all_pairs, ignore_index=True).to_csv(OUTPUT_DIR / "goemotions_pair_boundary_residuals.csv", index=False)
