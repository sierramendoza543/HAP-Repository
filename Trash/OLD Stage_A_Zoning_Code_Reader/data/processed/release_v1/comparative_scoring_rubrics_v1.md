# comparative_scoring_rubrics_v1.md

## V1

- Accepted legal forms: minimum_lot_size_sqft; no_minimum
- Direction: larger=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: score 0 (lowest tier)
- Qualitative-rule treatment: n/a
- Excluded legal forms: area-per-unit, open space, building footprint never substituted
- Uncertainty/caveat rule: unresolved excluded from denominator
- Example (Greenwich): RA-4: 174,240 sqft -> 100
- Example (Bridgeport): House C/N3: 9,000 sqft -> 50
- Limitations: Bridgeport confirmed V1 evidence exists for only 2 of 28 eligible scenarios

## V2

- Accepted legal forms: minimum_lot_width_ft; no_minimum
- Direction: larger=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: score 0
- Qualitative-rule treatment: n/a
- Excluded legal forms: frontage scored as width only where source-defined equivalent
- Uncertainty/caveat rule: unresolved excluded
- Example (Greenwich): RA-4: 200 ft -> 90
- Example (Bridgeport): Storefront/DX1: 18 ft -> 10
- Limitations: none material

## V5

- Accepted legal forms: conventional summed setback (front+side+rear); build-to flexibility (side+rear only)
- Direction: larger=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: n/a
- Qualitative-rule treatment: n/a
- Excluded legal forms: parking/accessory-structure setbacks never substituted for principal-building placement (see Notebook 14 fix)
- Uncertainty/caveat rule: structurally_different_placement_form scenarios excluded from V5 unless a frozen alternative rubric exists
- Example (Greenwich): RA-4: 250 ft summed -> 100
- Example (Bridgeport): House C/N3: 85 ft summed -> 70
- Limitations: build-to flexibility tier is a proxy, not a direct legal equivalent of a conventional setback

## V6

- Accepted legal forms: no-minimum; numeric spaces/unit; qualitative/discretionary
- Direction: higher_burden=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: score 0 only where source-supported scope applies
- Qualitative-rule treatment: separate ordinal branch (70)
- Excluded legal forms: bedroom/GFA formulas not forced into spaces/unit
- Uncertainty/caveat rule: formula-based flagged for manual harmonization, excluded if unresolved
- Example (Greenwich): no direct V6 categorical match recorded for RA-4 in this registry pass -- excluded from Greenwich benchmark, see limitations
- Example (Bridgeport): citywide no-minimum (§8.20.1) -> 0
- Limitations: Greenwich V6 not independently scored this pass (see Notebook 13 KNOWN_LIMITATIONS)

## V7

- Accepted legal forms: by-right; administrative; special permit; discretionary; legislative; prohibited/unavailable
- Direction: more_discretionary_or_prohibited=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: n/a
- Qualitative-rule treatment: n/a
- Excluded legal forms: two-family never counted as 3+-unit multifamily
- Uncertainty/caveat rule: not_applicable excluded from the housing-entitlement domain entirely for that scenario, never scored 0 or 100
- Example (Greenwich): RA-4: prohibited -> 100
- Example (Bridgeport): Storefront/DX1: allowed by right -> 0
- Limitations: 25 of 28 eligible Bridgeport scenarios are allowed-by-right; 3 gated out as not_applicable

## V8

- Accepted legal forms: by-right; objective conditions; discretionary; effectively unavailable; prohibited
- Direction: more_discretionary_or_unavailable=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: n/a
- Qualitative-rule treatment: n/a
- Excluded legal forms: state-default rules not scored without local applicability evidence
- Uncertainty/caveat rule: unresolved excluded
- Example (Greenwich): RA-4: allowed subject to objective conditions -> 30
- Example (Bridgeport): citywide §4.70.2: allowed subject to objective conditions -> 30
- Limitations: identical categorical value both towns this pass

## V9

- Accepted legal forms: numeric units/acre or units/lot or units/building; building-type-only control; 1-unit-per-lot
- Direction: higher_capacity=less_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: no_cap scores 0
- Qualitative-rule treatment: building-type-only control scored at a fixed caveated midpoint (50)
- Excluded legal forms: density never inferred from lot size/height/GIS
- Uncertainty/caveat rule: caveated -- run with and without in sensitivity (variant 6)
- Example (Greenwich): RA-4 §6-93: 1 unit/lot detached SF -> 100
- Example (Bridgeport): citywide building-type-only control -> 50 (caveated)
- Limitations: V9 is Notebook 09's score_ready_with_caveat variable; caveat carried through explicitly

## V11

- Accepted legal forms: ministerial; administrative objective; site plan objective; site plan discretionary; special permit; design review; rezoning; prohibited
- Direction: more_discretionary=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: n/a
- Qualitative-rule treatment: n/a
- Excluded legal forms: not double-counted with V7's identical citation unless shared_underlying_rule=true (see dependency section)
- Uncertainty/caveat rule: unresolved excluded
- Example (Greenwich): RA-4 §6-93: ministerial only -> 0 (same citation as V7 -- shared_underlying_rule=true)
- Example (Bridgeport): citywide administrative review with objective standards -> 20
- Limitations: Greenwich V7/V11 share a citation; Bridgeport's do not (see B5)

## V12

- Accepted legal forms: broadly by-right; by-right for some forms; administrative; special permit; overlay-limited; prohibited/unavailable
- Direction: narrower_or_prohibited=more_restrictive
- Score range: 0-100
- No-minimum/no-cap treatment: n/a
- Qualitative-rule treatment: n/a
- Excluded legal forms: building form never assumed missing-middle without unit-count verification
- Uncertainty/caveat rule: not_applicable excluded, never defaulted
- Example (Greenwich): RA-4 §6-93: prohibited -> 100
- Example (Bridgeport): 27 of 50 scenarios entitlement present -> 0; 23 absent -> 100
- Limitations: mirrors V7's dependency relationship, see dependency map
