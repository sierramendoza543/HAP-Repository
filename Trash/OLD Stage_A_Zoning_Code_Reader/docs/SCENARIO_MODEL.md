# SCENARIO_MODEL.md

## The scenario key

`r_{d,b,f,k}`: district (`d`) x building form/type or use (`b`) x site/frontage/condition (`f`) x
variable (`k`). Adopted because Bridgeport's form-based code genuinely varies rules by building type
within a single district (e.g. House A vs. House D in the same N-zone have different unit caps) --
collapsing to district-only would erase real legal variation.

## Scenario universe sizes (independently recomputed this run)

- Phase-2 baseline scenario registry: 46 rows (42 after removing 4 literal duplicate rows).
- Plus the Small General registry addendum (Notebook 11): 2 rows.
- Combined scenario universe used for Phase-3 scoring eligibility: 44.
- Score-eligible scenarios under the Notebook 11 rule: 28.

## Known limitation

Notebook 10's master-use-table and PARKING evidence covers some (district, building_form)
combinations that are *not* in the 44-scenario universe (e.g. House A in zone NX2) -- these were
deliberately left out of scope for the Notebook 11 integration per the user's explicit "narrowly
scoped" instruction, and remain real, recorded evidence (see
`outputs/review/bridgeport/step_03_v7_v12_evidence_out_of_scope_this_pass.csv`) available for a
future registry-completion pass.
