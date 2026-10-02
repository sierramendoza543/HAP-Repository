# Expanded Variable Scenario Aggregation Spec (DRAFT -- not executed)

This document specifies, but does not execute, how a future Phase 3 engine would aggregate
scenario-level V1-V12 results into a district-level and town-level construct score. No
aggregation is performed in this notebook.

1. Each analysis unit (district x building-form/scenario) contributes one value per score-ready
   variable to that district's distribution for that variable.
2. A district-level value is NOT a single number picked arbitrarily -- the spec requires either
   (a) reporting the full distribution (e.g. min/median/max across building types), or
   (b) a predeclared, documented selection rule (e.g. "the most permissive by-right pathway
   available in the district") decided by a human before any scoring run, never inferred here.
3. Variables flagged `shared_underlying_rule` in the dependency map must not both contribute full
   weight to the same domain without an explicit, predeclared dependency-adjustment rule.
4. Town-level aggregation across districts is explicitly out of scope until a dominant-district
   or distributional approach is chosen by the user -- this project has repeatedly declined to
   silently select a dominant district.
