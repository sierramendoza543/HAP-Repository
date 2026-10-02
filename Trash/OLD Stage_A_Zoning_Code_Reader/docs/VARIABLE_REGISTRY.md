# VARIABLE_REGISTRY.md

Canonical source: `data/processed/canonical_variable_registry.csv`. 12 variables (V1-V12), each with
a predeclared operational definition, accepted legal forms, and explicit prohibited conflations --
written before extraction, not fit to whatever the data happened to contain.

### V1 -- Minimum lot-size threshold

- **Direction:** larger_increases_restrictiveness
- **Accepted legal forms:** minimum_lot_size_sqft; minimum_lot_size_acres; minimum_site_area_sqft; minimum_site_area_per_dwelling_unit; no_minimum_lot_area; existing_lot_of_record_exception
- **Prohibited conflations:** open space; floor area; building footprint; amenity area; site area per unit
- **Score gate:** numeric or explicit no-minimum status with source

### V2 -- Minimum lot-width threshold

- **Direction:** larger_increases_restrictiveness
- **Accepted legal forms:** minimum_lot_width_ft; width_at_building_line_ft; width_at_setback_line_ft; frontage_requirement_ft; no_minimum_width
- **Prohibited conflations:** frontage treated as width without explicit code equivalence
- **Score gate:** numeric or explicit no-minimum status with source

### V3 -- Vertical development capacity

- **Direction:** higher_capacity_lowers_restrictiveness
- **Accepted legal forms:** maximum_building_height_ft; maximum_height_stories; dual stories+feet cap; confirmed absence of cap
- **Prohibited conflations:** stories as feet; ground-story height as total height; roof/parapet/stepback as total height
- **Score gate:** feet cap directly comparable; stories-only cap score-ready-with-caveat via ordinal rubric

### V4 -- Site-intensity / ground-plane control

- **Direction:** legal-form-specific (see rubric)
- **Accepted legal forms:** maximum_lot_coverage_pct; maximum_site_coverage_pct; maximum_impervious_coverage_pct; maximum_far; minimum_open_space_pct; minimum_pervious_area_pct; minimum_green_area_pct
- **Prohibited conflations:** FAR as coverage; open/pervious/green area as coverage
- **Score gate:** legal-form-specific ordinal rubric only; no cross-form conversion

### V5 -- Building-placement control

- **Direction:** larger_setback_increases_restrictiveness
- **Accepted legal forms:** front/side/rear_setback_ft; summed_minimum_setbacks_ft; build_to_minimum_ft; build_to_maximum_ft; frontage_buildout_requirement
- **Prohibited conflations:** parking/accessory setbacks as principal-building setbacks; build-to as setback; non-concurrent sum
- **Score gate:** numeric setback directly comparable; build-to separate placement-flexibility rubric

### V6 -- Vehicle-parking burden

- **Direction:** higher_burden_increases_restrictiveness
- **Accepted legal forms:** spaces_per_dwelling_unit; spaces_per_bedroom; spaces_per_gfa; no_minimum_parking_requirement; qualitative/discretionary rule
- **Prohibited conflations:** bedroom/GFA formulas forced into spaces/unit; ADU no-additional-parking generalized citywide; bicycle parking as vehicle parking
- **Score gate:** numeric or explicit no-minimum status; qualitative rules get categorical rubric

### V7 -- 3+-unit housing entitlement pathway

- **Direction:** more_certain_less_discretionary_lowers_restrictiveness
- **Accepted legal forms:** permitted_by_right; administrative_or_site_plan_review; special_permit_or_special_exception; discretionary_commission_review; rezoning_or_legislative_pathway; prohibited; unavailable_in_analysis_unit; unresolved_pending_master_use_table
- **Prohibited conflations:** two-family permission as multifamily; mixed-use label as proof; density allowance as proof
- **Score gate:** requires confirmed approval-pathway symbol, not just use-category text

### V8 -- ADU entitlement pathway

- **Direction:** more_certain_objective_entitlement_lowers_restrictiveness
- **Accepted legal forms:** allowed_by_right; allowed_subject_to_objective_conditions; conditional_discretionary_approval; effectively_unavailable; prohibited
- **Prohibited conflations:** state default law assumed without local applicability evidence
- **Score gate:** pathway + condition fields source-backed

### V9 -- Residential density / unit-cap control

- **Direction:** higher_capacity_lowers_restrictiveness
- **Accepted legal forms:** maximum_units_per_acre; maximum_units_per_lot; maximum_units_per_building; minimum_land_area_per_dwelling_unit; density_cap; building_type_only_density_control; no_explicit_density_or_unit_cap
- **Prohibited conflations:** unit count inferred from stories, height, FAR, lot size, or GIS observation
- **Score gate:** numeric cap = ordinal rubric; building-type-only control = categorical rubric only if type explicitly constrains unit count

### V10 -- Floor-area capacity

- **Direction:** higher_capacity_lowers_restrictiveness
- **Accepted legal forms:** maximum_far; maximum_floor_area_ratio; maximum_gross_floor_area; maximum_floorplate; no_explicit_floor_area_cap; form_envelope_only
- **Prohibited conflations:** FAR calculated from GIS/height/coverage/stories/plan images
- **Score gate:** direct FAR/GFA cap only; envelope-only controls not converted to FAR

### V11 -- General discretionary-review burden

- **Direction:** more_discretionary_increases_restrictiveness
- **Accepted legal forms:** ministerial_or_zoning_permit_only; administrative_review_with_objective_standards; site_plan_review_objective; site_plan_review_with_discretion; special_permit_or_special_exception; design_review_or_multiple_discretionary_bodies; rezoning_or_legislative_action; prohibited
- **Prohibited conflations:** double-counting the same special permit already scored under V7
- **Score gate:** representative compliant-project pathway identified; shared_underlying_rule flagged against V7 where applicable

### V12 -- Missing-middle housing entitlement (2-4 units)

- **Direction:** broader_more_certain_entitlement_lowers_restrictiveness
- **Accepted legal forms:** broadly_permitted_by_right; permitted_by_right_for_some_missing_middle_forms; administrative_or_site_plan_review; special_permit_or_special_exception; limited_to_specific_form_or_overlay; prohibited; unavailable_in_analysis_unit
- **Prohibited conflations:** townhouse-capable building type assumed missing-middle without unit-count verification
- **Score gate:** explicit form-to-unit-count mapping source-backed

