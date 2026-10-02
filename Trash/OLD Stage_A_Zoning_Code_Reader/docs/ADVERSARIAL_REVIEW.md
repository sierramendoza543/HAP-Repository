# ADVERSARIAL_REVIEW.md

A skeptical-reviewer checklist with real, audit-grounded answers from this notebook's own findings.

## Source and law

**Q: Is every governing claim supported by primary law rather than a summary?**
A: Every canonical matrix row traces to a `source_page` in the original PDF (hash-verified unchanged
this run). Manually transcribed table-family cells were read directly from the rendered source page,
not from a summary. Unresolved risk: amendment/effective-date tracking is not independently verified
in this pass (the source_metadata.json files record a single capture date each; no amendment-history
check was performed). Artifact: `data/raw/*/source_metadata.json`.

**Q: Are cited sections/pages actually applicable to the stated district/form/site?**
A: Section I's integrity tests confirm every scenario row's `district_code` is a valid, registered
district. Row-level district/form applicability (e.g. "does page 80 actually govern House A in
NX2") was manually verified at transcription time (Notebooks 07, 08, 10), not re-derived
algorithmically in this pass. Artifact: `integrity_test_results.csv`.

## Extraction

**Q: Did PDF layout cause dropped/misassigned table headers or values?**
A: Yes, documented directly: PyMuPDF's detector missed four entire table families (HEIGHT, BUILDING
SITING, PARKING, ALLOWED USES) across all 13 building types -- the project's single largest
extraction-correctness finding, recovered manually in Notebooks 07, 08, 10. Section F of this
notebook independently reverified the recovered counts against source files.

**Q: Which results depend on manual transcription, and can another reviewer reproduce it?**
A: All HEIGHT/BUILDING SITING/PARKING/ALLOWED-USES cell values. Reproducibility means: another
reviewer can re-render the cited page and re-check the cited cell -- not that re-running code
regenerates the transcription from scratch. See `REPRODUCIBILITY.md`.

## Scenario model

**Q: Is a scenario legally real or analytically invented?**
A: Section I verified every scenario's district_code against the 24-row canonical registry; no
scenario was found with an invalid district. The Small General addendum (2
rows) was added only because real, directly-read source evidence (pages 56-57) was found for it --
not to fill an analysis grid.

**Q: Is a scenario omitted because it is impossible, nonresidential, uncertain, or merely not
recovered?**
A: Mixed, and disclosed: `confirmed_not_applicable` scenarios (e.g. CX/Workshop) are genuinely
nonresidential by source text. Scenarios outside the 44-scenario registry (e.g. House A/NX2) were
omitted from Phase-3 scoring purely because the Phase-2 registry never enumerated them -- real
evidence for them exists and is preserved, not discarded (`step_03_v7_v12_evidence_out_of_scope_this_pass.csv`).

## GIS

**Q: What does the GIS extract represent and omit?**
A: 2000 parcel-level/parcel-derived features; 8
of 24 districts are `ordinance_only` (legally defined, not GIS-mapped in
this extract). See `GIS_METHODS_AND_LIMITATIONS.md` for the full scope statement.

## Variables

**Q: Is a "genuine absence" actually a search failure?**
A: Section D checked that every `genuine_absence_after_targeted_search` row carries a non-null
rationale/search-trail field -- see `genuine_absence_audit.csv` for the actual completeness
percentage found this run, not an assumed 100%.

**Q: Are variables double-counting one underlying restriction?**
A: The dependency map (`DEPENDENCY_AND_DOUBLE_COUNTING.md`) declares 8 variable-pair relationships
and their treatment. Notebook 12 explicitly checked (and logged its reasoning) for whether V7 and
V11 shared the same underlying citation for the scenarios it scored, rather than applying a blanket
discount.

## Results and claims

**Q: What results are confirmed vs. provisional vs. pending?**
A: See `RESULTS_STATUS.md` for the itemized split.

**Q: What would change the conclusions?**
A: (1) A re-verification of the manually transcribed cells by an independent second reviewer;
(2) resolving whether Notebook 10/11's scenario-level V7/V12 readiness should update Notebook 09's
original cross-town score-readiness count (currently left as an explicitly open question, not
asserted); (3) completing the Phase-2 scenario registry beyond Small General, which would expand the
Phase-3 eligible-scenario count beyond 28/44.

**Q: What is required before any score can be published (not just a labeled pilot)?**
A: A second-reviewer spot-check of a sample of manually transcribed cells; a decision on the
cross-town score-readiness question above; and, per `KNOWN_LIMITATIONS.md`, either acceptance of the
pilot's disclosed coverage gaps or a dedicated recovery pass to close them (V1 in particular).
