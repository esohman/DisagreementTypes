# The Structure of Disagreement in Emotion Annotation — analysis code

This package collects the analysis code used or specified for the current disagreement-types paper.

## Contents

- `scripts/01_tomats_audit_lift.py`
  - loads the TOMATS Excel workbook
  - audits row/slot counts
  - treats `none` as absence in a slot, while retaining valid later-slot emotions
  - computes labels per labelled item
  - computes within-annotator co-occurrence and lift for A1/A3

- `scripts/02_tomats_cross_overlap.py`
  - computes A1–A3 cross-annotator emotion overlap
  - row-normalizes the overlap matrix

- `scripts/03_tomats_filtered_agreement.py`
  - computes pairwise per-emotion binary F1
  - reports macro- and micro-F1 for the full TOMATS data
  - repeats the calculation on the A2-labelled subset

- `scripts/04_brighter_diagnostics.py`
  - BRIGHTER within-judgment co-occurrence lift
  - presence disagreement using binary entropy
  - conditional-intensity disagreement using mean pairwise absolute distance among positive ratings

- `scripts/05_goemotions_diagnostics.py`
  - item-adjusted label cardinality
  - general restrictive/expansive response-style scores
  - pair-specific merge tendency for six neighboring emotion pairs
  - residualizes pair-specific merging against overall breadth
  - `example_very_unclear` rates

- `scripts/06_goemotions_split_half_reliability.py`
  - repeated split-half reliability of GoEmotions item-adjusted label cardinality
  - Spearman and Pearson correlations
  - Spearman–Brown corrected reliability

- `scripts/07_goemotions_pair_permutation.py`
  - optional permutation null for pair-specific residual spread

- `scripts/08_goemotions_soft_targets.py`
  - optional helper for the separate SoftBCE / valence-collapse work
  - aggregates full individual GoEmotions annotations into per-item soft fine-grained targets
  - does not train a model

## TOMATS note

The workbook used in the paper contains 1,677 textual units. If the worksheet import includes non-item/header/material rows, remove them **before analysis** using the row-filter hook supplied in each TOMATS script.

`none` is treated as "no primary/slot emotion selected", not as a global no-emotion judgment. This matches the clarification that A3 sometimes entered `none` in Emotion1 when only a weaker secondary emotion was present, while still recording that secondary/tertiary emotion in later slots. Valid Emotion2/Emotion3 labels are therefore retained.

## GoEmotions note

The split-half script is the check needed before describing broad-vs-narrow annotation behavior as persistent/stable. It repeatedly splits each eligible rater's matched items in half, correlates their item-adjusted cardinality across halves, and applies the Spearman–Brown correction.
