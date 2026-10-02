# Scenario-Aware Comparative Residential Regulation Index — V1.0 Pilot

A local, static, offline interactive explorer for the Greenwich/Bridgeport V1.0 pilot comparative
regulation index.

> **Important:** This is a source-linked, scenario-aware pilot comparison of selected residential
> regulatory constructs. It does not constitute a complete townwide zoning-restrictiveness ranking,
> statewide ranking, causal estimate of housing production, legal opinion, or conclusion that one
> municipality is universally more or less restrictive than the other.

## Launch (one command, no install)

From this directory:

```bash
python3 -m http.server 8787
```

Then open **http://localhost:8787/** in any browser.

(A plain `open index.html` will not work — browsers block `fetch()` of local JSON files opened via
`file://`. The one-line local server above has no external dependencies; it ships with Python 3.)

## What's here

- `index.html` / `app.js` — the app itself. Vanilla HTML/CSS/JS, no build step, no npm, no external
  CDN or API calls, no secrets. Charts are drawn with inline SVG.
- `data/data.json` — a frozen, reconciled export of the real `release_v1` scoring outputs (Notebooks
  14–15). The app never recomputes a score; it only displays what was already computed and validated.
- `downloads/` — literal copies of the canonical release-v1 CSV/JSON artifacts, served for the
  Download/Audit tab.

## Tabs

1. **Start Here** — what the index measures, what it doesn't, coverage summary.
2. **Compare Scenarios** — Greenwich RA-4 benchmark vs. a selected Bridgeport scenario, domain by domain.
3. **Bridgeport Distribution** — the full distribution of eligible Bridgeport scenario scores against
   the Greenwich benchmark (never a single "Bridgeport score").
4. **Sensitivity** — all 6 required sensitivity variants, per scenario and in aggregate.
5. **Evidence Explorer** — all 12 registry variables (not just the 9 scored ones) for any scenario,
   with source page/section and exclusion reasons where applicable.
6. **Excluded Context** — V3/V4/V10 and why they're not in the numeric score.
7. **Methods and Limits** — formulas, weights, frozen rubrics, limitations.
8. **Download / Audit** — the real underlying files, plus version/hash metadata.

## Data integrity

Every number shown reconciles exactly to the canonical `data/processed/release_v1/*` CSVs — verified
programmatically when `data/data.json` was generated (see
`outputs/review/release_v1/interactive_data_reconciliation_audit_v1.csv`). The app does not read any
raw or mutable repository file at runtime; it only reads its own bundled `data/data.json`.

## Known limitations of this interactive build

- No maps or geographic rendering (per the release protocol: GIS data is not used to imply a legal
  boundary here).
- The Evidence Explorer shows citation metadata (page/section) but not rendered page-crop images —
  the underlying page-crop image library is a documented follow-up (see repository
  `docs/KNOWN_LIMITATIONS.md`).
- Built and tested in a Chromium-based browser via a local HTTP server; no cross-browser matrix was run.
