# Pilot Scope — Greenwich & Bridgeport Zoning PDF Pilot

```
Status: Draft v0.1 pilot guidance.
Purpose: This document guides the Greenwich–Bridgeport PDF pilot only.
It is not final scoring guidance and will be revised after reviewing
actual source documents, tables, footnotes, and edge cases.
```

## Pilot towns

- Greenwich, CT
- Bridgeport, CT

## Pilot variables

- **L1** — Minimum Lot Size
- **U2** — Two-Family Permission

## Rules

These rules govern the entire pilot, across all stages:

- **No score calculation.**
- **No subindex.**
- **No composite.**
- **No guessing.** If the source text doesn't say it, the field stays `null` /
  `not_available` / `unresolved` — never filled in by inference.
- **Every extracted answer must have source evidence**: an exact quote, a document
  reference (filename + hash), and a page number.
- **Every extracted record remains `pending_review`** until a human reviewer sets its
  `final_status` to `verified`. No record is usable downstream before that.

## What counts as success

A verified fact must be traceable, in under a few minutes, by a human opening the cited
PDF to the cited page and finding the cited quote. If that round-trip isn't fast and
obvious, the packet/extraction design needs improvement before the record is trusted —
not the other way around.

The pilot does not need a high acceptance rate to be a success. A pilot that catches its
own mistakes (rejects bad candidates, flags unresolved cases, requires human correction on
some records) is doing its job. The failure mode this pilot is designed to prevent is an
unsupported AI claim quietly becoming a "final" fact.

## Open items

- District list for Greenwich and Bridgeport: to be supplied before Stage 2/3.
- LLM provider for triage/extraction: Gemini.
- Table extraction approach: `pdfplumber`.
