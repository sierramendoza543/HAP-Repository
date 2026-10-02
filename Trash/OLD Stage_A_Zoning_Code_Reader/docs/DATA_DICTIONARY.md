# DATA_DICTIONARY.md

Auto-generated from live column introspection of the canonical matrices (first 200 rows sampled for null/example stats; full files are the source of truth).

### `fixed_variable_recovery_matrix_bridgeport_greenwich.csv`

| Column | dtype | Nulls (sample) | Example value |
|---|---|---|---|
| `town` | str | 0/200 null (first 200 rows) | `Bridgeport` |
| `analysis_unit_id` | str | 0/200 null (first 200 rows) | `DX1__Storefront` |
| `district_code` | str | 0/200 null (first 200 rows) | `DX1` |
| `district_name` | float64 | 200/200 null (first 200 rows) | `None` |
| `building_form_or_type` | str | 0/200 null (first 200 rows) | `Storefront` |
| `scenario_id` | float64 | 200/200 null (first 200 rows) | `None` |
| `variable_id` | str | 0/200 null (first 200 rows) | `V2` |
| `subvariable` | str | 0/200 null (first 200 rows) | `minimum_lot_width_ft` |
| `final_determination` | str | 0/200 null (first 200 rows) | `confirmed` |
| `raw_value` | float64 | 37/200 null (first 200 rows) | `18.0` |
| `raw_unit` | str | 37/200 null (first 200 rows) | `ft` |
| `normalized_value` | float64 | 63/200 null (first 200 rows) | `18.0` |
| `normalized_unit` | str | 63/200 null (first 200 rows) | `ft` |
| `categorical_value` | str | 189/200 null (first 200 rows) | `no_minimum_lot_width_stated` |
| `formula` | float64 | 200/200 null (first 200 rows) | `None` |
| `condition_text` | str | 179/200 null (first 200 rows) | `max=5.0` |
| `source_type` | str | 0/200 null (first 200 rows) | `manual_verified_visual_table` |
| `source_document` | str | 0/200 null (first 200 rows) | `bridgeport_zoning_code_full_2022-01.pdf.pdf` |
| `document_hash` | float64 | 200/200 null (first 200 rows) | `None` |
| `source_page` | int64 | 0/200 null (first 200 rows) | `20` |
| `printed_page` | int64 | 0/200 null (first 200 rows) | `20` |
| `section_or_node_path` | str | 0/200 null (first 200 rows) | `X.X0.4 BUILDING SITING -- Storefront` |
| `table_or_figure_id` | float64 | 200/200 null (first 200 rows) | `None` |
| `table_title` | str | 0/200 null (first 200 rows) | `Figure: Storefront Building Siting` |
| `row_label` | str | 0/200 null (first 200 rows) | `Lot Width` |
| `column_label` | float64 | 200/200 null (first 200 rows) | `None` |
| `source_excerpt` | float64 | 200/200 null (first 200 rows) | `None` |
| `extraction_method` | str | 0/200 null (first 200 rows) | `targeted_visual_table_recovery` |
| `source_confidence` | float64 | 0/200 null (first 200 rows) | `0.9` |
| `extraction_confidence` | float64 | 0/200 null (first 200 rows) | `0.9` |
| `reviewer_decision` | str | 0/200 null (first 200 rows) | `verified_governing_value` |
| `review_status` | str | 0/200 null (first 200 rows) | `reviewed` |
| `comparability_status` | str | 0/200 null (first 200 rows) | `directly_comparable` |
| `rationale` | str | 0/200 null (first 200 rows) | `directly transcribed from BUILDING SITING table` |
| `missingness_diagnosis` | str | 0/200 null (first 200 rows) | `confirmed_governing_rule` |
| `cross_reference_trail` | str | 167/200 null (first 200 rows) | `see 14.20.7 for measuring site coverage` |
| `date_version` | str | 0/200 null (first 200 rows) | `2026-10-01` |

### `expanded_variable_recovery_matrix_bridgeport_greenwich.csv`

