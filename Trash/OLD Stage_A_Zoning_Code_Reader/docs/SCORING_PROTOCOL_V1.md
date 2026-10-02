# SCORING_PROTOCOL_V1.md

## Unit of analysis
scenario = <town, district, building_form/use, site/frontage condition>

## Domains and weights (declared before scoring; theory-driven, not empirically fit)
- Land threshold & density (25%): L_s = 0.30*V1 + 0.25*V2 + 0.45*V9
- Building placement (15%): B_s = V5
- Vehicle-parking burden (10%): P_s = V6
- Housing-form entitlement (35%): H_s = 0.45*V7 + 0.25*V8 + 0.30*V12
- General discretionary-review burden (15%): D_s = V11
- R_s = 0.25*L + 0.15*B + 0.10*P + 0.35*H + 0.15*D, renormalized over available domains

## Dependency policy
V7<->V11 shared-citation check computed per scenario from actual source_page/section match (not assumed);
V11's weight is halved only where the match is real. V9 is a caveated variable; sensitivity variant 6
reports the conservative exclusion.

## Eligibility gate
A scenario/variable enters the frozen score input only if source-linked, scenario-valid, not
pending/unresolved, and not structurally non-equivalent without a frozen alternative rubric. 16 of 44
Bridgeport candidate scenarios were excluded from v1.0 with a disclosed reason each.

## Six required sensitivity variants
1 baseline, 2 equal-weight, 3 land/density-heavy, 4 housing-entitlement-heavy, 5 process-heavy
dependency-adjusted, 6 conservative (excludes caveated V9 and build-to V5 records).
