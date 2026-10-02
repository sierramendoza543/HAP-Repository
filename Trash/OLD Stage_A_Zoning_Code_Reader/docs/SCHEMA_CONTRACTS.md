# SCHEMA_CONTRACTS.md

## Contract: every canonical evidence row

Every row in a canonical matrix (`fixed_variable_recovery_matrix_*`, `expanded_variable_recovery_matrix_*`,
and their Notebook 10+ addenda) must have:
- a `final_determination` (or equivalent) value drawn only from the controlled vocabulary in
  `STATUS_TAXONOMY.md` -- independently verified in Section B of this notebook
  (22 undocumented values found this run).
- provenance fields appropriate to its source type (see `PROVENANCE_STANDARD.md`).
- for any `genuine_absence_after_targeted_search` row, a non-null `rationale`/search-trail field
  (see `genuine_absence_audit.csv`, Section D).

## Contract: every override/addendum row

Must be a **new row in a new file**, never an in-place edit. Must be traceable to a prior baseline
record where one exists (district_code + building_form_or_type + variable_id join key, used
throughout Notebooks 10-12).

## Contract: every scenario row

Must have a `district_code` drawn from the 24-row `bridgeport_district_metadata.csv` registry
(verified in Section I, integrity test `all_baseline_scenario_district_codes_are_valid`) and a
`scenario_id` matching the `bridgeport-scenario-NNNN` format (verified in Section I).
