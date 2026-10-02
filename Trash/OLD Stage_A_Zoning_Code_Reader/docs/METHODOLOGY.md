# METHODOLOGY.md

## Conceptual model

Every zoning rule is keyed to a scenario `r_{d,b,f,k}` where `d` = district, `b` = building
form/type or use, `f` = site/frontage/condition, and `k` = the variable (V1-V12). This replaces a
single per-district value with a scenario-aware model, because Bridgeport's form-based code varies
real rules (unit caps, setbacks, parking) by building type and site condition within the same
district -- collapsing to one district-level value would silently discard real legal variation. See
`docs/SCENARIO_MODEL.md`.

## Source hierarchy

Both towns' zoning codes were parsed into a hierarchy of sections/subsections (Bridgeport:
1941 nodes, independently reverified in Section F of Notebook 13), native text
tokens, and PyMuPDF table-detection candidates (392
raw candidates for Bridgeport, 32 verified as
structured tables, 75 flagged
diagram/unverified).

## Table/diagram recovery

PyMuPDF's table detector missed four recurring, templated table families that repeat once per
Bridgeport building type: HEIGHT, BUILDING SITING, PARKING & ACCESSORY STRUCTURES, and ALLOWED
USES/master-use-table. Each was found via document-wide hierarchy search, rendered at 200-400 DPI,
and manually transcribed by a human reviewer with full page/table/row/column provenance -- never
algorithmically inferred. See `docs/VISUAL_TABLE_RECOVERY.md`.

## Manual verification

Every manually transcribed value carries source page, table/section path, and (where applicable)
row/column labels. Promotion from a visual candidate to `confirmed` required direct human
verification against the rendered source page -- never a VLM output alone (Notebook 06's VLM
infrastructure was built but never exercised against a live model; see `REPRODUCIBILITY.md`). See
`docs/MANUAL_REVIEW_PROTOCOL.md`.

## GIS's role

GIS data (Bridgeport: 2000 parcel-level features) is used only for spatial
context and district-crosswalk diagnostics, never as a substitute for ordinance text and never to
establish legal entitlement. See `docs/GIS_METHODS_AND_LIMITATIONS.md`.

## Variable framework

12 variables (V1-V12), each with a predeclared operational definition, accepted legal forms, and
explicit prohibited conflations, declared *before* extraction. See `docs/VARIABLE_REGISTRY.md`.

## Comparability and missingness

See `docs/COMPARABILITY_FRAMEWORK.md` and `docs/STATUS_TAXONOMY.md`. The project prohibits a generic
`"missing"` status anywhere in a canonical evidence field -- Section B of this notebook independently
verified zero violations of that rule across all canonical matrices as of this run.

## Future scoring boundary

Notebook 12 produced a labeled **pilot** scenario-level index for Bridgeport (28 of 44 eligible
scenarios, nine variables, six sensitivity variants, explicit coverage disclosure) and a single
Greenwich reference point. This is explicitly not a validated, production, or cross-town score --
see `docs/RESULTS_STATUS.md` for exactly what is and is not claimed.
