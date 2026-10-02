# GIS_METHODS_AND_LIMITATIONS.md

## Independently verified this run

- Bridgeport zoning-district GeoJSON: **2000 features**, CRS `EPSG:4326`,
  geometry type(s) `['Polygon']`, **2000 valid /
  0 invalid** geometries (via `shapely`/`geopandas` validity check).
- District/ordinance crosswalk: **16 of 24**
  canonical districts have a GIS-mapped presence (66.7%);
  the remaining 8 are `ordinance_only` -- defined in the zoning
  text but not present as a mapped polygon in this GIS extract.

## Explicit scope statement

- **The GIS layer does not establish legal entitlement.** It is a parcel-level/parcel-derived extract
  (per Bridgeport's own GIS README), not a pre-dissolved, authoritative zone-boundary layer.
- **Absence from this 2000-feature GIS extract is not proof of legal
  absence.** A district can be real, legally defined, and currently unmapped in this particular GIS
  snapshot (e.g. an overlay or a district with zero current parcels).
- **GIS area figures (`gross_mapped_area_acres`) are gross, parcel-derived figures only** -- they
  exclude no water/right-of-way/non-buildable land and are never used as a buildable or developable
  area estimate anywhere in this project.
- **No fuzzy matching was used to establish legal correspondence** between a GIS zone code and an
  ordinance district code -- the crosswalk above is an exact-code match only; unmatched codes are
  reported as `ordinance_only`, not silently paired to the nearest GIS code.
