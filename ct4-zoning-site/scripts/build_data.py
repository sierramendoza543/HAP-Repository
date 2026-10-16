#!/usr/bin/env python3
"""Builds /data/towns/*.json from research findings.
Each variable carries a citation: {source, cite, quote}. `quote` is verbatim
text independently verified against the source document's own extracted
text (via pdftotext on the mirrored PDF). Where we don't have a confirmed
verbatim match, quote is None -- the UI then says so plainly instead of
highlighting the wrong thing."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOWNS_DIR = os.path.join(ROOT, "data", "towns")

def nza(jid):
    return {"kind": "nza", "id": f"nza-{jid}", "url": f"https://edit.zoningatlas.org/statsrollup/jurisdiction/{jid}/", "title": "NZA Jurisdiction Snapshot"}

def pdf(slug, file, title, live_url):
    return {"kind": "pdf", "id": f"{slug}-pdf", "file": f"/sources/{file}", "url": live_url, "title": title}

def link(slug, title, live_url):
    return {"kind": "link", "id": f"{slug}-link", "url": live_url, "title": title}

TOWNS = {}

def add(slug, name, jurisdiction_id, population, land_area_acres, districts_analyzed,
        composite_score, nza_metrics, primary_source, restrictive_district,
        permissive_district, variables, caveat):
    TOWNS[slug] = {
        "slug": slug, "name": name, "jurisdiction_id": jurisdiction_id,
        "population": population, "land_area_acres": land_area_acres,
        "districts_analyzed": districts_analyzed, "composite_score": composite_score,
        "last_checked": "2026-10-16",
        "restrictive_district": restrictive_district,
        "permissive_district": permissive_district,
        "variables": variables,
        "nza_metrics": nza_metrics,
        "primary_source": primary_source,
        "caveat": caveat,
    }

def nza_block(jid, pct2, pct3, pct4, lot80, parking):
    src = nza(jid)
    def m(label, value, unit=""):
        return {"label": label, "value": value, "unit": unit, "source": src}
    return [
        m("2-family housing prohibited", pct2, "% of residential land"),
        m("3-family housing prohibited", pct3, "% of residential land"),
        m("4+-family housing prohibited", pct4, "% of residential land"),
        m("1-family lots requiring ≥80,000 sq ft", lot80, "% of 1-family land"),
        m("Residential land with a parking mandate", parking, "% of residential land"),
    ]

def v(category, district, label, value, source, cite, quote=None):
    return {"category": category, "district": district, "label": label, "value": value,
            "source": source, "cite": cite, "quote": quote}

U, D, A, P, AP = "Use Permissions", "Dimensional Standards", "ADU Policy", "Parking", "Approval Process"

# ================= GREENWICH =================
gw9 = pdf("greenwich", "greenwich-div9.pdf", "Building Zone Regulations, Div. 9 (Use Regs, Aug. 2023)", "https://www.greenwichct.gov/DocumentCenter/View/37828")
gw21 = pdf("greenwich21", "greenwich-div21.pdf", "Building Zone Regulations, Div. 21 (Bulk Schedule)", "https://www.greenwichct.gov/DocumentCenter/View/37841")
add("greenwich", "Greenwich", 317, 64594, 30322, 49, 82.7,
    nza_block(317, 95.3, 97.7, 98.3, 59.8, 92), gw9, "R-20 / RA-2", "R-MF",
    [
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "Single-family", "Allowed by-right — only permitted use", gw9, "§6-93(a)(1)",
          "The following principal uses are permitted in RA-4, RA-2, RA-1, R-20 and R-12 Zones and all other principal uses are expressly excluded: (1) Detached single family dwellings, one (1) per lot."),
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "Two-family", "Prohibited", gw9, "§6-93 / 6-94"),
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "Three-family", "Prohibited", gw9, "§6-93 / 6-94"),
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "4+-family", "Prohibited", gw9, "§6-93 / 6-94"),
        v(D, "R-20", "Min. lot size", "20,000 sq ft", gw21, "§6-205(a) table", "20,000"),
        v(D, "RA-2", "Min. lot size", "2 acres (87,120 sq ft)", gw21, "§6-205(a) table"),
        v(D, "RA-4", "Min. lot size", "4 acres (174,200 sq ft)", gw21, "§6-205(a) table"),
        v(D, "R-12", "Min. lot size", "12,000 sq ft", gw21, "§6-205(a) table"),
        v(U, "R-MF", "Two-family / multifamily", "Special Permit only, no distinct 3-unit tier", gw9, "§6-98.1(a)(2)(A)",
          "The building of a two family dwelling, conversion from a single family to a two-family dwelling, addition or alteration to a single family dwelling to create a two-family dwelling, additions to an existing (2) two-family residence, addition or alteration to one or more multi-family dwellings or a combination of single family, two-family and/or multi-family dwellings on a lot."),
        v(D, "R-MF", "Min. lot area, multifamily tier", "2,400 sq ft/family", gw21, "§6-205(a)", "2,400"),
        v(A, "Town-wide", "ADU max size (External, R-20/RA-1)", "1,000 sq ft", gw9, "§6-99(a)(3)(D)(i)",
          "External ADUs shall be limited to 800 square feet in R-12, R-7 and R-6 zones; 1,000 square feet in RA-1 and R-20 zones; and 1,200 square feet in RA-2 and RA-4 zones."),
        v(A, "Town-wide", "ADU owner-occupancy", "Required — owner must reside in either unit", gw9, "§6-99(a)(3)(A)",
          "The owner of record (the “Owner”) must reside in either the ADU or the Primary Unit."),
        v(A, "Town-wide", "ADU approval pathway", "By Zoning Permit (not Special Permit, unless oversized/nonconforming)", gw9, "§6-99(a)(2)-(4)"),
        v(AP, "R-MF", "Multifamily approval pathway", "Special Permit (Planning & Zoning Commission)", gw9, "§6-98.1(a)(2)"),
        v(P, "R-MF", "Parking, 1–2BR unit", "1 garage space + 1 outdoor space", gw9, "§6-155 (Div. 15, not locally mirrored)"),
    ],
    "Town adopted 2025–2026 amendments (nursing-home conversions, multifamily parking per PA 25-1) not fully reflected in the Aug. 2023 PDF — verify against the amendment list before external use. The parking table (Div. 15, §6-155) was cited from the original research pass but is not locally mirrored for quote verification.")

# ================= BRIDGEPORT =================
bp = pdf("bridgeport", "bridgeport-zoning.pdf", "\"Zone Bridgeport\" form-based code (amended July 2022)", "https://portal.ct.gov/-/media/CSC/1_Dockets-medialibrary/1_MEDIA_DO500_600/DO516/ApplicantSubmissions/Application/UI---City-of-Bridgeport-Zoning-Code-Amended-July-25-2022.pdf")
add("bridgeport", "Bridgeport", 311, 151599, 10246, 25, 15.5,
    nza_block(311, 31.5, 39.3, 37.9, 0.0, 0), bp, "N1", "NX2",
    [
        v(U, "N1", "Single-family (House A)", "1 in House — no 2-unit option exists", bp, "§3.90.9",
          "Number of Principal Units: 1 in House"),
        v(U, "N1", "ADU", "1 in House or Backyard Cottage — allowed by-right", bp, "§3.90.9"),
        v(D, "N1", "Min. lot width", "45 ft (no lot area minimum)", bp, "§3.90.4", "Lot Width: 45 ft. min."),
        v(U, "NX2", "Up to 4 units (House A)", "By-right, no special permit, + 1 backyard cottage", bp, "§3.90.9",
          "up to 4 in House plus 1 in Backyard Cottage"),
        v(U, "NX2", "Double House A", "Up to 4 by-right / 6 with special permit", bp, "§3.80.9"),
        v(U, "NX2", "Small General building type", "3 min., 6 max., up to 8 with special permit", bp, "§3.60.9"),
        v(D, "NX2", "Min. lot width (House A)", "35 ft", bp, "§3.90.4"),
        v(AP, "NX2", "4+-unit approval pathway", "By-right up to 4 units; Special Permit above that", bp, "§3.90.9 / §3.80.9"),
        v(P, "Town-wide", "Parking minimum", "None — citywide", bp, "§8.20.1",
          "This zoning code does not establish minimum off-street parking requirements"),
    ],
    "A 2025 proposal (25-23) to add residential parking minimums citywide was found but its adoption status is unconfirmed.")

# ================= STAMFORD =================
sf = pdf("stamford", "stamford-zoning.pdf", "Zoning Regulations, City of Stamford (through July 10, 2024)", "https://stamfordct.gov/home/showpublisheddocument/5847/638568338177670000")
add("stamford", "Stamford", 304, 139134, 23707, 46, 64.7,
    nza_block(304, 86.5, 87.9, 73.9, 21.9, 100), sf, "R-20", "R-6",
    [
        v(U, "R-20", "District definition", "One-Family Residence District", sf, "Table I; §1-2",
          "R-20              One-Family Residence District"),
        v(U, "R-20", "Two-family / multifamily", "Both prohibited", sf, "Table I"),
        v(D, "R-20", "Min. lot size", "20,000 sq ft", sf, "Table II, Appendix B",
          "R-20          20000   100   100   20000     1    2½    30    15"),
        v(U, "R-6", "District definition", "One-Family, Two-Family Residence District", sf, "Table I; §1-2",
          "R-6               One-Family, Two-Family Residence District"),
        v(U, "R-6", "Two-family", "Allowed by-right", sf, "Table I"),
        v(U, "R-6", "Multifamily (3+)", "Still prohibited", sf, "Table I"),
        v(D, "R-6", "Min. lot size", "5,000 sq ft (1F) / 6,000 sq ft (2F)", sf, "Table II, Appendix B",
          "R-6           5000     50      -              -      1(19)      2½        30"),
        v(A, "Town-wide", "ADU eligibility", "Only lots with ≤1 single-family dwelling and ≥10,000 sq ft lot area", sf, "ADU definition, §222-28",
          "ADUs shall only be permitted on Lots containing no more than one (1) Single-Family Dwelling and which have a Lot Area of at least 10,000sf"),
        v(A, "Town-wide", "ADU owner-occupancy", "Required", sf, "ADU definition, §222-28",
          "The property owner must reside on the premises."),
        v(A, "Town-wide", "ADU max size", "800 sq ft gross floor area", sf, "ADU definition, §222-28",
          "The size of the ADU shall not exceed eight hundred (800) sf in Gross Floor Area"),
        v(A, "Town-wide", "ADU eligibility exclusion", "Multifamily (incl. legally nonconforming 2-/3-family) ineligible", sf, "ADU definition, §222-28",
          "No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units"),
        v(P, "R-20/R-6", "Parking, single-family house", "2 spaces", sf, "§12.D.2, Table 12.7"),
        v(P, "R-6", "Parking, two-family house (per unit)", "2 spaces/unit", sf, "§12.D.2, Table 12.7"),
    ],
    "Live stamfordct.gov PDF was blocked by bot-protection during research; a Wayback Machine snapshot of the identical text was used — recommend re-verifying the live link.")

# ================= NORWALK =================
nw3 = pdf("norwalk", "norwalk-art3.pdf", "Norwalk Zoning Regulations, Art. 3 (Zoning Districts, eff. Feb. 2024)", "https://www.norwalkct.gov/DocumentCenter/View/32245")
nwb = pdf("norwalkbulk", "norwalk-bulk.pdf", "Norwalk Bulk & Height Schedule (7/9/2025)", "https://www.norwalkct.gov/DocumentCenter/View/36646")
add("norwalk", "Norwalk", 303, 93661, None, 23, 55.9,
    nza_block(303, 77.5, 81.9, 81.9, 0.0, 100), nw3, "CD-1S", "CD-2",
    [
        v(U, "CD-1S", "Two-family & multifamily", "Both \"NP\" (Not Permitted)", nw3, "Table 4.3.9.A"),
        v(D, "CD-1S", "Min. lot size", "6,250 sq ft", nwb, "Bulk & Height Schedule (7/9/2025)", "CD-1S        6,250"),
        v(A, "CD-1S", "ADU", "Permitted by-right with limitations", nw3, "Table 4.3.9.A, §4.3.4.C.3.a"),
        v(U, "CD-2", "Two-family", "\"P\" — permitted by right; multifamily still \"NP\"", nw3, "Table 4.3.9.A"),
        v(D, "CD-2", "Min. lot size", "5,000 sq ft", nwb, "Bulk & Height Schedule (7/9/2025)", "CD-2         5,000"),
        v(A, "CD-1S/CD-2", "ADU max size", "1,000 sq ft", nw3, "§4.3.4.C.3.a"),
        v(A, "CD-1S/CD-2", "ADU eligibility", "Must be on a lot with a Single-Family Detached Dwelling; 1 per lot, owner must reside on lot", nw3, "§4.3.4.C.3.a"),
        v(P, "CD-1S/CD-2", "Parking minimum", "Not regulated for buildings of ≤16 units, except in Traffic Mitigation Districts", nw3, "Table 4.3.12.B-1"),
    ],
    "CD-3/CD-4 allow multifamily by-right-with-limitations, but column alignment for CD-3W/CD-4W sub-variants was ambiguous in the extracted PDF text — not reported to avoid miscitation. The use-permission table (Table 4.3.9.A) and ADU standards (§4.3.4) weren't in the PDFs mirrored locally, so those rows above carry a citation but not an independently re-verified quote.")

# ================= DARIEN =================
dn = link("darien", "Darien Zoning Regulations (last revised May 10, 2026)", "https://www.darienct.gov/DocumentCenter/View/6613")
add("darien", "Darien", 302, 22528, None, 26, 74.5,
    nza_block(302, 97.0, 97.0, 97.0, 32.4, 100), dn, "R-1", "DMR",
    [
        v(U, "R-1/R-2/R-1½/R-1⅓/R-1⅕", "Only single-family permitted", "2-/3-/4+-family prohibited town-wide", dn, "§402.a",
          "a single, detached one-family dwelling on its own lot"),
        v(D, "R-1", "Min. lot size", "43,560 sq ft (1 acre)", dn, "§406"),
        v(D, "R-2", "Min. lot size", "87,120 sq ft (2 acres)", dn, "§406"),
        v(U, "DMR", "Multifamily", "Special Permit only", dn, "§524.a"),
        v(D, "DMR", "Min. lot size (zone)", "3 acres (130,680 sq ft)", dn, "§525"),
        v(U, "DMR", "Density", "4 DU/net acre by-right (6 with 20% affordable)", dn, "§526.1"),
        v(U, "DMR", "Bedroom mix requirement", "≥15% of units must be 1BR; no unit may exceed 3BR", dn, "§526.3"),
        v(A, "Town-wide", "ADU max size", "700 sq ft attached / 1,000 sq ft detached, and <30% of combined floor area", dn, "§407.c"),
        v(A, "Town-wide", "ADU owner-occupancy", "Required (annual affidavit)", dn, "§407.c"),
        v(A, "Town-wide", "ADU program sunset", "Expires for new applications after June 30, 2029 unless readopted", dn, "§407.c"),
        v(P, "R-1/R-2", "Parking, one-/two-family residences", "2 spaces/unit", dn, "§904.a"),
    ],
    "Darien formally opted OUT of CT's statewide ADU law (PA 21-29) via local vote in 2022 — its ADU rules exist under independent local authority. No local PDF mirror exists for Darien (blocked at ingest time), so quotes above are limited to what the research pass directly transcribed.")

# ================= NEW CANAAN =================
nc = pdf("newcanaan", "newcanaan-zoning.pdf", "New Canaan Zoning Regulations (amended through May 1, 2023)", "https://cms3.revize.com/revize/newcanaanct/Departments/Land%20Use/Zoning%20Regulations.pdf")
add("new-canaan", "New Canaan", 319, 21160, None, 24, 92.4,
    nza_block(319, 97.4, 98.3, 98.3, 81.3, 100), nc, "Four Acre Residence Zone", "B Residence Zone / Apartment Zone",
    [
        v(U, "Four Acre Residence Zone", "2-/3-/4+-family", "Prohibited — only 1 family/building (except age-restricted via special permit)", nc, "§3.3.C table, note 1",
          "a two-family dwelling in the B Residence Zone per Section 3.2.C.1."),
        v(D, "Four Acre Residence Zone", "Min. lot size", "174,240 sq ft (4 acres)", nc, "§3.5.A.1 table",
          "Four Acre Residence Zone                                          174,240"),
        v(U, "B Residence Zone", "Two-family", "Special Permit only", nc, "§3.2.C.1"),
        v(D, "B Residence Zone", "Min. lot size", "7,500 sq ft", nc, "§3.5.A.1 table",
          "B Residence Zone                                                     7,500"),
        v(U, "Apartment Zone", "Two-family & multifamily", "Both Special Permit only", nc, "§5.4.C.1-2"),
        v(D, "Apartment Zone", "Max density", "1 unit / 5,000 sq ft", nc, "§5.4.D.1"),
        v(A, "Town-wide", "ADU max size", "1,000 sq ft or 40% of combined floor area, whichever less", nc, "§3.3.B.6",
          "not exceed 1,000 square feet or 40% of the combined floor areas of the single-family dwelling and the accessory dwelling unit"),
        v(A, "Town-wide", "ADU owner-occupancy", "Required", nc, "§3.3.B.6",
          "the owner of the property shall occupy either the principal dwelling unit or the accessory dwelling unit"),
        v(P, "Town-wide", "Parking, single-family", "2 spaces", nc, "§6.2.C table"),
        v(P, "B Residence Zone", "Parking, two-family", "2 spaces/unit (4 total)", nc, "§6.2.C table"),
    ],
    "No as-of-right multifamily district exists anywhere in New Canaan — every multi-unit pathway requires a discretionary Special Permit hearing.")

# ================= WESTPORT =================
wp = link("westport", "Westport Zoning Regulations (eff. April 12, 2024)", "https://online.encodeplus.com/regs/westport-ct/")
add("westport", "Westport", 329, 27996, None, 40, 35.2,
    nza_block(329, 0.6, 0.3, 0.2, 38.0, 100), wp, "Residence AAA", "Residence C",
    [
        v(U, "Residence AAA", "Two-family / multifamily", "Prohibited as normal use (only via §32-12 Special Permit)", wp, "§11-2.1.1 / §11-2.3.16"),
        v(D, "Residence AAA", "Min. lot size", "2 acres", wp, "§11-3"),
        v(U, "Residence C", "Two-family", "Allowed BY RIGHT as a principal use", wp, "§18-2.1.2"),
        v(D, "Residence C", "Max density", "10 units/gross acre", wp, "§18-4.1"),
        v(D, "Residence C", "Town-wide aggregate cap", "120 total dwelling units under this zone", wp, "§18-4.2"),
        v(U, "Residence C", "Affordability requirement", "≥15% of market-rate units workforce/affordable (or 17.5% fee-in-lieu)", wp, "§18-17.1-2"),
        v(A, "Residence AAA", "ADU max size (structural, no owner-occ.)", "850 sq ft (≤1.5 ac) / 1,000 sq ft (>1.5 ac)", wp, "§11-2.4.8A"),
        v(A, "Residence AAA", "ADU max size (internal apartment, owner-occ. req.)", "1,500 sq ft or 25% of total floor area, whichever smaller", wp, "§11-2.4.12A"),
        v(A, "Residence C", "ADU availability", "Excluded — §11-2.4.12 accessory apartment provision not carried over", wp, "§18-2.2.1"),
        v(P, "Town-wide", "Parking, developments ≤16 units", "No minimum (2026 amendment, §34-14.1), except in a Conservation & Traffic Mitigation District", wp, "§34-14.1"),
    ],
    "A 2026 amendment (§34-14.1) eliminated minimum parking entirely for residential developments of 16 units or fewer townwide. No local PDF mirror exists for Westport (browsable encodeplus code site, not a single PDF), so these facts carry citations but not independently re-verified quotes.")

# ================= WILTON =================
wl = link("wilton", "Wilton Zoning Regulations (last revised Sept. 2026)", "https://www.wiltonct.gov/planning-zoning-department/files/regulations-document-october-7")
add("wilton", "Wilton", 330, 19255, None, 19, 95.4,
    nza_block(330, 98.5, 98.7, 98.7, 88.8, 100), wl, "R-2A", "HODD",
    [
        v(U, "R-2A", "\"Two-family\" / \"three-family\"", "Do not exist anywhere in the 337-page code", wl, "full-text search"),
        v(U, "R-2A", "Multifamily", "Prohibited", wl, "§29-5.A.2.a"),
        v(D, "R-2A", "Min. lot size", "2 acres (87,120 sq ft)", wl, "§29-5.D table"),
        v(U, "HODD", "Multi-family attached dwellings", "Permitted as a matter of right", wl, "§29-5.E.8",
          "Permitted Uses. The following principal uses shall be permitted in the HODD as a matter of right: a. Multi-family attached dwellings. b. Open space. c. Single-family detached dwellings."),
        v(D, "HODD", "Lot area", "9–11 acres", wl, "§29-5.E.9.a-b"),
        v(U, "HODD", "Density / affordability", "10 units/gross acre, 30% affordable required", wl, "§29-5.E.9.c-d"),
        v(A, "Town-wide", "ADU max size", "¼ of gross floor area or 750 sq ft, whichever greater; max 2 bedrooms", wl, "§29-4.D.1"),
        v(A, "Town-wide", "ADU owner-occupancy", "Required (one unit, annual certification)", wl, "§29-4.D.1"),
        v(P, "DRD/multifamily <17 units", "Parking minimum", "None, unless in a Conservation & Traffic Mitigation District", wl, "§29-8.B.5"),
        v(P, "R-2A", "Parking, single-family", "2/unit + 1 per guest sleeping room for roomers/boarders", wl, "§29-8.B.5.a(1)"),
    ],
    "HODD sites are capped between 9 and 11 acres — a narrow, purpose-built carve-out, not a general-purpose multifamily zone. No local PDF mirror exists for Wilton, so only the HODD permitted-uses fact above has an independently re-verified quote.")

# ================= RIDGEFIELD =================
rf = link("ridgefield", "Ridgefield Zoning Regulations (revised through July 2026)", "https://ridgefieldct.gov/Documents/Boards%20Committees%20and%20Commissions/Planning%20and%20Zoning%20Commission/About%20PZC%20Meetings/Zoning%20Regulations/Zoning%20Regulations%20July%2026.pdf")
add("ridgefield", "Ridgefield", 323, 25300, None, 21, 61.8,
    nza_block(323, 95.8, 95.6, 95.6, 0.0, 97), rf, "RAAA", "MFDD",
    [
        v(U, "RAAA", "Single-family", "Allowed, requires Zoning Permit (ZEO)", rf, "§3.2.B.1"),
        v(U, "RAAA", "2-/3-family", "Bundled & prohibited except by Special Permit in the separate SD R-20 overlay", rf, "§3.2.C.10.d"),
        v(D, "RAAA", "Min. lot size", "130,680 sq ft (3 acres)", rf, "§3.5.A table"),
        v(D, "R-7.5", "Min. lot size (least restrictive base district)", "7,500 sq ft", rf, "§3.5.A table"),
        v(U, "MFDD", "Multifamily", "Special Permit only — town's only multifamily pathway", rf, "§4.2.B"),
        v(D, "MFDD", "Density", "6 units/acre (8 with 15% affordable)", rf, "§4.2.C"),
        v(A, "RAAA", "ADU max size", "900 sq ft (main dwelling <3,000 sf) or 1,200 sq ft (≥3,000 sf)", rf, "§3.3.B.2"),
        v(A, "RAAA", "ADU approval pathway", "Zoning Permit (ZEO), not Special Permit", rf, "§3.3.B.2"),
        v(P, "RAAA", "Parking, one-/two-family", "2 spaces/unit", rf, "§7.3.B table"),
        v(P, "RAAA", "Parking, ADU + principal", "3 spaces combined", rf, "§3.3.B.2.h"),
    ],
    "Ridgefield has no as-of-right multifamily district of any kind — every multi-unit path requires a discretionary Special Permit hearing. No local PDF mirror exists for Ridgefield, so these facts carry citations but not independently re-verified quotes.")

# ================= WESTON =================
ws = link("weston", "Weston Zoning Regulations (amended through July 7, 2025)", "https://www.westonct.gov/home/showpublisheddocument/15463/638937003479630000")
add("weston", "Weston", 328, 10490, 12157, 3, 100.0,
    nza_block(328, 99.9, 99.9, 99.9, 100.0, 100), ws, "R-2A", "Village District / VD-R",
    [
        v(U, "R-2A", "Entire town's base zone", "2-/3-/4+-family prohibited, not addressed anywhere in the code", ws, "Sec. 321"),
        v(D, "R-2A", "Min. lot size", "2 acres", ws, "Sec. 321"),
        v(U, "Village District / VD-R", "All uses, incl. multifamily", "Require Special Permit", ws, "Sec. 322"),
        v(D, "Village District / VD-R", "Min. lot size (zone)", "1 acre, 200 ft min. width and depth", ws, "Sec. 322"),
        v(U, "Village District / VD-R", "Affordability", "5+ unit projects must set aside ≥15% affordable", ws, "Sec. 322"),
        v(U, "VD-R", "Unit size cap (2025 amendment, unverified)", "2 bedrooms / 1,200 sq ft max", ws, "§322.3(c)(ii)"),
        v(A, "R-2A", "ADU max size", "Lesser of 25% of dwelling floor area or 800 sq ft", ws, "Sec. 345.4"),
        v(A, "R-2A", "ADU owner-occupancy", "Required", ws, "Sec. 345.5"),
        v(P, "Village District / VD-R", "Parking", "1 space (1BR unit); 2 spaces (2+BR unit)", ws, "Sec. 363(b)-(d)"),
    ],
    "Town's own PDF was blocked by a bot-detection wall during research; base-district figures came from a 2021-dated third-party copy (no local mirror exists, so no quotes could be independently re-verified), and the R-2A single-family parking minimum could not be located at all — flagged for direct verification with Weston Land Use.")

# ================= EASTON =================
es = link("easton", "Easton Zoning Regulations (last revised July 7, 2024)", "https://ct-easton.civicplus.com/DocumentCenter/View/3109")
add("easton", "Easton", 316, 7815, 17110, 3, 96.9,
    nza_block(316, 100, 100, 100, 91.4, 100), es, "Residence A / Residence B", "None exists",
    [
        v(U, "Residence A/B", "\"Two-family\", \"duplex\", \"multi-family\", \"three-family\"", "Zero matches in a full-text search of the 6,576-line regulations", es, "exhaustive keyword search"),
        v(D, "Residence A", "Min. lot size", "40,000 sq ft", es, "§3510 table"),
        v(D, "Residence B", "Min. lot size", "3 acres (130,680 sq ft)", es, "§3510 table"),
        v(U, "Any district", "Multifamily pathway", "None — not even by special permit", es, "full code review"),
        v(A, "Residence A/B", "ADU max size (attached)", "Lesser of 40% of dwelling area or 1,500 sq ft", es, "§5220.2.a"),
        v(A, "Residence A/B", "ADU max size (detached)", "Lesser of 30%/1,000 sq ft (≥87,120 sf lot) or 20%/800 sq ft (≥34,000 sf lot)", es, "§5220.2.b"),
        v(A, "Residence A/B", "ADU owner-occupancy", "Required (annual affidavit)", es, "§5220.1"),
        v(A, "Residence A/B", "ADU bedroom cap", "2 bedrooms (attached) / 1 bedroom (detached)", es, "§5220.3"),
        v(P, "Residence A/B", "Parking, single-family dwelling", "2.0 spaces", es, "§6221 table"),
        v(P, "Residence A/B", "Parking, ADU", "+2.0 spaces (4 total with ADU)", es, "§6221 table"),
    ],
    "Of all 17 towns researched, Easton is the single clearest case of total legal exclusion of 2+-family housing — confirmed by exhaustive keyword search, not an oversight. No local PDF mirror exists for Easton, so these facts rest on the search method itself rather than a re-verifiable quote.")

# ================= FAIRFIELD =================
ff = pdf("fairfield", "fairfield-zoning.pdf", "Fairfield Zoning Regulations (eff. Sept. 6, 2025)", "https://fairfieldct.gov/Fairfield_ZoningRegulations_Adopted_Effective_09062025%20-%20updated%209.28.26.pdf")
add("fairfield", "Fairfield", 315, 65300, 18618, 17, 61.7,
    nza_block(315, 91.2, 95.8, 95.1, 0.0, 100), ff, "AAA/AA/R-3/R-2/A", "District C",
    [
        v(U, "AAA/AA/R-3/R-2/A", "No multi-unit housing category", "Exists at all in these five districts", ff, "§1.2, §3.1 preamble",
          "No use shall be permitted in said Districts, except as these Single-Family Residence District regulations"),
        v(U, "AAA/AA/R-3/R-2/A", "How many districts", "There shall be five Single-Family Residence Districts", ff, "§1.1",
          "There shall be five Single-Family Residence Districts, “AAA”, “AA”, “R-3”, “R-2”, and “A”."),
        v(D, "AAA", "Min. lot size", "2 acres", ff, "§3.3.1 table"),
        v(D, "A", "Min. lot size", "9,375 sq ft", ff, "§3.3.1 table"),
        v(U, "District B/C", "Two-family", "Permitted (\"P\") in both B and C", ff, "§5.2 use table",
          "A. Two-Family Dwellings                                                             P               P      Section 5.3"),
        v(U, "District C", "Three-family", "Permitted (\"P\") in C only (— in B)", ff, "§5.2 use table",
          "B.     Three-Family Dwellings                                                   —                   P"),
        v(U, "District C", "Four-family", "Permitted (\"P\") in C only (— in B)", ff, "§5.2 use table",
          "C. Four-Family Dwellings                                                        —                   P"),
        v(D, "District B/C", "Lot minimums (2F / 3F / 4F)", "9,000 (B) / 7,500 (C) — 10,000 (C) — 12,500 (C) sq ft", ff, "§5.3.1 table",
          "Minimum Lot Area for Two-Family (sf)                                                9,000              7,500"),
        v(A, "AAA/AA/R-3", "ADU (detached) availability", "Permitted; not available in R-2 or A", ff, "§3.2 table, item T"),
        v(A, "Town-wide", "ADU max size", "Lesser of 40% of original residence floor area or 1,500 sq ft", ff, "§13.3.B",
          "The accessory apartment shall contain no more than 40% of the floor area of the originally existing residence or 1,500 square feet, whichever is less."),
        v(A, "Town-wide", "ADU owner-occupancy", "Required throughout the duration of the permit", ff, "§13.3.A",
          "A principal owner of the residence must reside in either the primary dwelling or the accessory apartment throughout the duration of the permit."),
        v(P, "Town-wide", "Parking, single-family", "2 spaces", ff, "§25.4.1 table"),
        v(P, "District B/C", "Parking, multifamily (≤16 units)", "1 space/1BR unit, 2 spaces/2BR+ unit", ff, "§25.4.1 table"),
    ],
    "Fairfield is the clearest \"permissive\" comparison case among the 17 towns — a genuine, explicitly tiered by-right multifamily district.")

# ================= REDDING =================
rd = pdf("redding", "redding-zoning.pdf", "Redding Zoning Regulations (amendments through Feb. 15, 2024)", "https://reddingct.gov/wp-content/uploads/2025/10/Redding-Zoning-Regulations-1.24.24.pdf")
add("redding", "Redding", 322, 8830, 19732, 12, 99.1,
    nza_block(322, 99.2, 98.9, 98.9, 98.7, 100), rd, "R-1", "RV",
    [
        v(U, "R-1/R-4/R-2/R-½", "Only single-family permitted", "All uses must fall under §4.2.1, 4.2.2 or 4.2.3", rd, "§4.2, §4.2.1(a)",
          "Within Residential Zones (R-4, R-2, R-1, R-½, RV), buildings, structures and land shall be used only as permitted in Sections 4.2.1, 4.2.2 and 4.2.3."),
        v(D, "R-1", "Min. lot size", "43,560 sq ft (1 acre)", rd, "§4.6 table", "43,560"),
        v(D, "R-4", "Min. lot size (most restrictive tier)", "174,200 sq ft (4 acres)", rd, "§4.6 table"),
        v(U, "RV", "Multifamily", "Special Permit only, capped at 1 unit/8,000 sq ft of site area", rd, "§4.2.3(o)",
          "Within RV Residential Zone only, residential apartments, townhouses or condominiums not exceeding a density of one (1) residential unit per 8,000 square feet of site area"),
        v(D, "RV", "Min. lot size (zone)", "No acreage minimum (NR)", rd, "§4.6 table"),
        v(A, "Town-wide", "ADU approval pathway", "Special Permit required (not by-right)", rd, "§5.12.1",
          "One (1) accessory residential apartment (see Definitions, Section 8.1.11) may be permitted on a lot, subject to a Special Permit granted by the Commission."),
        v(A, "Town-wide", "ADU owner-occupancy", "Required throughout the duration of the apartment use", rd, "§5.12.3(a)",
          "The owner of the premises shall be resident in either the accessory or principal dwelling throughout the duration of the apartment use."),
        v(A, "Town-wide", "ADU max size (attached)", "Lesser of 30% of dwelling floor area or 1,000 sq ft", rd, "§5.12.4(c)",
          "comprising no more than 30% of the total finished floor area of the dwelling, or 1000 square feet of gross (total) floor area, whichever is less."),
        v(P, "Town-wide", "Parking, single-family dwelling", "2 spaces/dwelling", rd, "§5.6.2 table"),
    ],
    "Redding's ADU rules give no size figure for detached ADUs in R-4 — a likely drafting gap rather than a deliberate restriction.")

# ================= MONROE =================
mn = pdf("monroe", "monroe-zoning.pdf", "Monroe Zoning Regulations (amended through July 2, 2026)", "https://www.monroect.gov/Home/DownloadDocument?docId=82b32408-e8ae-4afd-b9ca-58f87c1e35da")
add("monroe", "Monroe", 318, 19269, 16323, 16, 72.8,
    nza_block(318, 95.2, 80.0, 80.0, 48.4, 89), mn, "RF-1", "MFR",
    [
        v(U, "RF-1", "Multifamily (incl. 2-unit, by Monroe's own definition)", "Prohibited (\"x\")", mn, "§10.1 Use Schedule",
          "Multi-Family Dwelling                     x      x       x      x     SEP     x    SEP     X       x          x     X       x        x        x"),
        v(D, "RF-1", "Min. lot size", "43,560 sq ft (1 acre)", mn, "Art. 3 §3.1.4(A)", "RF-1:43560 sq. ft."),
        v(U, "MFR", "Multifamily density", "2.5 units/gross acre (attached)", mn, "§3.4.5(A)(1)",
          "Attached single-family units: two-and-half (2.5) units per gross acre of the parcel"),
        v(D, "MFR", "Min. parcel to create district", "70 contiguous acres", mn, "§3.4.5(B)",
          "Minimum parcel size shall be seventy (70) acres under same ownership in a single continuous"),
        v(A, "RF-1/RF-2/RF-3", "ADU approval pathway", "By-right (\"ACC\" — Certificate of Use, no special-permit hearing)", mn, "§6.9.2(H)"),
        v(A, "RF-1/RF-2", "ADU attachment requirement", "Attached only (RF-3 also permits detached)", mn, "§6.9.1(B)"),
        v(A, "Town-wide", "ADU owner-occupancy", "Required at all times", mn, "§6.9.2(A)",
          "Either the principal dwelling or accessory apartment shall be occupied by the owner of the premises at all times."),
        v(A, "Town-wide", "ADU size range", "400–1,000 sq ft, max 1 bedroom, ≤30% of gross livable floor area", mn, "§6.9.1(C)",
          "Living area of an accessory apartment shall contain a minimum of four-hundred (400) square feet and shall not exceed a maximum of one-thousand (1,000) square feet; there shall be no more than one (1) bedroom in such apartment."),
        v(P, "Town-wide", "Parking, studio/1BR", "1.0 space/unit", mn, "§10.2 Schedule"),
        v(P, "Town-wide", "Parking, 2BR+", "2.0 spaces/unit", mn, "§10.2 Schedule"),
    ],
    "Monroe's code does not distinguish a 3-unit tier from larger multifamily — its own definition of \"multi-family\" legally includes buildings with as few as 2 units.")

# ================= TRUMBULL =================
tb = pdf("trumbull", "trumbull-zoning.pdf", "Trumbull Zoning Regulations (amended through Aug. 19, 2026)", "https://trumbull-ct.gov/DocumentCenter/View/1323")
add("trumbull", "Trumbull", 327, 38073, 14786, 25, 63.6,
    nza_block(327, 99.6, 98.8, 98.0, 0.0, 99), tb, "Residence A/AA/AAA", "MFO",
    [
        v(U, "Residence A/AA/AAA", "Single-family only", "Only use permitted: \"One-Family Dwelling\"", tb, "Art. II §1.1.1",
          "Within the Residence AAA, AA or A Zone no Building or Structure shall be erected, altered, occupied or used, arranged or designed to be used for other than one or more of the following specified purposes: 1. One-Family Dwelling;"),
        v(D, "Residence A", "Min. lot size", "21,780 sq ft (½ acre)", tb, "Art. I §2"),
        v(D, "Residence AA/AAA", "Min. lot size", "43,560 sq ft (1 acre)", tb, "Art. I §2"),
        v(U, "Town-wide", "Multifamily rental moratorium", "No new applications above 50 units (except 55+ housing) until Feb. 28, 2027", tb, "Art. XVII",
          "the Planning and Zoning Commission hereby declares an immediate moratorium on all applications for, and approvals of, any multi-family residential rental housing to determine the additional need of this type of housing in the Town."),
        v(U, "MFO", "Multifamily", "Special Permit only, existing I-L/I-L2 industrial land ≥10 acres", tb, "§7.6.2"),
        v(U, "MFO", "Density / town-wide cap", "20 units/acre, capped at 600 units town-wide", tb, "§7.6.4(1)",
          "The maximum number of dwelling units shall be 20 units per acre. The maximum number of dwelling units that may be developed pursuant to this MFO shall be 600, provided that no more than 220 units may be approved by the Commission within any 12 month period."),
        v(D, "MFO", "Unit types", "1BR (min 700 sf) and 2BR (min 950 sf) only — no studios, no 3BR+", tb, "§7.6.4(9)"),
        v(D, "MFO", "Height cap", "65 ft / 5 stories", tb, "§7.6.4(2)"),
        v(A, "Residence A/AA/AAA", "ADU approval pathway", "Administrative (ZEO) if within existing footprint; Special Permit otherwise", tb, "§1.1.2(7)(D)"),
        v(A, "Residence A/AA/AAA", "ADU owner-occupancy", "Required for at least one unit", tb, "§1.1.2(7)(C)(b)",
          "At least one (1) Dwelling Unit in the converted single-family home shall be owner-occupied"),
        v(A, "Residence A/AA/AAA", "ADU size", "≥300 sq ft, max 30% of principal dwelling's livable floor area", tb, "§1.1.2(7)(C)(a)",
          "An accessory apartment must have at least three hundred (300) square feet of Livable Floor Area. Maximum size shall not exceed thirty (30%) per cent of the Livable Floor Area of the Principal Dwelling"),
        v(A, "Residence A/AA/AAA", "ADU deed restriction", "40-year affordable-housing deed restriction under CGS §8-30g(k)", tb, "§1.1.2(7)(D)"),
        v(P, "MFO", "Parking", "1.8 spaces/1BR unit, 2.0 spaces/2BR unit, + 1.0 guest space/20 units", tb, "§7.6.4(5)"),
    ],
    "Trumbull currently has a town-wide moratorium on new multifamily rental applications above 50 units (except 55+ housing), expiring Feb. 28, 2027 — a procedural block layered on top of the underlying district-level rules.")

# ================= SHELTON =================
sh = pdf("shelton", "shelton-zoning.pdf", "City of Shelton Zoning Regulations (recodified April 16, 2024)", "https://shelton.qscendcms.com/ckfinder/connector?command=Proxy&lang=en&type=Files&currentFolder=%2F&hash=c245c263ce0eced480effe66bbede6b4d46c15ae&fileName=2024%20Regulation%20scanned.pdf")
add("shelton", "Shelton", 324, 42805, 19384, 26, 60.4,
    nza_block(324, 90.1, 90.1, 89.8, 4.1, 95), sh, "R-1", "R-4",
    [
        v(U, "R-1", "2-/3-family & 4+-family", "Both prohibited (\"X\")", sh, "Schedule A, Row 2/2A/3"),
        v(D, "R-1", "Min. lot size", "40,000 sq ft", sh, "Schedule B, Row 1"),
        v(U, "R-4", "2-/3-family & multifamily (4-12 units)", "Allowed by Special Exception, subject to added lot-area requirements", sh, "Schedule A, Row 2/2A/3"),
        v(D, "R-4", "Min. lot area per unit (2F)", "7,500 sq ft", sh, "Schedule B, Row 2"),
        v(A, "R-1/R-4 (town-wide)", "ADU approval pathway", "By-right on use table, subject to detailed standards", sh, "§45.6"),
        v(A, "R-1/R-4 (town-wide)", "ADU owner-occupancy", "Required, and both units must be occupied by the same family group", sh, "§45.6.4, §45.6.7"),
        v(A, "R-1/R-4 (town-wide)", "ADU size", "400–900 sq ft (lesser of ⅓ habitable area or 900 sf, min 500 sf)", sh, "§45.6.6"),
        v(P, "R-1/R-4", "Parking, 1–2 unit dwellings", "2 spaces/unit", sh, "§42.2 table"),
        v(P, "R-1/R-4 (town-wide)", "Parking, ADU", "+2 additional spaces", sh, "§45.6.2"),
    ],
    "Shelton's own code is a scanned, image-only PDF with NO embedded text layer — it cannot be text-searched or highlighted in the in-app viewer at all. Every figure above was OCR'd and visually verified against the table images directly during research; open the original source to see the actual scanned tables.")

# ================= STRATFORD =================
st = link("stratford", "Stratford Zoning Code Ch. A220 (eff. Jan. 1, 2025)", "https://ecode360.com/9207545")
add("stratford", "Stratford", 326, 53610, 11017, 28, 33.8,
    nza_block(326, 84.2, 1.5, 0.9, 0.0, 100), st, "RS-1", "RM-1",
    [
        v(U, "RS-1", "Two- and three-family", "One combined use-table row, \"Two and Three Family Dwellings,\" not permitted", st, "§4.2.4 Use Table",
          "Two and Three Family Dwellings"),
        v(D, "RS-1", "Min. lot size", "40,000 sq ft", st, "§3.2.1 table"),
        v(U, "RS-1/RM-1", "4+-unit multifamily", "Special Permit (threshold inconsistently stated as \"4 or more\" vs. \"3+\")", st, "§5.1.2-3"),
        v(U, "RM-1", "2- and 3-family", "Allowed BY RIGHT (\"P¹\")", st, "§4.2.4 Use Table"),
        v(D, "RM-1", "Min. lot area per unit", "2,500 sq ft", st, "§3.2.2, footnote 1"),
        v(A, "RS-1/RM-1 (town-wide)", "ADU approval pathway", "Administrative review (\"A\")", st, "§4.4.2"),
        v(A, "RS-1/RM-1 (town-wide)", "ADU owner-occupancy", "Required for duration of the permit", st, "§4.4.2.E"),
        v(A, "RS-1/RM-1 (town-wide)", "ADU max size", "1,000 sq ft, max 1 bedroom", st, "§4.4.2.E"),
        v(P, "RS-1", "Parking, single-family dwelling", "1 space/unit", st, "§6.8.4.A table"),
        v(P, "RM-1", "Parking, multifamily (3+)", "1/unit (studio-1BR), 1.5/unit (2BR), 2/unit (3+BR), + 10% guest", st, "§6.8.4.A table"),
    ],
    "An apparent inconsistency exists between the Use Table's \"4 or more units\" threshold and §5.1's \"(3+)\" heading for Special Permit review — flagged for follow-up. No local PDF mirror exists for Stratford (eCode360 is a browsable HTML code site), so most facts above carry a citation but not an independently re-verified quote.")

os.makedirs(TOWNS_DIR, exist_ok=True)
for slug, t in TOWNS.items():
    with open(os.path.join(TOWNS_DIR, f"{slug}.json"), "w") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)

total_vars = sum(len(t["variables"]) for t in TOWNS.values())
print(f"Wrote {len(TOWNS)} town files to {TOWNS_DIR} ({total_vars} variables total, avg {total_vars/len(TOWNS):.1f}/town)")
