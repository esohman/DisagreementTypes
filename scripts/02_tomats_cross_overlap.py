from pathlib import Path
import pandas as pd
import numpy as np

EXCEL_PATH = "TOMATSannotations2025 2.xlsx"
SHEET_A1 = "Annotator1-J"
SHEET_A3 = "Annotator3-E"
TEXT_COL = "Text"
OUTPUT_DIR = Path("outputs/tomats")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EMOTIONS = ["anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"]

def clean_label(x):
    if pd.isna(x): return None
    x = str(x).strip().lower()
    return x if x in EMOTIONS else None

def get_sets(df):
    out = []
    for _, row in df.iterrows():
        s = {clean_label(row[c]) for c in ["Emotion1", "Emotion2", "Emotion3"]}
        s.discard(None)
        out.append(s)
    return out

def load_sheet(sheet):
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
    # Apply the SAME 1,677-item row filter as script 01.
    return df.reset_index(drop=True)

if __name__ == "__main__":
    a1 = load_sheet(SHEET_A1)
    a3 = load_sheet(SHEET_A3)
    if len(a1) != len(a3):
        raise ValueError("A1 and A3 must be aligned on identical item rows.")
    s1, s3 = get_sets(a1), get_sets(a3)
    counts = pd.DataFrame(0, index=EMOTIONS, columns=EMOTIONS, dtype=int)
    for left, right in zip(s1, s3):
        for e1 in left:
            for e3 in right:
                counts.loc[e1, e3] += 1
    norm = counts.div(counts.sum(axis=1).replace(0, np.nan), axis=0)
    counts.to_csv(OUTPUT_DIR / "A1_A3_cross_overlap_counts.csv")
    norm.to_csv(OUTPUT_DIR / "A1_A3_cross_overlap_row_normalized.csv")
