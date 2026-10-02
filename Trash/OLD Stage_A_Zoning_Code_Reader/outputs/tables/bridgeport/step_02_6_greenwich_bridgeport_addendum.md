# Phase 2.6 Addendum -- Exploratory Greenwich-Bridgeport Evidence Comparison (Height)

> **Important:** This is an addendum to the existing exploratory comparison, not a replacement. It reports what Phase 2.6's targeted visual table recovery changed about Bridgeport's height evidence specifically. It is not a statewide ranking, validated cross-town composite score, causal estimate, or legal conclusion.

## What changed

Bridgeport now has 13/13 building-type `maximum_height_stories` values confirmed via direct human visual-table recovery (previously 0 confirmed -- Phase 2's regex found no clean match, and the earlier Phase 2.5 conclusion was that height is diagram-only). Ground-story and upper-story height **in feet** are also now confirmed as separate, supplemental variables.

## Why this still does not create a Greenwich comparison for height

- Greenwich RA-4's `maximum_building_height_ft` is: missing (3.5 stories only, no stories-to-feet conversion found in the Greenwich code)
- Bridgeport's newly-recovered values are in **stories**, not feet, and ground/upper-story feet ranges are sub-components, not total building height.
- Per explicit project policy, stories are never silently converted to feet, and a ground/upper-story standard is never silently treated as total building height.
- **Result: height remains `structurally_non_equivalent` for Greenwich comparison purposes, even though Bridgeport's own evidence completeness for this variable improved dramatically** (0 -> 13 confirmed district-level story-count values).

## Table

| Variable | Greenwich (RA-4) | Bridgeport (Phase 2.6) | Comparability |
|---|---|---|---|
| maximum_height_stories | 3.5 stories (from the dimensional schedule) | 13 building types, see step_02_6_recovered_dimensional_standards.csv | structurally_non_equivalent |
| maximum_building_height_ft | missing | missing (not expressed in feet anywhere found) | missing |
| ground/upper story height ft | not separately tracked for Greenwich | 12 building types with ft ranges recovered | needs_manual_harmonization |