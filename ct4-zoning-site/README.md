# CT-4 Zoning Scorecard

A living, citation-backed zoning restrictiveness scorecard for towns in Connecticut's 4th
Congressional District. Built for a meeting with Rep. Jim Himes's office; designed to grow
beyond the initial 17 towns.

## Run it

```bash
npm install
npm run dev
```

Open http://localhost:3000 (or the port your `.claude/launch.json` config points at).

## How data is stored

Everything lives in `/data` as plain JSON, versioned in git — no database. This keeps every
research pass diffable and makes adding a town as simple as adding one file.

- `data/towns/<slug>.json` — one file per town: composite score, the five NZA-sourced metrics
  that feed it, and two `DistrictBlock`s (most restrictive / most permissive district) with
  individual facts, each carrying its own `source` + `cite`.
- `public/sources/<file>.pdf` — mirrored copies of the source regulations, used by the in-app
  PDF citation viewer. Not every town has one: some sources blocked automated downloads or are
  browsable code sites (eCode360, encodeplus) rather than a single PDF. Those towns fall back
  to an "open the live source" link instead of the embedded viewer.

### Adding a new town

1. Research it the way the existing 17 were researched (town's own current zoning regs +
   matching NZA Jurisdiction Snapshot at `zoningatlas.org`).
2. If you can get a PDF, mirror it into `public/sources/<slug>.pdf`.
3. Add a new entry to `scripts/build_data.py` (or just hand-write
   `data/towns/<slug>.json` following the existing files' shape — see `src/lib/types.ts`
   for the schema) and run:
   ```bash
   python3 scripts/build_data.py   # if using the script
   python3 scripts/hash_sources.py # stamps content_hash for PDF change-detection
   ```
4. The overview page and heatmap auto-discover every file in `data/towns/` at build time —
   nothing else to wire up.

## Citation traceability

Every metric on a town page is a clickable/hoverable citation. Clicking one opens
`SourceViewer`, which:

- For a mirrored PDF: loads it with `pdfjs-dist`, searches all pages for the citation's most
  distinctive token (e.g. "6-93" out of "Sec. 6-93(a)(1)"), jumps to the first matching page,
  and highlights the match.
- For a source with no local mirror (blocked download, or a browsable code site, or an NZA
  snapshot page): shows a clear note and a link to the live source instead of guessing.

## "Check for zoning changes"

Each town page has a button that hits `/api/check/[slug]`, which re-fetches the town's live
primary source and compares a sha256 hash against the one stamped at ingest time
(`scripts/hash_sources.py`). It reports **up to date**, **changes detected**, or
**no baseline** (for link-only sources) — it does **not** automatically re-run research. If it
flags changes, re-run the research pass for that town by hand and regenerate its JSON file.

## Deploying to Vercel

This is a stock Next.js App Router project — no special config needed beyond what's already in
`next.config.ts`. Push to a GitHub repo and import it in Vercel, or run `vercel` from this
directory. The mirrored PDFs ship as static assets under `/public`, so citations work
immediately in production with no extra storage setup.

## Known limitations (be upfront about these with staff)

- NZA percentages are **town-wide averages**, not district-specific — a town's single most
  restrictive or most permissive district can differ from its town-wide number.
- A handful of source PDFs were blocked by bot-detection on the town's own site; those towns'
  cards note the fallback used.
- No real GIS/map view yet — the heatmap is a town × metric grid, not geographic district
  polygons. Swapping in a real map is straightforward once a town's zoning district GeoJSON is
  collected (see `src/components/MetricHeatmap.tsx` for where to add it).
