# The Structure of Disagreement in Emotion Annotation

Reproducibility materials for the paper **The Structure of Disagreement in Emotion Annotation**.

This repository contains analysis code and derived outputs for three emotion-annotation resources:

- **TOMATS**: multilabel emotion annotations of 1,677 approximately sentence-level units from Ernest Hemingway's *The Old Man and the Sea*.
- **BRIGHTER**: individual ordinal emotion ratings.
- **GoEmotions**: individual multilabel emotion annotations with persistent rater identifiers.

The paper examines several forms of disagreement, including semantic overlap, annotator-specific boundary behavior, procedural sparsity, general annotation breadth, and the distinction between disagreement over emotion presence and disagreement over intensity.

## Repository structure

```text
README.md
LICENSE
DATA_LICENSE.md
requirements.txt
CITATION.cff

data/
    README.md

scripts/
    00_run_all.py
    01_tomats_audit_lift.py
    02_tomats_cross_overlap.py
    03_tomats_filtered_agreement.py
    04_brighter_diagnostics.py
    05_goemotions_diagnostics.py
    06_goemotions_split_half_reliability.py
    07_goemotions_pair_permutation.py
    08_make_figures.py

outputs/
    manuscript_summary_tables/
    figures/
```

Scripts `01`--`07` are the paper-analysis scripts already maintained in the main repository. This package adds the repository documentation, licensing files, an execution wrapper, and a figure-generation scaffold.

## Reproducing the analyses

1. Obtain the source datasets from their original distributions and place them as described in `data/README.md`.
2. Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the analyses in order:

```bash
python scripts/00_run_all.py
```

4. Regenerate final manuscript figures:

```bash
python scripts/08_make_figures.py
```

The individual scripts may also be run separately.

## Manuscript mapping

- `01_tomats_audit_lift.py`: TOMATS row/slot audit; labels per labelled item; within-annotator co-occurrence and lift.
- `02_tomats_cross_overlap.py`: A1--A3 cross-annotator overlap and row-normalized overlap matrix.
- `03_tomats_filtered_agreement.py`: full and A2-filtered pairwise macro/micro F1.
- `04_brighter_diagnostics.py`: BRIGHTER co-occurrence lift; presence disagreement; conditional-intensity disagreement.
- `05_goemotions_diagnostics.py`: item-adjusted label cardinality; restrictive/expansive response style; pair-specific merge tendency; residualized pair-specific boundary behavior; `example_very_unclear` rates.
- `06_goemotions_split_half_reliability.py`: repeated split-half reliability of GoEmotions item-adjusted label cardinality.
- `07_goemotions_pair_permutation.py`: optional permutation null for pair-specific residual spread.
- `08_make_figures.py`: final publication-style figures.

## Data redistribution

The copyrighted text of *The Old Man and the Sea* is **not** redistributed. TOMATS annotation and derived tables should be keyed by sentence/item index only. See `DATA_LICENSE.md` and `data/README.md`.

BRIGHTER and GoEmotions are not redistributed here; users should obtain them from their original distributions under their respective licenses.

## Contact

Emily Öhman, Waseda University