| Column | dtype | Nulls (sample) | Example value |
|---|---|---|---|
| `town` | str | 0/200 null (first 200 rows) | `Bridgeport` |
| `analysis_unit_id` | str | 0/200 null (first 200 rows) | `DX1__Storefront` |
| `district_code` | str | 0/200 null (first 200 rows) | `DX1` |
| `district_name` | float64 | 200/200 null (first 200 rows) | `None` |
| `variable_id` | str | 0/200 null (first 200 rows) | `V2` |
| `framework_label` | str | 0/200 null (first 200 rows) | `Minimum lot-width threshold` |
| `final_determination` | str | 0/200 null (first 200 rows) | `confirmed` |
| `categorical_value` | str | 189/200 null (first 200 rows) | `no_minimum_lot_width_stated` |
| `raw_value` | float64 | 37/200 null (first 200 rows) | `18.0` |
| `normalized_value` | float64 | 63/200 null (first 200 rows) | `18.0` |
| `source_page` | float64 | 0/200 null (first 200 rows) | `20.0` |
| `section_or_node_path` | str | 0/200 null (first 200 rows) | `X.X0.4 BUILDING SITING -- Storefront` |
| `source_excerpt` | float64 | 200/200 null (first 200 rows) | `None` |
| `rationale` | str | 0/200 null (first 200 rows) | `directly transcribed from BUILDING SITING table` |
| `extraction_method` | str | 0/200 null (first 200 rows) | `targeted_visual_table_recovery` |
| `source_confidence` | float64 | 0/200 null (first 200 rows) | `0.9` |
| `extraction_confidence` | float64 | 0/200 null (first 200 rows) | `0.9` |
| `missingness_diagnosis` | str | 0/200 null (first 200 rows) | `confirmed_governing_rule` |
| `comparability_status` | str | 0/200 null (first 200 rows) | `directly_comparable` |
| `cross_reference_trail` | str | 167/200 null (first 200 rows) | `see 14.20.7 for measuring site coverage` |
| `date_version` | str | 0/200 null (first 200 rows) | `2026-10-01` |
| `score_readiness` | str | 0/200 null (first 200 rows) | `score_ready` |
| `score_eligibility_rationale` | str | 0/200 null (first 200 rows) | `confirmed with a direct or documented-transform comparability status` |

### `bridgeport_v7_v12_master_use_table_addendum.csv`

| Column | dtype | Nulls (sample) | Example value |
|---|---|---|---|
| `town` | str | 0/100 null (first 200 rows) | `Bridgeport` |
| `district_code` | str | 0/100 null (first 200 rows) | `DX1` |
| `building_form_or_type` | str | 0/100 null (first 200 rows) | `Storefront` |
| `scenario_registry_status` | str | 0/100 null (first 200 rows) | `in_phase2_registry` |
| `variable_id` | str | 0/100 null (first 200 rows) | `V7` |
| `final_determination` | str | 0/100 null (first 200 rows) | `confirmed_allowed_by_right` |
| `raw_value` | str | 0/100 null (first 200 rows) | `No limits` |
| `source_type` | str | 0/100 null (first 200 rows) | `manual_verified_visual_table` |
| `source_document` | str | 0/100 null (first 200 rows) | `bridgeport_zoning_code_full_2022-01.pdf.pdf` |
| `source_page` | int64 | 0/100 null (first 200 rows) | `24` |
| `section_or_node_path` | str | 0/100 null (first 200 rows) | `3.20.9` |
| `table_or_figure_id` | str | 0/100 null (first 200 rows) | `3.20.9.ALLOWED_USES` |
| `row_label` | str | 0/100 null (first 200 rows) | `Number of Principal Units` |
| `column_label` | str | 0/100 null (first 200 rows) | `DX1` |
| `source_excerpt` | str | 0/100 null (first 200 rows) | `Number of Principal Units: No limits; Household Living: allowed_upper_stories_only` |
| `extraction_method` | str | 0/100 null (first 200 rows) | `manual_direct_page_render_and_human_transcription` |
| `source_confidence` | str | 0/100 null (first 200 rows) | `high_direct_human_verification` |
| `rationale` | str | 0/100 null (first 200 rows) | `principal_units_no_limits_stated` |
| `missingness_diagnosis` | str | 0/100 null (first 200 rows) | `confirmed_allowed_by_right` |
| `comparability_status` | str | 0/100 null (first 200 rows) | `directly_comparable` |
| `shared_table_cell` | bool | 0/100 null (first 200 rows) | `True` |
| `date_version` | str | 0/100 null (first 200 rows) | `2026-10-01T20:28:15.079390+00:00` |

### `bridgeport_scenario_score_eligibility_universe.csv`

