# Data setup

The repository does not redistribute BRIGHTER, GoEmotions, or the copyrighted text of *The Old Man and the Sea*.

## TOMATS

Expected input: the TOMATS annotation workbook used in the original analysis.

The public release should contain annotation/derived tables keyed by sentence or item index only. Do not include the literary text itself.

TOMATS annotation and derived tables released by the authors are licensed under CC BY 4.0; see `../DATA_LICENSE.md`.

## BRIGHTER

Obtain BRIGHTER from its original distribution. The dataset is licensed under CC BY 4.0.

The scripts expect the individual-level English annotation release containing ordinal 0--3 ratings for the six dimensions used in the paper:

- anger
- fear/anxiety
- happiness
- sadness
- social warmth
- surprise

Update paths in the analysis script or use the expected filenames documented there.

## GoEmotions

Obtain the raw GoEmotions annotation files from the original Google Research distribution. The dataset is licensed under CC BY 4.0.

The paper uses the raw individual-annotation release with persistent rater identifiers and the `example_very_unclear` field.

## Important

For reproducibility, retain the original downloaded source files unchanged and write all intermediate and derived outputs to a separate directory.
