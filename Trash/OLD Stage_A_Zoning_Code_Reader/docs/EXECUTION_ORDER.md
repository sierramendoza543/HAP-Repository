# EXECUTION_ORDER.md

## Canonical notebook execution sequence

1. `notebooks/01_collection_phase.ipynb` -- Greenwich Phase 1 collection
2. `notebooks/02_phase_2_extraction_and_phase_3_scoring.ipynb` -- Greenwich Phase 2 extraction / Greenwich prototype scoring
3. `notebooks/04_bridgeport_collection_phase.ipynb` -- Bridgeport Phase 1 collection
4. `notebooks/05_bridgeport_all_district_extraction_and_comparability.ipynb` -- Bridgeport Stage 0 schema + Phase 2 all-district extraction
5. `notebooks/06_bridgeport_visual_diagram_recovery_and_validation.ipynb` -- Bridgeport Phase 2.5 VLM/visual-recovery infrastructure
6. `notebooks/07_bridgeport_targeted_visual_table_recovery.ipynb` -- Bridgeport Phase 2.6 HEIGHT/PARKING targeted visual recovery
7. `notebooks/08_fixed_variable_targeted_recovery_bridgeport_greenwich.ipynb` -- Bridgeport Phase 2.7 fixed-variable recovery matrix
8. `notebooks/09_expanded_variable_recovery_and_score_readiness.ipynb` -- Expanded 12-variable registry + score readiness
9. `notebooks/10_bridgeport_master_use_table_and_parking_completion.ipynb` -- Bridgeport Phase 2.8 master-use-table + PARKING completion
10. `notebooks/11_bridgeport_score_readiness_integration.ipynb` -- Phase 3 pre-score integration gate
11. `notebooks/12_bridgeport_phase3_pilot_scenario_scoring.ipynb` -- Phase 3 pilot scenario-level scoring
12. `notebooks/13_repository_finalization_and_research_validation.ipynb` -- this notebook (finalization/audit; depends on all prior notebooks' outputs but performs no new extraction)

## What can be rerun automatically

All 11 pipeline notebooks (01-12, excluding this one) execute end-to-end via
`jupyter nbconvert --to notebook --execute --inplace` against the project `.venv`, with 0 embedded
errors as of this audit (0 total errors found across all notebooks in this run).

## What requires manual review to reproduce exactly

- Every manually transcribed table-family record (HEIGHT, BUILDING SITING, PARKING, ALLOWED USES) --
  a second reviewer must independently re-read the cited PDF page to verify, not just re-run code.
- Any `candidate_found_needs_manual_review` or `pending_visual_recovery` record.

## What requires source access

- Re-deriving anything from the raw PDFs or GIS GeoJSON requires the exact files in `data/raw/`,
  whose hashes are checked at the top of this notebook and recorded in
  `repository_finalization_manifest.json`.

## What cannot currently be reconstructed from repository state alone

- The exact package-version environment each notebook 01-12 was *originally* run under (see
  `reproducibility_gaps.csv`, `ENVIRONMENT.md`).
- A live VLM inference pass (Notebook 06's infrastructure was never exercised against a real model).
