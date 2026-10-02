# RESULTS_STATUS.md

## What is confirmed (independently reverified by Notebook 13)

- Bridgeport source document: 304 pages, hash `afe7c678fa5dfc85...`
- 24 canonical Bridgeport districts; 1941 hierarchy nodes; 392
  raw table candidates (32 verified structured,
  75 diagram/unverified).
- GIS crosswalk: 16/24 districts have an exact GIS match.
- Four previously PyMuPDF-undetected table families (HEIGHT, BUILDING SITING, PARKING, ALLOWED USES)
  fully recovered, 13/13 building types each, with full page provenance.
- V7 (3+-unit entitlement): 24
  allowed-by-right / 6
  not-available-by-right / 20
  not-applicable, across 50 (district, building_form) scenarios.
- V12 (missing-middle entitlement): 27
  present / 23 absent, same 50 scenarios.
- Of the 44-scenario Phase-2-registry-plus-addendum universe used for scoring, **28 scenarios
  are score-eligible** under a rule declared before any score was computed.
- Notebook 12's pilot index: Bridgeport's 28 eligible scenarios range 0.099
  to 0.649 (0=least, 1=most restrictive);
  Greenwich's RA-4 reference point sits at approximately 0.63.

## What remains provisional

- Whether V7 and V12's new scenario-level resolution should formally update Notebook 09's original
  **cross-town** (district-level, both-towns-required) score-readiness count is an open question this
  notebook deliberately does not resolve -- see `variable_score_readiness_validation_matrix.csv`.
  **No "9/12" or "8/12" claim is asserted as fact by this repository.**
- 0 of 5 deterministic legal-semantic
  conflation checks failed this run -- see `legal_semantic_validation_findings.csv` for which ones,
  if any, and their severity.

## What is explicitly NOT claimed anywhere in this repository

- No Bridgeport or Greenwich town-level composite score.
- No Bridgeport-vs-Greenwich ranking or "winner."
- No dominant district selection.
- No statewide percentile.
- No causal claim about zoning restrictiveness and housing outcomes.
