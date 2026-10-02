# Expanded Variable Uncertainty and Coverage Spec (DRAFT -- not executed)

1. `pending_visual_recovery`, `unresolved_scope_or_cross_reference`, and
   `candidate_found_needs_manual_review` rows are excluded from any future score's numerator AND
   denominator for that variable -- they do not count as a permissive or restrictive value.
2. `genuine_absence_after_targeted_search` is a valid policy state (the code truly does not
   regulate this) and may be scored as its own category once a human confirms how it should be
   treated relative to numeric peers -- not defaulted to "most permissive" or "most restrictive."
3. `not_applicable_to_analysis_unit` rows are excluded from that scenario's denominator entirely.
4. Evidence confidence (source_confidence x extraction_confidence) should gate a future score's
   reported uncertainty band, not silently raise or lower the point estimate.
