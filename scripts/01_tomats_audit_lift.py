from pathlib import Path
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

EXCEL_PATH = "TOMATSannotations2025 2.xlsx"
ANNOTATOR_SHEETS = ["Annotator1-J", "Annotator2", "Annotator3-E"]  # edit if needed
TEXT_COL = "Text"
OUTPUT_DIR = Path("outputs/tomats")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EMOTIONS = ["anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"]

def clean_label(x):
    if pd.isna(x):
        return None
    x = str(x).strip().lower()
    return x if x in EMOTIONS else None

def load_tomats():
    xls = pd.ExcelFile(EXCEL_PATH)
    ann_dfs = {}
    for sheet in ANNOTATOR_SHEETS:
        ann_id = sheet.split("-")[0]
        df = pd.read_excel(xls, sheet_name=sheet)

        # IMPORTANT: apply the same filter used to obtain the 1,677 text units.
        # If the imported workbook includes header/material rows, remove them here.
        # Example only:
        # df = df[df[TEXT_COL].notna()].copy()
        # df = df[df[TEXT_COL].astype(str).str.strip().ne("Text")].copy()

        df[TEXT_COL] = df[TEXT_COL].astype(str)
        ann_dfs[ann_id] = df.reset_index(drop=True)
    return ann_dfs

def emotion_columns(df):
    cols = [c for c in df.columns if str(c).strip().lower() in {"emotion1", "emotion2", "emotion3"}]
    order = {"emotion1": 1, "emotion2": 2, "emotion3": 3}
    cols = sorted(cols, key=lambda c: order[str(c).strip().lower()])
    if len(cols) != 3:
        raise ValueError(f"Expected Emotion1/2/3, found {cols}")
    return cols

def label_sets(df):
    cols = emotion_columns(df)
    out = []
    for _, row in df.iterrows():
        s = {clean_label(row[c]) for c in cols}
        s.discard(None)
        out.append(s)
    return out

def audit(df, annotator):
    cols = emotion_columns(df)
    print(f"\n===== {annotator} =====")
    print("Rows:", len(df))
    for col in cols:
        n = df[col].apply(lambda x: clean_label(x) is not None).sum()
        print(f"{col} core labels:", n)
    sets = label_sets(df)
    labelled = [s for s in sets if s]
    print("Rows with >=1 core emotion:", len(labelled))
    print("Mean core labels per labelled item:", np.mean([len(s) for s in labelled]) if labelled else np.nan)
    weaker = df[
        df["Emotion1"].apply(lambda x: clean_label(x) is None)
        & (df["Emotion2"].apply(lambda x: clean_label(x) is not None) | df["Emotion3"].apply(lambda x: clean_label(x) is not None))
    ]
    print("No core Emotion1 but core Emotion2/3:", len(weaker))
    if len(weaker):
        weaker[[TEXT_COL, "Emotion1", "Emotion2", "Emotion3"]].to_csv(
            OUTPUT_DIR / f"{annotator}_later_slot_emotions.csv", index=False
        )

def compute_lift(sets, labelled_only=True):
    if labelled_only:
        sets = [s for s in sets if s]
    N = len(sets)
    marg = {e: sum(e in s for s in sets) for e in EMOTIONS}
    rows = []
    for e1, e2 in itertools.combinations(EMOTIONS, 2):
        n_joint = sum(e1 in s and e2 in s for s in sets)
        p1, p2 = marg[e1] / N, marg[e2] / N
        p_joint = n_joint / N
        expected = p1 * p2
        lift = p_joint / expected if expected > 0 else np.nan
        rows.append({
            "emotion1": e1, "emotion2": e2, "N_items": N,
            "n_emotion1": marg[e1], "n_emotion2": marg[e2],
            "n_joint": n_joint, "p_joint": p_joint,
            "p_expected": expected, "lift": lift
        })
    return pd.DataFrame(rows).sort_values("lift", ascending=False)

def cooccurrence_matrix(sets):
    m = pd.DataFrame(0, index=EMOTIONS, columns=EMOTIONS, dtype=int)
    for s in sets:
        for a, b in itertools.combinations(sorted(s), 2):
            m.loc[a, b] += 1
            m.loc[b, a] += 1
    np.fill_diagonal(m.values, 0)
    return m

if __name__ == "__main__":
    ann_dfs = load_tomats()
    all_lift = []
    for annotator in ["Annotator1", "Annotator3"]:
        df = ann_dfs[annotator]
        audit(df, annotator)
        sets = label_sets(df)
        lift = compute_lift(sets, labelled_only=True)
        lift.insert(0, "annotator", annotator)
        all_lift.append(lift)
        print(f"\n{annotator} labelled-item lift")
        print(lift[["emotion1", "emotion2", "n_joint", "lift"]].head(15).to_string(index=False))
        co = cooccurrence_matrix(sets)
        co.to_csv(OUTPUT_DIR / f"{annotator}_cooccurrence_counts.csv")

    pd.concat(all_lift, ignore_index=True).to_csv(
        OUTPUT_DIR / "tomats_within_annotator_lift.csv", index=False
    )
