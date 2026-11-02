# Map data notes (retrieved 2026-11-02)

## Town outlines: ct4-towns.geojson (26 KB, 17 features)
- Source: Census Cartographic Boundary 2021 county subdivisions, CT, 1:500k, shoreline-clipped.
  https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_09_cousub_500k.zip
- License: public domain (US Government work).
- Processing: simplify 0.0001 deg, 5-decimal rounding. 1:500k is coarse (~100 m); fine for a regional choropleth, will not align exactly with parcel-level district edges.

## District files (districts/<slug>.geojson)
Properties: `code` (our code, or null when unmatched), `original_code` (source label; joined with " + " when merged), `scored_v2` (true if code is in the V2 scored list given for that town). Same-code polygons are merged into one MultiPolygon. Collection-level `note` repeats the source. Rewrite: simplified, 5-decimal rounding. Unmatched districts are kept with code null (draw gray), nothing fabricated.

### Stamford, Greenwich, Norwalk: CT Zoning Atlas (DesegregateCT / CT Data Collaborative)
- URL: https://ct-data-collaborative.github.io/desegregate-ct-map/map/data/final.20220427.geojson (statewide, 14.8 MB; file dated 2022-04-27). Map page: https://ct-data-collaborative.github.io/desegregate-ct-map/map/
- License: none stated on the map page or repo pages found; treat as "published by DesegregateCT / CT Data Collaborative, attribute, confirm terms before commercial reuse". Not the later NZA zoningatlas.org release (no CT download found there; the NZA S3 bucket statezoningatlasdata is gone and Mercatus lists no CT file).
- Vintage caveat: 2022 snapshot. Stamford/Greenwich names are post-2022 where unchanged but may have since been amended; Norwalk is the pre-rewrite map.
- Simplify tolerance: 0.00006 deg (Stamford, Norwalk), 0.0001 deg (Greenwich).

**Stamford** (187 KB; covers ~98% of town area). Atlas gives names, not codes; matched by name:
RA-3, RA-2, RA-1 exact; "RA-20 One Family" -> R-20 and "RA-10 One Family" -> R-10 (atlas label says RA-; our codes are R-20/R-10, matched by lot size, likely atlas labeling variance); "R-7-1/2" -> R-7 1/2; R-6; R-5; RM-1; "Multiple Family Residence Design" -> R-MF (name match, moderate confidence). "X/Designed Residence" variants -> RA-1/R-D, RA-2/R-D, R-10/R-D, R-20/R-D (codes that exist in data/land_area/stamford.json; not in the scored list, fold to base code if desired).
Unmatched (code null): Center City North, Coastal Water Dependent, Community Business, Designed Business/Commercial/Community Shopping Center/High-Technology/Industrial Park/Industrial/Mill River/Transportation Center/Waterfront Development, General Commercial, General Industrial, Hospital Complex Design, Intermediate Commercial, Light Industrial, Limited Business, Mixed Use Development, Multiple Family Design High Density (likely R-H/R-HD, not asserted), Neighborhood Business, Neighborhood Mixed Use Design, Park, Planned Development, South End Redevelopment North/South, Village Commercial.
All 10 scored Stamford codes are present.

**Greenwich** (324 KB; ~86% coverage): 4/2/1 Acre Residence -> RA-4/RA-2/RA-1; R-20, R-12, R-7, R-6 exact; Multifamily -> R-MF. Also matched (not scored): acre conservation -> RA-C4/C2/C1, R-C20/C12/C7, Planned Residential -> R-PR, Planned Housing Elderly/Small Unit -> R-PHD-E/R-PHD-SU, Central Greenwich Business (Retail) -> CGB/CGBR, General Business (-Office) -> GB/GBO, Local Business -> LB, Waterfront Business -> WB, Hospital H-1/H-2, Parking -> P, Executive Office Business -> BEX-50 (moderate; BEX-50-R not separable).
Unmatched: Historic Overlay, Local Business Retail (LBR-1 vs LBR-2 not separable), "None".
All 8 scored Greenwich codes present.

**Norwalk** (138 KB; ~91% coverage): atlas uses pre-rewrite names. Crosswalk from data/land_area/norwalk.json applied: AAA -> CD-1L; AA and A -> CD-1M; B -> CD-1S; C -> CD-2; D and Neighborhood Business (NB) -> CD-3. original_code holds the old code (e.g. "A + AA"). Mapping reflects the old city map; areas may be stale (see status in norwalk.json).
Unmatched (null): Business 1/2, Central Business, East Avenue Village, Executive Office, Golden Hill Village, Hospital, Industrial No. 1, Island Conservation, Light Industrial No. 2, Marine Commercial, Reed-Putnam Design, Research & Development, Restricted Industrial, Rowayton Avenue Village, Silvermine Tavern Village, SoNo Station Design, South Norwalk Business, Washington Street Design (no crosswalk entry).
All 5 CD codes present.

### Bridgeport (410 KB; ~83% coverage; slightly over the 400 KB target)
- Source: City of Bridgeport GIS Hub, "2023 Zoning Parcels" (ZONE_2023, parcel polygons, 28,046 features), plain GeoJSON download:
  https://city-of-bridgeport-gis-hub-bridgeportct.hub.arcgis.com/api/download/v1/items/96b9402f162d42099ee08889bece123e/geojson?layers=0 (item page: .../datasets/96b9402f162d42099ee08889bece123e_0)
- License: none stated in the Hub metadata (public municipal open data portal); confirm.
- Used instead of the Atlas because it carries the exact current codes (the Atlas has only descriptive names, e.g. two "Mixed Use Corridor" features that cannot be split into MX1/MX2).
- Method: parcels are not districts, so each parcel was buffered ~5 m (0.00005 deg) outward and unioned per code to close street gaps; adjacent districts may therefore overlap by a few meters and streets are shaded. Simplify 0.00012 deg.
- Matched exactly: N1, N2, N3 (one parcel "N3 Estates" merged into N3), N4, NX1-NX4, DX1, DX2, MX1, MX2, MXN, RX2 (all 14 scored codes present).
- Unmatched (null, shown for completeness): RX1, CX, I, IX, P1, P2, P4, P5, PDD.

## Not found / limitations
- No NZA/zoningatlas.org Connecticut download link was found; no statewide zoning layer exists on geodata.ct.gov or the CT Housing Data Hub (housingmaps.ct.gov).
- Stamford, Greenwich and Norwalk city open-data portals with plain zoning downloads were not found (Greenwich GIS is request/fee-based; Stamford and Norwalk offer only viewers).
- All Atlas-derived files are 2022 vintage.
- Tools: Python 3.12 + shapely 2.2 + pyshp in a scratchpad venv; downloads treated as untrusted data.
