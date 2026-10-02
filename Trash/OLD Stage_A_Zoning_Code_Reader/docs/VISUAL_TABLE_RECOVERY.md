# VISUAL_TABLE_RECOVERY.md

## Four recovered table families (Bridgeport)

| Family | Pages (detected) | Pages/types recovered | Notebook |
|---|---|---|---|
| HEIGHT | 13 | 13 | 07 |
| BUILDING SITING | 13 | 13 | 08 |
| PARKING & ACCESSORY STRUCTURES | 13 | 13 | 07 (2) + 10 (11) |
| ALLOWED USES / master-use-table | 13 | 13 | 10 |

All figures above are independently recomputed in Section F of Notebook 13 against the underlying
files, not copied from prior notebooks' printed summaries.

## Method

1. Document-wide hierarchy search locates every page in a 13-page-per-building-type family.
2. Each page is rendered at 200-400 DPI via PyMuPDF.
3. A human reviewer directly reads the rendered page and transcribes values with full page/table/
   row/column provenance -- never OCR, never a VLM output alone.
4. Three pages (House C PARKING, House D PARKING, Workshop PARKING) were found to use a
   structurally different setback rule form (no fixed behind-facade distance) and were recorded as
   such (`rule_form` field), never fabricated as a number -- independently reverified in Section E.

## Known residual gap

A difficult page-94 (House C HEIGHT) ambiguity was flagged during Phase 2.5/2.6; this notebook did
not independently re-verify that specific cell against the source page (out of scope for this audit
pass) -- flagged here rather than silently assumed resolved.
