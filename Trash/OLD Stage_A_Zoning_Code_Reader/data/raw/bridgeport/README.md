# Bridgeport zoning-code sources

## Canonical zoning code

- Jurisdiction: City of Bridgeport, Connecticut
- Filename: `bridgeport_zoning_code_full_2022-01.pdf.pdf` (double extension as provided; left unchanged since raw sources are immutable)
- Relative path: `data/raw/bridgeport/bridgeport_zoning_code_full_2022-01.pdf.pdf`
- Pages: 304 (computed directly from the PDF; see `source_metadata.json` for the hash)
- Effective/version date: effective January 1, 2022, adopted November 29, 2021 (both stated on the document's own title page)
- Official source URL: unknown — manually downloaded before pipeline run
- Retrieval date: unknown — manually downloaded before pipeline run
- Immutable-source statement: this file is treated as immutable evidence. The collection notebook may read and hash it but must never overwrite, edit, annotate, or save derived content over it.

## Official zoning map

- Not present in `data/raw/bridgeport/` as of this writing. No separate zoning-map PDF was supplied.

## GIS zoning-district polygons

- Local file: `data/raw/bridgeport/gis/bridgeport_zoning_districts_2021.geojson`
- Official FeatureServer URL (per user-supplied metadata, not independently re-verified by this notebook run): `https://services6.arcgis.com/mQcEelNKPZjQfrvM/arcgis/rest/services/Zoning___Sept2021_WFL1/FeatureServer/0`
- Layer name: `ZONE_2021_Parcels`
- Geometry type: Polygon (confirmed: 2,000 features, CRS EPSG:4326 in the local file)
- Primary zoning-code field: `ZONE_2021` (confirmed present, 0 nulls across 2,000 features)
- Supporting fields present: `LOCAL_HISTDIST` (111 non-null of 2,000), `Allowed01`–`Allowed05` (+ `_Link` variants), `ZONE_ID`, `ZONE_`, `SUMMARY_CAT`, plus duplicated `OBJECTID`/`Name` variants (`_1`, `_12`) suggesting this file is a join of a parcel layer to a zoning-polygon layer
- Rollout context: reflects the September 2021 zoning layer used for Bridgeport's January 2022 zoning-code rollout (per filename/date alignment with the code's effective date)
- Gross-area limitation: this layer is parcel-level or parcel-derived, not a pre-dissolved zone boundary layer. Any area computed from it must be labeled `gross_mapped_area_acres` and must not be called `developable_residential_area_acres` unless documented exclusions (water, rights-of-way, non-buildable land) are actually calculated.
- Unique `ZONE_2021` values observed in the local file (16): I, IX, MX1, MXN, N1, N2, N3, NX1, NX2, NX3, NX4, P1, P2, P4, RX1, RX2. (Additional codes referenced elsewhere for Bridgeport, e.g. DX1, DX2, CX, P3, P5, PDD, do not appear in this particular 2,000-feature local extract and should not be assumed present until found in either the ordinance text or a fuller GIS pull.)

## Source handling

- Raw source files in this directory remain unchanged by any notebook.
- All derived products (tokens, hierarchy, tables, evidence bundles, GIS joins, etc.) are written outside `data/raw/`, under `data/interim/bridgeport/`, `data/processed/bridgeport/`, and `outputs/*/bridgeport/`.
