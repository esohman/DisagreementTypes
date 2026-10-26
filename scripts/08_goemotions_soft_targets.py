from pathlib import Path
import pandas as pd

DATA_DIR = Path("goemotions_raw")
FILES = ["goemotions_1.csv", "goemotions_2.csv", "goemotions_3.csv"]
ITEM_COL = "id"
UNCLEAR_COL = "example_very_unclear"
OUTPUT_DIR = Path("outputs/goemotions_soft_targets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EMOTIONS = ["admiration","amusement","anger","annoyance","approval","caring","confusion","curiosity","desire","disappointment","disapproval","disgust","embarrassment","excitement","fear","gratitude","grief","joy","love","nervousness","optimism","pride","realization","relief","remorse","sadness","surprise","neutral"]

# Review this mapping against the valence-collapse paper before using it as a final condition.
POSITIVE={"admiration","amusement","approval","caring","desire","excitement","gratitude","joy","love","optimism","pride","relief"}
NEGATIVE={"anger","annoyance","disappointment","disapproval","disgust","embarrassment","fear","grief","nervousness","remorse","sadness"}

def unclear_bool(s):
    if pd.api.types.is_bool_dtype(s): return s.fillna(False)
    return s.fillna(0).astype(int).astype(bool)

if __name__ == "__main__":
    df=pd.concat([pd.read_csv(DATA_DIR/f) for f in FILES], ignore_index=True)
    clear=df.loc[~unclear_bool(df[UNCLEAR_COL])].copy()
    clear.groupby(ITEM_COL)[EMOTIONS].mean().reset_index().to_csv(OUTPUT_DIR/"goemotions_soft_finegrained.csv",index=False)
    clear["positive_any"]=clear[list(POSITIVE)].max(axis=1)
    clear["negative_any"]=clear[list(NEGATIVE)].max(axis=1)
    clear["neutral_any"]=clear["neutral"]
    clear.groupby(ITEM_COL)[["positive_any","negative_any","neutral_any"]].mean().reset_index().to_csv(OUTPUT_DIR/"goemotions_soft_valence_collapsed.csv",index=False)
    print("Saved soft fine-grained and collapsed targets.")
