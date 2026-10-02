# RESEARCH_PROTOCOL.md

## Fixed variables

V1-V12, declared in `expanded_variable_registry_v1.csv` before any Phase-3 scoring work began (see
`VARIABLE_REGISTRY.md`). Variable definitions were not altered after seeing how easy or hard they
were to extract -- the project explicitly considered and rejected "redefine variables around what's
easy to find" as a strategy (recorded in-session), opting instead to build targeted recovery
techniques for the originally defined variables.

## Unit of analysis

A (district, building_form_or_type) **scenario**, not a district and not a town. Town-level
aggregation is explicitly out of scope for any claim in this repository.

## Inclusion/exclusion logic for the Notebook 12 pilot index

A scenario is score-eligible only if it appears in the Phase-2 scenario registry (or the narrowly
scoped Small-General addendum) AND both V7 and V12 are resolved AND at least 6 of the remaining 7
candidate variables are resolved. This rule was declared in Notebook 11 before Notebook 12 computed
any score, and was not loosened after seeing that only 28 of 44 scenarios qualified.

## Manual-review policy

See `MANUAL_REVIEW_PROTOCOL.md`. A visual-table candidate may be promoted to `confirmed` only via
direct human verification against the rendered source page; a VLM output alone is never sufficient
to promote a record to `confirmed` (Notebook 06's own stated policy, upheld throughout).

## Validation protocol

Every new notebook in this project ends with an explicit, assert-backed validation cell plus a
hash-based baseline-unchanged check on every file it reads. Notebook 13 (this one) adds an
independent, outside-the-pipeline re-verification pass against the same underlying files.

## Change-control policy

All corrections are additive (new, separately named files), never in-place edits to a baseline file.
Every override records the prior value, the new value, the source evidence, and the reason. See
`SCHEMA_CONTRACTS.md`.

## Claim discipline

No score, ranking, dominant-district selection, statewide percentile, or causal claim appears
anywhere in this repository as of the date of this notebook's execution. See `RESULTS_STATUS.md`.
