# MANUAL_REVIEW_PROTOCOL.md

## Reviewer decision fields

`reviewer_decision`, `review_status`, `reviewer_name_or_id`, `review_date`, `reviewer_note` --
present in `bridgeport_phase_2_6_visual_table_manual_verification.csv` for every Phase 2.5/2.6
manually verified cell.

## Promotion rule

A visual-table candidate reaches `confirmed`/`manual_verified_visual_table` status only via direct
human verification against the rendered source page. A VLM candidate alone is never sufficient
(Notebook 06's explicit, upheld policy -- the VLM pipeline was built but never exercised against a
live model in this project; see `REPRODUCIBILITY.md`).

## Review-status controlled vocabulary

`not_reviewed`, `automated_candidate`, `visually_inspected`, `manually_verified`,
`rejected_by_review`, `needs_legal_review`, `unresolved` (see `STATUS_TAXONOMY.md`).
