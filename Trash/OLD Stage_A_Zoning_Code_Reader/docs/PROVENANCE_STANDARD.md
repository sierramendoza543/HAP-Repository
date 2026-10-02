# PROVENANCE_STANDARD.md

Minimum evidence requirements by source type, as actually enforced across Notebooks 04-12:

| Source type | Minimum required fields |
|---|---|
| `original_source_text` | source_document, source_page, source_excerpt |
| `verified_structured_table` | source_document, source_page, table_or_figure_id, row_label, column_label |
| `manual_verified_visual_table` | source_document, source_page, table_or_figure_id, row_label, column_label, reviewer decision/date (where a manual-verification record exists) |
| `manual_verified_diagram` | source_document, source_page, crop/figure reference |
| `vlm_diagram_candidate` | all of the above plus explicit non-confirmed status -- never alone sufficient to reach `confirmed` |
| `derived_classification` (e.g. a broadcast citywide rule) | source_document, source_page of the originating general rule, explicit note that the value is broadcast rather than scenario-specific |

Section D of Notebook 13 independently measured actual completeness against this standard for the
canonical matrices -- see `provenance_completeness_audit.csv` for the real, computed percentages
(not asserted compliance).
