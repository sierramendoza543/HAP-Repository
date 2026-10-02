# Housing Accountability Pipeline (HAP) -- Stage A Zoning Code Reader

## Purpose

A source-grounded evidence pipeline that extracts, verifies, and organizes zoning-code rules for
Bridgeport, CT and Greenwich, CT, as a foundation for a future interactive, evidence-linked
zoning-comparison tool. It is **not** a scoring tool in its current state, and this repository
produces **no final municipal score, ranking, dominant-district selection, statewide percentile, or
causal claim**.

## Research question

To what extent, and under what explicit legal forms, do Bridgeport's and Greenwich's zoning codes
constrain housing development -- and can that evidence be organized rigorously enough, with full
source provenance, to eventually support a defensible comparative index?

## Scope

- **Greenwich:** Phase 1 collection + Phase 2 extraction for the RA-4 prototype district (and any
  other already-processed units); see `notebooks/01_collection_phase.ipynb`,
  `notebooks/02_phase_2_extraction_and_phase_3_scoring.ipynb`.
- **Bridgeport:** full-document Phase 1 collection (24 districts), Phase 2 all-district scenario-aware
  extraction, Phase 2.5-2.8 visual-recovery passes for four previously-undetected table families
  (HEIGHT, BUILDING SITING, PARKING & ACCESSORY STRUCTURES, ALLOWED USES/master-use-table), a
  12-variable (V1-V12) comparability framework, and a Phase 3 pilot scenario-level scoring exercise.

## Current completion status

See `docs/RESULTS_STATUS.md` for the precise, per-variable state and `docs/VALIDATION_REPORT.md` for
this notebook's full audit result. In one line: **evidence recovery and a scenario-level pilot
scoring exercise are both complete; a validated, cross-town production score is not.**

## How to navigate this repository

- `notebooks/` -- the canonical, numbered pipeline (see `docs/EXECUTION_ORDER.md`).
- `data/raw/` -- original, immutable source documents (PDFs, GIS GeoJSON, source metadata with hashes).
- `data/interim/`, `data/processed/` -- derived artifacts; see `docs/ARTIFACT_MAP.md` for what's
  canonical vs. intermediate vs. additive-correction-only.
- `outputs/tables/`, `outputs/figures/`, `outputs/review/`, `outputs/logs/` -- generated tables,
  figures, review queues, and run manifests.
- `docs/` -- this documentation package.

## No-score statement

No interactive deliverable, final municipal score, town ranking, dominant-district selection,
statewide percentile, or causal conclusion has been produced by this repository as of
2026-10-01T21:11:33.275290+00:00. Notebook 12 computed a **scenario-level pilot index** for Bridgeport (explicitly
labeled pilot, with disclosed coverage gaps and six sensitivity variants) and placed it against a
single Greenwich reference point -- this is explicitly not a town-level score or ranking (see
`docs/RESULTS_STATUS.md`).

## Limitations

See `docs/KNOWN_LIMITATIONS.md` for the full, itemized list.