| Column | dtype | Nulls (sample) | Example value |
|---|---|---|---|
| `district_code` | str | 0/44 null (first 200 rows) | `CX` |
| `building_form_or_type` | str | 0/44 null (first 200 rows) | `general` |
| `scenario_id` | str | 0/44 null (first 200 rows) | `bridgeport-scenario-0001` |
| `V1` | str | 0/44 null (first 200 rows) | `no_evidence_recorded_for_this_scenario` |
| `V2` | str | 0/44 null (first 200 rows) | `no_evidence_recorded_for_this_scenario` |
| `V5` | str | 0/44 null (first 200 rows) | `no_evidence_recorded_for_this_scenario` |
| `V6` | str | 0/44 null (first 200 rows) | `confirmed_qualitative_rule` |
| `V7` | str | 0/44 null (first 200 rows) | `no_evidence_recorded_for_this_scenario` |
| `V8` | str | 0/44 null (first 200 rows) | `confirmed` |
| `V9` | str | 0/44 null (first 200 rows) | `confirmed_qualitative_rule` |
| `V11` | str | 0/44 null (first 200 rows) | `confirmed_qualitative_rule` |
| `V12` | str | 0/44 null (first 200 rows) | `no_evidence_recorded_for_this_scenario` |
| `V1_resolved` | bool | 0/44 null (first 200 rows) | `False` |
| `V2_resolved` | bool | 0/44 null (first 200 rows) | `False` |
| `V5_resolved` | bool | 0/44 null (first 200 rows) | `False` |
| `V6_resolved` | bool | 0/44 null (first 200 rows) | `True` |
| `V7_resolved` | bool | 0/44 null (first 200 rows) | `False` |
| `V8_resolved` | bool | 0/44 null (first 200 rows) | `True` |
| `V9_resolved` | bool | 0/44 null (first 200 rows) | `True` |
| `V11_resolved` | bool | 0/44 null (first 200 rows) | `True` |
| `V12_resolved` | bool | 0/44 null (first 200 rows) | `False` |
| `resolved_count` | int64 | 0/44 null (first 200 rows) | `4` |
| `score_eligible` | bool | 0/44 null (first 200 rows) | `False` |
| `eligibility_rationale` | str | 0/44 null (first 200 rows) | `V7 and/or V12 not resolved for this scenario: missing ['V7', 'V12']` |

### `bridgeport_pilot_scenario_index_all_variants.csv`

| Column | dtype | Nulls (sample) | Example value |
|---|---|---|---|
| `district_code` | str | 0/28 null (first 200 rows) | `DX1` |
| `building_form_or_type` | str | 0/28 null (first 200 rows) | `Storefront` |
| `scenario_id` | str | 0/28 null (first 200 rows) | `bridgeport-scenario-0008` |
| `land` | float64 | 26/28 null (first 200 rows) | `0.7794117647058824` |
| `placement` | float64 | 0/28 null (first 200 rows) | `0.1923076923076923` |
| `parking` | float64 | 0/28 null (first 200 rows) | `0.0` |
| `housing_entitlement` | float64 | 3/28 null (first 200 rows) | `0.05` |
| `density` | float64 | 0/28 null (first 200 rows) | `0.5` |
| `procedural` | float64 | 0/28 null (first 200 rows) | `0.1428571428571428` |
| `R_s_baseline` | float64 | 0/28 null (first 200 rows) | `0.1471840659340659` |
| `coverage_fraction_baseline` | float64 | 0/28 null (first 200 rows) | `0.8` |
| `domains_used_baseline` | str | 0/28 null (first 200 rows) | `['density', 'housing_entitlement', 'parking', 'placement', 'procedural']` |
| `R_s_housing_entitlement_emphasized` | float64 | 0/28 null (first 200 rows) | `0.1225921137685843` |
| `coverage_fraction_housing_entitlement_emphasized` | float64 | 0/28 null (first 200 rows) | `0.85` |
| `R_s_land_emphasized` | float64 | 0/28 null (first 200 rows) | `0.1645815722738799` |
| `coverage_fraction_land_emphasized` | float64 | 0/28 null (first 200 rows) | `0.65` |
| `R_s_procedural_emphasized` | float64 | 0/28 null (first 200 rows) | `0.1549450549450549` |
| `coverage_fraction_procedural_emphasized` | float64 | 0/28 null (first 200 rows) | `0.85` |
| `R_s_v7_v12_equal_split` | float64 | 0/28 null (first 200 rows) | `0.1284340659340659` |
| `coverage_fraction_v7_v12_equal_split` | float64 | 0/28 null (first 200 rows) | `0.8` |
| `R_s_strict_full_coverage_only` | float64 | 26/28 null (first 200 rows) | `0.5701680672268907` |