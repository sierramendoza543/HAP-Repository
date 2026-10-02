# COMPARABILITY_FRAMEWORK.md

## Controlled comparability statuses

`directly_comparable`, `comparable_with_documented_transform`, `qualitative_only`,
`structurally_non_equivalent`, `not_applicable`, `needs_manual_harmonization` (see
`STATUS_TAXONOMY.md`). The generic `missing` value is prohibited in this field exactly as in evidence
status.

## Non-conflation rules enforced

stories != feet; ground-story height != total building height; FAR != lot coverage; open/pervious/
green area != lot coverage; frontage != lot width (unless source-defined equivalent); build-to !=
conventional setback; accessory/parking setback != principal-building setback; two-family != 3+-unit
multifamily. Section E of Notebook 13 runs deterministic, executable checks for a representative
subset of these against the live data -- see `legal_semantic_validation_findings.csv`.

## Known cross-form limitation

V5 (placement) explicitly carries two structurally distinct sub-rubrics (conventional summed-setback
vs. build-to flexibility) that are independently normalized and never cross-converted in raw feet
(enforced in Notebook 12, verified again in Section E of this notebook).
