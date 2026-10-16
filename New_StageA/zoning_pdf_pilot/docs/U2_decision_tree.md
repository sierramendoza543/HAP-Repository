# U2 — Two-Family Permission: Draft Decision Tree

```
Status: Draft v0.1 pilot guidance.
Purpose: This document guides the Greenwich–Bridgeport PDF pilot only.
It is not final scoring guidance and will be revised after reviewing
actual source documents, tables, footnotes, and edge cases.
```

This is the initial working logic for routing and extracting U2 (two-family permission)
candidates in Stages 2–3. It is expected to change once we see how Greenwich's and
Bridgeport's actual use tables and footnotes are laid out.

## Changelog

- **v0.1 (initial draft):** single shared search-term list for both towns.
- **v0.1, revised after Stage 0/1 discovery:** Bridgeport's registered zoning code
  (304 pages, effective Jan 1 2022) returned **zero** hits anywhere for "two-family,"
  "duplex," or "multi-family" — confirmed by a full-document scan, not a sampling
  assumption. It is a form-based code that permits two-unit housing through a
  **building type** category, "Double House A Building Type" (section 3.80), with its
  own per-zone table (allowed zones, unit counts, dimensional standards). Search terms
  are now **per-municipality**; see below. The reported variable stays `U2 — Two-Family
  Permission` — only the discovery vocabulary changed, not what the pilot is measuring.
  This is exactly the kind of legally-equivalent-local-language gap this draft status
  exists to catch before it reaches extraction.

## Stage 2 — what makes a page a candidate packet

A page becomes a U2 source packet if it contains one of the search terms for that
municipality:

**Default (used by Greenwich and any town without its own list):**
```
two-family
two family
two-family dwelling
duplex
permitted uses
use regulations
special permit
special exception
```

**Bridgeport-specific** (form-based code vocabulary — two-unit housing is reached via
building-type and household-living language, not "two-family"/"duplex"):
```
two-family
two family
duplex
double house
building type
household living
principal units
attached house
detached house
neighborhood zone
form-based
```

A packet is just labeled raw material at this point — not yet a classification of
relevance. Finding a Bridgeport packet via "double house" or "principal units" does
not by itself establish that it's legally equivalent to "two-family permission" — that
equivalence judgment belongs in Stage 3 triage/extraction and ultimately human review,
not in this term list.

## Stage 3a — triage categories (draft)

| Category | Meaning |
|---|---|
| `LIKELY_U2_GOVERNING_RULE` | Looks like it states whether two-family use is permitted |
| `USE_TABLE_OR_PERMISSION_RULE` | A use table with two-family as one row/column by district |
| `DEFINITION_ONLY` | Defines "two-family dwelling" or "duplex" without stating permission |
| `FEE_OR_PROCEDURAL_TEXT` | Mentions two-family only in a fee/application/procedural context |
| `CROSS_REFERENCE_ONLY` | Points elsewhere without stating a permission status |
| `IRRELEVANT` | Term match was coincidental |
| `UNRESOLVED` | Model cannot confidently classify |

Packets marked `LIKELY_U2_GOVERNING_RULE` or `USE_TABLE_OR_PERMISSION_RULE` move to
extraction. Everything else is rejected with a one-line reason, logged, not deleted.

## Stage 3b — extraction fields (draft)

```
district code
district name, if stated
permission status
approval pathway
condition
exact quote
page number
table title
row label
column label
footnote
uncertainty
```

`permission status` is restricted to what the source text actually states (e.g.
by-right / special permit / special exception / prohibited) — never inferred from a
related use, a definition alone, or "one-family plus accessory dwelling unit" language,
which is explicitly **not** the same as two-family permission.

## Known open questions (to resolve after seeing real PDFs)

- How to represent a district where two-family is permitted only under a specific
  condition (e.g. lot size threshold, owner-occupancy) — condition field vs. separate
  record.
- How to handle a town-wide ADU allowance that is distinct from two-family use, so the
  two are never conflated in extraction.
- How footnotes that narrow a use-table cell should be captured alongside the quote.
