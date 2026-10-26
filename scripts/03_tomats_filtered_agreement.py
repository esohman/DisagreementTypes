from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

EXCEL_PATH = "TOMATSannotations2025 2.xlsx"
SHEETS = {"A1": "Annotator1-J", "A2": "Annotator2", "A3": "Annotator3-E"}
OUTPUT_DIR = Path("outputs/tomats")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EMOTIONS = ["anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"]

def clean_label(x):
    if pd.isna(x): return None
    x = str(x).strip().lower()
    return x if x in EMOTIONS else None

def load_sheet(sheet):
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet)
    # Apply the SAME 1,677-item filter as scripts 01–02.
    return df.reset_index(drop=True)

def binary_matrix(df):
    rows = []
    for _, row in df.iterrows():
        s = {clean_label(row[c]) for c in ["Emotion1", "Emotion2", "Emotion3"]}
        s.discard(None)
        rows.append([int(e in s) for e in EMOTIONS])
    return np.asarray(rows, dtype=int)

def pair_scores(a, b, mask):
    a, b = a[mask], b[mask]
    per = [f1_score(a[:, j], b[:, j], zero_division=0) for j in range(len(EMOTIONS))]
    return float(np.mean(per)), f1_score(a.ravel(), b.ravel(), zero_division=0)

if __name__ == "__main__":
    dfs = {k: load_sheet(v) for k, v in SHEETS.items()}
    Y = {k: binary_matrix(v) for k, v in dfs.items()}
    a2_has_core = Y["A2"].sum(axis=1) > 0
    rows = []
    for p, q in [("A1","A2"),("A1","A3"),("A2","A3")]:
        for cond, mask in [("Full", np.ones(len(Y[p]), bool)), ("Filtered", a2_has_core)]:
            macro, micro = pair_scores(Y[p], Y[q], mask)
            rows.append({"pair": f"{p}–{q}", "condition": cond, "n_items": int(mask.sum()), "macro_f1": macro, "micro_f1": micro})
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))
    out.to_csv(OUTPUT_DIR / "tomats_full_vs_filtered_f1.csv", index=False)
