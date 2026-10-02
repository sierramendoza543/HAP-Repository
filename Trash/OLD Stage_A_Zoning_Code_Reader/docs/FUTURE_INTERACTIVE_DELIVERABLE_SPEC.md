# FUTURE_INTERACTIVE_DELIVERABLE_SPEC.md

This document specifies what a future interactive tool should do -- it does not build one.

## Target audiences

Planning staff, housing researchers, legal reviewers, and engaged residents comparing zoning rules
across towns and building types.

## User questions the tool must answer

- "What does the zoning code actually say for [this district, this building type]?"
- "What's the source for this value -- can I see the actual page?"
- "Is this value confirmed, pending, or a documented absence?"
- "How does this compare to a similar scenario in the other town, and with what caveats?"

## Required views

1. Scenario browser (district x building-form grid, Notebook 09's `r_{d,b,f,k}` model).
2. Evidence-card detail view per cell (source page image, excerpt, status, reviewer info).
3. Variable registry reference (V1-V12 definitions, accepted forms, prohibited conflations).
4. Coverage/readiness dashboard (what's confirmed vs. pending vs. genuinely absent).
5. A pilot-index view, clearly labeled provisional, with coverage disclosure visible per scenario --
   never a single headline town score.

## Nonnegotiable caveats to carry into the interface

- Every value must link to its source page/table and status.
- `not_applicable` must render distinctly from a numeric 0 -- never visually implying "least
  restrictive."
- Structurally non-equivalent values (e.g. build-to vs. setback) must never appear on the same
  numeric axis without a visible form label.
- No single headline "Bridgeport score" or "Greenwich score" -- only scenario-level, coverage-labeled
  values.

## Evidence-card behavior

Each card must show: town, district/scenario, variable, source document/page/section, source
excerpt, status, comparability status, review status, and a limitation note where relevant. See
`PROVENANCE_STANDARD.md` for the minimum field set per source type.

## Data-update workflow

New notebooks append additive evidence files; the interactive tool's data layer should read from the
canonical matrices listed in `ARTIFACT_MAP.md`, never from a notebook's intermediate state.

## What must never be simplified

- The distinction between `pending_visual_recovery`, `genuine_absence_after_targeted_search`, and
  `structurally_non_equivalent_rule_present` -- these are legally different claims and must never be
  collapsed into one "no data" icon.

## What score/readiness information can and cannot be shown

Can show: per-scenario, per-variable confirmed values and their coverage/readiness status. Cannot
show: a computed composite town score as a headline number, a ranking, or a "more/less restrictive
town" badge, until a validated (not pilot) scoring methodology is formally adopted.

## Accessibility requirements

Standard WCAG 2.1 AA baseline; source-document page images need text alternatives (the underlying
transcribed value + excerpt already serve this purpose and should be surfaced, not just the image).

## Static-to-interactive asset mapping

- `outputs/figures/finalization/*.png` -> dashboard summary tiles.
- `data/processed/*.csv` canonical matrices -> the interactive data layer's source tables.
- A full evidence-card image library (see `KNOWN_LIMITATIONS.md`) is the main asset still to be
  produced before the evidence-card detail view (item 2 above) can be built.
