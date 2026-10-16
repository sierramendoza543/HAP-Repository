# Zoning PDF Pilot — Greenwich & Bridgeport

A small, human-gated pilot to test whether official municipal zoning PDFs can be
collected, searched, and extracted into verified, source-quoted facts for two test
variables:

- **L1** — Minimum Lot Size
- **U2** — Two-Family Permission

for **Greenwich, CT** and **Bridgeport, CT**.

This pilot does not compute a score, subindex, or composite. The deliverable is a small
set of verified district-level facts, each backed by an exact quote and PDF page number.

## Stages

Everything runs in one notebook, [`zoning_pdf_pilot.ipynb`](zoning_pdf_pilot.ipynb), built
as a sequence of checkpoints. Each stage stops with a printed status before the next one
begins — this is not one automated end-to-end run.

0. **Setup and scope** — configuration, guardrail flags, folder/PDF presence checks.
1. **Collect and register PDFs** — hash and catalog manually-uploaded official PDFs.
2. **Create source packets** — find candidate pages/sections for L1 and U2.
3. **LLM triage and extraction** (Gemini) — classify packets, then extract structured,
   quote-backed candidate facts for packets marked relevant.
4. **Human-review spreadsheet** — every candidate fact reviewed against its source PDF.
5. **Pilot summary** — a verified fact table and a process-quality table. No scoring.

## Folder layout

| Folder | Contents |
|---|---|
| `data/raw_pdfs/{greenwich_ct,bridgeport_ct}/` | Manually-uploaded official PDFs (not in git) |
| `data/source_manifest/` | One record per PDF: hash, pages, title, status |
| `data/processed/extracted_text/` | Page-by-page extracted text |
| `data/processed/source_packets/` | Labeled candidate chunks sent toward the LLM stage |
| `data/processed/table_artifacts/` | Extracted table text/CSV, if applicable |
| `schemas/` | Locked JSON contracts for packets, triage, candidates, review records |
| `outputs/` | One subfolder per stage's saved artifact |
| `docs/` | Plain-English draft guidance for the two pilot variables |

Raw PDFs and all outputs are excluded from git; only the folder structure is tracked.

## Status

See the Stage 0 cell output in the notebook for the current computed pilot status
(`WAITING_FOR_DOCUMENT_UPLOAD` until both towns have at least one PDF registered).
