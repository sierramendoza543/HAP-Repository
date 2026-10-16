# L1 — Minimum Lot Size: Draft Decision Tree

```
Status: Draft v0.1 pilot guidance.
Purpose: This document guides the Greenwich–Bridgeport PDF pilot only.
It is not final scoring guidance and will be revised after reviewing
actual source documents, tables, footnotes, and edge cases.
```

This is the initial working logic for routing and extracting L1 (minimum lot size)
candidates in Stages 2–3. It is expected to change once we see how Greenwich's and
Bridgeport's actual dimensional tables and footnotes are laid out.

## Changelog

- **v0.1 (initial draft):** single shared search-term list for both towns.
- **v0.1, revised after Stage 0/1 discovery:** Greenwich's code uses traditional
  dimensional-schedule language, confirmed present in Stage 0's content check
  ("minimum lot size" appears on 11 pages). Bridgeport's code (registered in Stage 1,
  304 pages, effective Jan 1 2022) is a **form-based code** — it regulates by building
  type rather than a single town-wide dimensional table, and literal lot-size phrasing
  is comparatively rare. Search terms are now **per-municipality** rather than shared;
  see below. This is a vocabulary-discovery revision, not a change to what L1 means.

## Stage 2 — what makes a page a candidate packet

A page becomes an L1 source packet if it contains one of the search terms for that
municipality:

**Default (used by Greenwich and any town without its own list):**
```
minimum lot size
minimum lot area
minimum site area
minimum zoning lot area
lot area per dwelling unit
dimensional standards
bulk regulations
schedule of required open spaces
```

**Bridgeport-specific** (form-based code vocabulary — dimensional standards are
embedded per building type, e.g. "Lot Width"/"Site Coverage" tables under each building
type section, rather than one town-wide schedule):
```
minimum lot size
minimum lot area
lot width
site coverage
building type
dimensional
```

A packet is just labeled raw material at this point — not yet a classification of
relevance.

## Stage 3a — triage categories (draft)

| Category | Meaning |
|---|---|
| `LIKELY_L1_GOVERNING_RULE` | Looks like it states an actual lot-size standard |
| `DIMENSIONAL_TABLE_OR_SCHEDULE` | A table/schedule with lot size as one column among dimensional standards |
| `DEFINITION_ONLY` | Defines "lot," "lot area," etc. without stating a required minimum |
| `FEE_OR_PROCEDURAL_TEXT` | Mentions lot size only in a fee/application/procedural context |
| `CROSS_REFERENCE_ONLY` | Points to "the building zone regulations" or similar without stating a value |
| `IRRELEVANT` | Term match was coincidental (e.g. "parking lot") |
| `UNRESOLVED` | Model cannot confidently classify |

Packets marked `LIKELY_L1_GOVERNING_RULE` or `DIMENSIONAL_TABLE_OR_SCHEDULE` move to
extraction. Everything else is rejected with a one-line reason, logged, not deleted.

## Stage 3b — extraction fields (draft)

```
district code
district name, if stated
raw lot-size value
unit
condition
exact quote
page number
table title
row label
column label
footnote
uncertainty
```

Any field not directly supported by the quoted text is `null`. A value is never inferred
from a related district, a default assumption, or a prior pilot result.

## Known open questions (to resolve after seeing real PDFs)

- How to handle a schedule where lot size varies by use (single-family vs. multifamily)
  within the same district — one record per combination, or a condition field?
- How to represent a lot size expressed as "X acres" vs. "X square feet" consistently.
- How footnotes that modify a table cell (e.g. corner-lot exceptions) should be captured.
