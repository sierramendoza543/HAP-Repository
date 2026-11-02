#!/usr/bin/env python3
"""Builds /data/towns/*.json from research findings.
Each variable carries a citation: {source, cite, quote}. `quote` is verbatim
text independently verified against the source document's own extracted
text (via pdftotext on the mirrored PDF). Where we don't have a confirmed
verbatim match, quote is None -- the UI then says so plainly instead of
highlighting the wrong thing."""
import json, os, re

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
OA = "Overlays & Affordability"

# ================= GREENWICH =================
gw9 = pdf("greenwich", "greenwich-div9.pdf", "Building Zone Regulations, Div. 9 (Use Regs, Aug. 2023)", "https://www.greenwichct.gov/DocumentCenter/View/37828")
gw21 = pdf("greenwich21", "greenwich-div21.pdf", "Building Zone Regulations, Div. 21 (Bulk Schedule)", "https://www.greenwichct.gov/DocumentCenter/View/37841")
add("greenwich", "Greenwich", 317, 64594, 30322, 49, 86.4,
    nza_block(317, 96.0, 97.9, 98.5, 65.0, 100), gw9, "R-20 / RA-2", "R-MF",
    [
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "Single-family", "Allowed by-right — only permitted use", gw9, "§6-93(a)(1)",
          "The following principal uses are permitted in RA-4, RA-2, RA-1, R-20 and R-12 Zones and all other principal uses are expressly excluded: (1) Detached single family dwellings, one (1) per lot."),
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "Two-family", "Prohibited — same exhaustive-use-list basis", gw9, "§6-93 / 6-94",
          "all other principal uses are expressly excluded"),
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "Three-family", "Prohibited — same exhaustive-use-list basis", gw9, "§6-93 / 6-94",
          "all other principal uses are expressly excluded"),
        v(U, "R-20/RA-2/RA-4/RA-1/R-12", "4+-family", "Prohibited — same exhaustive-use-list basis", gw9, "§6-93 / 6-94",
          "all other principal uses are expressly excluded"),
        v(D, "R-20", "Min. lot size", "20,000 sq ft", gw21, "§6-205(a) table", "20,000"),
        v(D, "RA-2", "Min. lot size", "2 acres (87,120 sq ft)", gw21, "§6-205(a) table", "2 Acres"),
        v(D, "RA-4", "Min. lot size", "4 acres (174,200 sq ft)", gw21, "§6-205(a) table", "4 Acres"),
        v(D, "R-12", "Min. lot size", "12,000 sq ft", gw21, "§6-205(a) table", "12,000"),
        v(D, "R-20", "Max. height", "2.5 stories / 37½ ft", gw21, "§6-205(a) table"),
        v(D, "R-20", "Floor Area Ratio (F.A.R.)", "0.225", gw21, "§6-205(a) table", ".225"),
        v(D, "R-20", "Min. front / side / rear yard", "40 ft / 10 ft / 40 ft", gw21, "§6-205(a) table"),
        v(D, "R-MF", "Max. height (multifamily tier)", "4 stories / 40 ft", gw21, "§6-205(a) table",
          "4             40 ft.              2,400"),
        v(D, "R-MF", "Min. front / side / rear yard (multifamily tier)", "50 ft / 5 ft / 50 ft", gw21, "§6-205(a) table",
          "50 ft.                  50 ft.               50 ft."),
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
        v(OA, "R-PHD-SU zone only", "Min. unit size", "450 sq ft (efficiency) / 650 sq ft (1BR) / 850 sq ft (2BR)",
          link("greenwich-div6", "Div. 6, Residential-Planned Housing Design-Small Unit Zone", "https://www.greenwichct.gov/DocumentCenter/View/37825/10-PZ-Regs-Division-6-amended-4-24-2013"),
          "§6-64(c)",
          "1 Room-Efficiency 450 sq. ft. ... 1 Bedroom Unit 650 sq. ft. ... 2 Bedroom Unit 850 sq. ft."),
        v(OA, "Business zones only (incentive, not mandate)", "Inclusionary zoning", "≥20% of units must be BMR, opt-in density/FAR bonus",
          link("greenwich-6110", "§6-110, Dwelling Units and BMR Units in Business Zones (eff. 5/6/26)", "https://www.greenwichct.gov/DocumentCenter/View/55728/Adopted-BZR-Amendment-Section-6-110-DUs-and-BMR-DUs-in-Business-Zones-5626"),
          "§6-110(b)",
          "At least 20% of the total number of units must be BMR Units, divided equally between MID Units and AH Units."),
        v(OA, "Town-wide (opt-in, parcel-specific)", "Historic overlay", "Voluntary HO zone via zoning map amendment, not a mapped district",
          link("greenwich-6109", "§6-109, Historic Overlay Zone (eff. 11/25/25)", "https://www.greenwichct.gov/DocumentCenter/View/52849/Adopted-BZR-Amendment-Section-6-109-Historic-Overlay-Final-Version"),
          "§6-109",
          "The designation of an HO zone requires approval of a zoning map amendment from the Planning and Zoning Commission."),
        v(OA, "Town-wide", "Demolition delay", "Up to 90 days (45 + 45 if an objection is filed)",
          link("greenwich-demo", "Town of Greenwich, Historic Demolition Delay", "https://www.greenwichct.gov/2865/Historic-Demolition-Delay"),
          "Town permitting page (codified ordinance section not located)",
          "is subject to a 45 minimum day waiting period"),
        v(OA, "Coastal Overlay Zone", "Coastal/flood overlay", "Applies — Long Island Sound frontage, CT Coastal Management Act review",
          link("greenwich-6111", "§6-111, Coastal Overlay Zone (draft 6/29/26)", "https://www.greenwichct.gov/DocumentCenter/View/57617/DRAFT-Proposed-Amendment-to-Section-6-111-Coastal-Overlay-Zone-and-related-amendments-to-Sections-6-13-6-22-and-6-181-62926"),
          "§6-111",
          "A Coastal Overlay Zone is hereby established in accordance with the authorization of Sections 22a-90 to 22a-96 of the General Statutes"),
    ],
    "Town adopted 2025–2026 amendments (nursing-home conversions, multifamily parking per PA 25-1) not fully reflected in the Aug. 2023 PDF — verify against the amendment list before external use. The parking table (Div. 15, §6-155) was cited from the original research pass but is not locally mirrored for quote verification.")

# ================= BRIDGEPORT =================
bp = pdf("bridgeport", "bridgeport-zoning.pdf", "\"Zone Bridgeport\" form-based code (amended July 2022)", "https://portal.ct.gov/-/media/CSC/1_Dockets-medialibrary/1_MEDIA_DO500_600/DO516/ApplicantSubmissions/Application/UI---City-of-Bridgeport-Zoning-Code-Amended-July-25-2022.pdf")
add("bridgeport", "Bridgeport", 311, 151599, 10246, 25, 15.5,
    nza_block(311, 31.5, 39.3, 37.9, 0.0, 0), bp, "N1", "NX2",
    [
        v(U, "N1", "Single-family (House A)", "1 in House — no 2-unit option exists", bp, "§3.90.9",
          "Number of Principal Units: 1 in House"),
        v(U, "N1", "ADU", "1 in House or Backyard Cottage — allowed by-right", bp, "§3.90.9",
          "1 in House or Backyard Cottage"),
        v(D, "N1", "Min. lot width", "45 ft (no lot area minimum)", bp, "§3.90.4", "Lot Width: 45 ft. min."),
        v(D, "N1", "Height (House A)", "1.5 stories min. / 2.5 stories max.", bp, "§3.90.6",
          "1.5 stories min.    2 stories min.     2 stories min."),
        v(U, "NX2", "Up to 4 units (House A)", "By-right, no special permit, + 1 backyard cottage", bp, "§3.90.9",
          "up to 4 in House plus 1 in Backyard Cottage"),
        v(U, "NX2", "Double House A", "Up to 6 by-right, 8 with special permit, + 1 backyard cottage", bp, "§3.80.9",
          "up to 6, 8 with special permit in House;"),
        v(U, "NX2", "Small General building type", "3 min., 6 max., up to 8 units with special permit", bp, "§3.60.9",
          "3 min., 6 max.,"),
        v(D, "NX2", "Min. lot width (House A)", "35 ft", bp, "§3.90.4", "35 ft. min."),
        v(AP, "NX2", "4+-unit approval pathway", "By-right up to 4 units (House A) or 6 units (Double House A/Small General); Special Permit above that", bp, "§3.90.9 / §3.80.9 / §3.60.9"),
        v(P, "Town-wide", "Parking minimum", "None — citywide", bp, "§8.20.1",
          "This zoning code does not establish minimum off-street parking requirements"),
        v(OA, "Town-wide", "Min. unit size", "Not found — no town-wide minimum dwelling-unit floor area in the zoning code", bp, "full-text search of definitions (§15865)"),
        v(OA, "Town-wide", "Inclusionary zoning", "None found — no inclusionary set-aside ordinance in the zoning code (notable outlier among CT-4 towns)", bp, "full-text search, §4.70 Accessory Uses reviewed"),
        v(OA, "OH zone (tied to Ch. 12.32 local historic districts)", "Historic overlay", "Requires Certificate of Appropriateness for alteration/demolition within OH zone", bp, "§2.50.3",
          "a building or structure located within an OH zone may not be erected, altered, demolished, or removed and no area within an OH zone may be used for industrial, commercial, business, home industry or occupational parking until a certificate of appropriateness has been issued for such activity by the historic district commission."),
        v(OA, "Town-wide", "Demolition delay", "Up to 90 days for qualifying structures, referred to City Historian",
          link("bridgeport-demo", "City of Bridgeport, Demolition Delay Determination of Applicability form", "https://bridgeportct.gov/sites/default/files/2023-03/Bldg_20230301_Demolition_Delay_Form.pdf"),
          "Municipal Code Ch. 15-36 §15.26.020 (via city form)",
          "This property is subject to Demolition Delay Ordinance and is referred to City Historian for further action."),
        v(OA, "Coastal Site Plan review (§11.80)", "Coastal/flood overlay", "Applies — Long Island Sound frontage, CT Coastal Management Act review", bp, "§11.80.1-2",
          "Coastal site plan review and approval is required for all non-exempt activities and projects on sites located wholly or partially within the"),
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
          "R-20          20000   100   100   20000     1"),
        v(D, "R-20", "Max. height", "2.5 stories / 30 ft", sf, "Table II, Appendix B",
          "30           15         40     65      15      35         50"),
        v(D, "R-20", "Min. front / side / rear yard", "40 ft / 15 ft / 50 ft", sf, "Table II, Appendix B",
          "30           15         40     65      15      35         50"),
        v(D, "R-20", "Max. building coverage", "15% of lot", sf, "Table II, Appendix B",
          "30           15         40     65      15      35         50"),
        v(U, "R-6", "District definition", "One-Family, Two-Family Residence District", sf, "Table I; §1-2",
          "R-6               One-Family, Two-Family Residence District"),
        v(U, "R-6", "Two-family", "Allowed by-right", sf, "Table I"),
        v(U, "R-6", "Multifamily (3+)", "Still prohibited", sf, "Table I"),
        v(D, "R-6", "Min. lot size", "5,000 sq ft (1F) / 6,000 sq ft (2F)", sf, "Table II, Appendix B",
          "R-6           5000     50      -              -      1(19)"),
        v(D, "R-6", "Max. height", "2.5 stories / 30 ft", sf, "Table II, Appendix B",
          "30           25         25     50       6      12         30"),
        v(D, "R-6", "Min. front / side / rear yard", "25 ft / 6 ft (one) 12 ft (both) / 30 ft", sf, "Table II, Appendix B",
          "30           25         25     50       6      12         30"),
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
        v(OA, "C-G/C-C mixed-use", "Min. unit size", "Min. 500 sq ft of lot area per unit (400 sq ft by Special Permit) — a lot-area, not floor-area, minimum", sf, "Zoning Regs (section number unconfirmed — live site blocked automated access)"),
        v(OA, "Town-wide (varies by district)", "Inclusionary zoning", "Reported 3–12% set-aside depending on district; a 2024 proposal to raise this is unconfirmed as adopted", sf, "§7 (formerly §7.4), BMR Regulations — live site blocked automated access, secondary-sourced"),
        v(OA, "Cultural Resources Inventory (CRI) model, not a mapped district", "Historic overlay", "Listed buildings get zoning relief in exchange for facade preservation, administered by HPAC", sf, "§7.3 — secondary-sourced, live site blocked"),
        v(OA, "Town-wide", "Demolition delay", "Chapter 88; notice-to-deadline gaps of roughly 20–21 days observed in published legal notices, exact statutory period unconfirmed", sf, "Code of Ordinances Ch. 88 — not independently retrieved"),
        v(OA, "Coastal Area Management provisions", "Coastal/flood overlay", "Applies — Long Island Sound frontage; a proposed Coastal Resilience Overlay (CRO) Zone requiring +3 ft above base flood elevation is reported but adoption status unconfirmed", sf, "Stamford Master Plan Coastal Addendum (1984) / CCMA — secondary-sourced"),
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
        v(D, "CD-1S", "Max. height", "2.5 stories / 40 ft to peak", nwb, "Bulk & Height Schedule (7/9/2025)"),
        v(D, "CD-1S", "Min. front / side / rear yard", "30 ft / 6 ft / 15 ft", nwb, "Bulk & Height Schedule (7/9/2025)",
          "CD-1S        6,250         N/R                         50 ft. min.                         32 ft. to midpoint max.               See Below1                                                                     6 ft. min.                       15 ft. min."),
        v(A, "CD-1S", "ADU", "Permitted by-right with limitations", nw3, "Table 4.3.9.A, §4.3.4.C.3.a"),
        v(U, "CD-2", "Two-family", "\"P\" — permitted by right; multifamily still \"NP\"", nw3, "Table 4.3.9.A"),
        v(D, "CD-2", "Min. lot size", "5,000 sq ft", nwb, "Bulk & Height Schedule (7/9/2025)", "CD-2         5,000"),
        v(D, "CD-2", "Max. height", "2.5 stories / 40 ft to peak", nwb, "Bulk & Height Schedule (7/9/2025)"),
        v(D, "CD-2", "Min. front / side / rear yard", "30 ft / 5 ft / 15 ft", nwb, "Bulk & Height Schedule (7/9/2025)",
          "CD-2         5,000         N/R                         50 ft. min.                         32 ft. to midpoint max.               See Below1                                                                     5 ft. min.                       15 ft. min."),
        v(A, "CD-1S/CD-2", "ADU max size", "1,000 sq ft", nw3, "§4.3.4.C.3.a"),
        v(A, "CD-1S/CD-2", "ADU eligibility", "Must be on a lot with a Single-Family Detached Dwelling; 1 per lot, owner must reside on lot", nw3, "§4.3.4.C.3.a"),
        v(P, "CD-1S/CD-2", "Parking minimum", "Not regulated for buildings of ≤16 units, except in Traffic Mitigation Districts", nw3, "Table 4.3.12.B-1"),
        v(OA, "Town-wide", "Min. unit size", "No zoning-code minimum found; Housing Code (Ch. 59, not zoning) governs habitable room sizes separately",
          link("norwalk-ch59", "Norwalk Code of Ordinances, Chapter 59 (Housing Code)", "https://ecode360.com/27049991"),
          "§59-7 (not independently verified)"),
        v(OA, "CBD, SSDD, and ~16 other named zones", "Inclusionary zoning (\"Workforce Housing\")", "10% of units in developments of ≥20 units (≥12 units in CBD/SSDD); up to 20–30% density bonus available",
          link("norwalk-workforce", "§118-1050, Workforce housing regulation (through 6/13/2019)", "https://ecode360.com/26974593"),
          "§118-1050(2)",
          "Developments of twenty (20) or more dwelling units shall designate a minimum of ten percent (10%) of the total number of units, rounded up to the nearest whole number, as workforce housing units"),
        v(OA, "Norwalk Green Historic District only (not a citywide overlay)", "Historic overlay", "One small mapped district; certificate of appropriateness required for alteration/demolition within it",
          link("norwalk-ch56", "Norwalk Code of Ordinances, Chapter 56 (Historic District)", "https://ecode360.com/27049799"),
          "§56-4.B",
          "No building permit for erection of a building or structure or for alteration of an exterior architectural feature within an historic district and no demolition permit for demolition or removal of a building or structure within an historic district shall be issued"),
        v(OA, "Town-wide", "Demolition delay", "Up to 120 days (2023 rewrite raised the ceiling from the 90-day state default); 90 days specifically within the Norwalk Green Historic District",
          link("norwalk-ch55", "Norwalk Code of Ordinances, Chapter 55 (Demolition Delay, amended 3/28/2023)", "https://ecode360.com/27049778"),
          "§55-5.F",
          "In no event shall the issuance of a Demolition permit be delayed for more than 120 days from the date the application is deemed filed."),
        v(OA, "Flood Hazard Zone (§118-1100) + Coastal Zone (§118-1110)", "Coastal/flood overlay", "Applies — Long Island Sound frontage; detailed elevation and anchoring standards, public hearing required for larger multifamily near mean high water",
          link("norwalk-coastal", "§118-1110, Coastal Zone (added 2/29/1980)", "https://ecode360.com/26974685"),
          "§118-1110(2)",
          "The purpose of this section is to implement the State Coastal Management Act, Chapter 444 of the Connecticut General Statutes."),
    ],
    "CD-3/CD-4 allow multifamily by-right-with-limitations, but column alignment for CD-3W/CD-4W sub-variants was ambiguous in the extracted PDF text — not reported to avoid miscitation. The use-permission table (Table 4.3.9.A) and ADU standards (§4.3.4) weren't in the PDFs mirrored locally, so those rows above carry a citation but not an independently re-verified quote.")

# ================= DARIEN =================
dn = pdf("darien", "darien-zoning.pdf", "Darien Zoning Regulations (last revised May 10, 2026)", "https://www.darienct.gov/DocumentCenter/View/6613")
add("darien", "Darien", 302, 22528, None, 26, 74.5,
    nza_block(302, 97.0, 97.0, 97.0, 32.4, 100), dn, "R-1", "DMR",
    [
        v(U, "R-1/R-2/R-1½/R-1⅓/R-1⅕", "Only single-family permitted", "2-/3-/4+-family prohibited town-wide", dn, "§402.a",
          "a single, detached one-family dwelling on its own lot"),
        v(D, "R-1", "Min. lot size", "43,560 sq ft (1 acre)", dn, "§406",
          "Minimum Lot Area                                  1 acre (43,560 sq. ft.)"),
        v(D, "R-2", "Min. lot size", "87,120 sq ft (2 acres)", dn, "§406",
          "Minimum Lot Area                              2 acres (87,120 sq. ft.)"),
        v(U, "DMR", "Multifamily", "Special Permit only", dn, "§524.a",
          "524.   Principal Uses Requiring Special Permits"),
        v(D, "DMR", "Min. lot size (zone)", "3 acres (130,680 sq ft)", dn, "§525",
          "Minimum Lot Area                                 3 acres (130,680 sq. ft.)"),
        v(U, "DMR", "Density", "4 DU/net acre by-right (6 with 20% affordable)", dn, "§526.1a-b",
          "Four (4) Dwelling Units/Net Acre"),
        v(U, "DMR", "Bedroom mix requirement", "≥15% of units must be 1BR; no unit may exceed 3BR", dn, "§526.3a",
          "At least 15 percent of the total number of units shall be limited to one bedroom. No unit shall contain more than three bedrooms."),
        v(A, "Town-wide", "ADU max size", "700 sq ft attached / 1,000 sq ft detached, and <30% of combined floor area", dn, "§407.c.1",
          "700 square feet if it is part of or attached to the principal dwelling unit"),
        v(A, "Town-wide", "ADU owner-occupancy", "Required (annual affidavit)", dn, "§407.c.9",
          "The property is to be owner occupied, meaning that the record owner of the property must reside in either the principal dwelling or the accessory dwelling unit."),
        v(A, "Town-wide", "ADU program sunset", "Expires for new applications after June 30, 2029 unless readopted", dn, "§407.c.16",
          "The provisions of Subsections 403n. and 407c shall remain valid for five (5) years"),
        v(P, "R-1/R-2", "Parking, one-/two-family residences", "2 spaces/unit", dn, "§904.a",
          "One and two-family residences            2 spaces for each family unit."),
        v(OA, "Elderly/BMR housing only", "Min. unit size", "≥800 sq ft per elderly BMR unit; no general town-wide minimum found", dn, "§438",
          "Each elderly below market-rate housing unit required to be constructed or acquired shall be at least 800 square feet in size"),
        v(OA, "All zones allowing dwelling units", "Inclusionary zoning", "14% of units must be affordable (≤80% SMI) in developments of ≥4 units; deed-restricted 40 years", dn, "§580, 583",
          "Developments resulting in the creation of four or more multi-family dwelling units shall designate a minimum of fourteen percent (14%) of the total number of dwelling units as affordable housing"),
        v(OA, "Opt-in \"Protected Town Landmark\" (not a mapped district)", "Historic overlay", "Voluntary, parcel-specific special-permit tool, similar structure to Greenwich's HO zone", dn, "§1051.1-2",
          "certain structures and land areas have value as Town Landmarks, which value transcends the ordinary standards incorporated in these Regulations"),
        v(OA, "Town-wide", "Demolition delay", "Likely exists (observed 21–30-day objection windows in a tracked case) but codified text and exact delay period not located", dn, "Code of Ordinances — not independently retrieved"),
        v(OA, "Coastal Area Management, §810", "Coastal/flood overlay", "Applies — Long Island Sound frontage, CT Coastal Management Act review", dn, "§811, 813",
          "The purpose of this Section is to achieve the goals, objectives and policies of the State-wide Coastal Area Management Program as set forth in Chapter 444 Section 22a-90 through 22a-112 of the General Statutes"),
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
        v(D, "Four Acre Residence Zone", "Max. principal building height", "40 ft", nc, "§3.5.F.1 table",
          "Four Acre Residence Zone                    40           20             45           30"),
        v(D, "Four Acre Residence Zone", "Min. front / side / rear yard", "50 ft / 50 ft / 50 ft", nc, "§3.4.D.2 table",
          "Four Acre Residence Zone                50        50          50             50"),
        v(U, "B Residence Zone", "Two-family", "Special Permit only", nc, "§3.2.C.1",
          "a two-family dwelling in the B Residence Zone per Section 3.2.C.1."),
        v(D, "B Residence Zone", "Min. lot size", "7,500 sq ft", nc, "§3.5.A.1 table",
          "B Residence Zone                                                     7,500"),
        v(D, "B Residence Zone", "Max. principal building height", "30 ft", nc, "§3.5.F.1 table",
          "B Residence Zone                            30           15             35           20"),
        v(U, "Apartment Zone", "Two-family & multifamily", "Both Special Permit only", nc, "§5.4.C.1-2"),
        v(D, "Apartment Zone", "Max density", "1 unit / 5,000 sq ft", nc, "§5.4.D.1"),
        v(A, "Town-wide", "ADU max size", "1,000 sq ft or 40% of combined floor area, whichever less", nc, "§3.3.B.6",
          "not exceed 1,000 square feet or 40% of the combined floor areas of the single-family dwelling and the accessory dwelling unit"),
        v(A, "Town-wide", "ADU owner-occupancy", "Required", nc, "§3.3.B.6",
          "the owner of the property shall occupy either the principal dwelling unit or the accessory dwelling unit"),
        v(P, "Town-wide", "Parking, single-family", "2 spaces", nc, "§6.2.C table"),
        v(P, "B Residence Zone", "Parking, two-family", "2 spaces/unit (4 total)", nc, "§6.2.C table"),
        v(OA, "Multi-family/elderly special-permit housing", "Min. unit size", "750 sq ft minimum gross floor area/unit (1.5-story type), excluding basement/attic/garage", nc, "zoning regs (specific housing type, not confirmed town-wide)",
          "Minimum gross floor area per unit 750 square feet excluding basements, attic space and garage space"),
        v(OA, "Multi-Family Zone, Apartment Zone, Business Zones (≥5 units, public water/sewer)", "Inclusionary zoning", "15% of units must be affordable (≤80% median income), deed-restricted 40 years", nc, "§7.6.C.3.a",
          "Where a project results in the creation of at least five (5) dwelling units, fifteen percent (15%) of the units must be provided as affordable housing, at or below eighty percent (80%) median income, and deed restricted for a minimum of forty (40) years"),
        v(OA, "One mapped district (≈ 21 buildings around God's Acre)", "Historic overlay", "Historic District Commission controls exterior appearance only, not zoning/density/use",
          link("newcanaan-ch31", "New Canaan Code of Ordinances, Ch. 31 (Historic District, adopted 1963)", "https://ecode360.com/9044801"),
          "§31-5",
          "No powers of the New Canaan Town Planning and Zoning Commission and the New Canaan Zoning Board of Appeals having to do with the use of land within the Historic District shall be impaired by this ordinance."),
        v(OA, "Town-wide", "Demolition delay", "Up to 90 days for structures >50 years old and ≥500 sq ft",
          link("newcanaan-ch12a", "New Canaan Code of Ordinances, Ch. 12A (Demolition, adopted 2006)", "https://ecode360.com/9044207"),
          "§12A-1",
          "The purpose of this ordinance is to authorize the Town of New Canaan, as allowed by § 29-406(b) of the Connecticut General Statutes, to impose a waiting period of not more than 90 days before granting a demolition permit"),
        v(OA, "None — inland town", "Coastal/flood overlay", "No coastal boundary; has only a thin, notice-only Floodplain Overlay Zone", nc, "§5.5",
          "The Floodplain Overlay Zone is intended to provide reasonable notice regarding property that may be subject to the effects of flooding."),
    ],
    "No as-of-right multifamily district exists anywhere in New Canaan — every multi-unit pathway requires a discretionary Special Permit hearing.")

# ================= WESTPORT =================
wp = link("westport", "Westport Zoning Regulations (eff. April 12, 2024)", "https://online.encodeplus.com/regs/westport-ct/")
add("westport", "Westport", 329, 27996, None, 40, 35.2,
    nza_block(329, 0.6, 0.3, 0.2, 38.0, 100), wp, "Residence AAA", "Residence C",
    [
        v(U, "Residence AAA", "Two-family / multifamily", "Prohibited as normal use", wp, "§11-2",
          "In an AAA Residence District, no land, building, or structure shall be used, and no building shall be hereafter erected, altered, or added to, unless otherwise provided in these regulations except for one (1) or more of the following uses: 11-2.1 Principal Uses 11-2.1.1One (1) single-family dwelling per lot."),
        v(D, "Residence AAA", "Min. lot size", "2 acres", wp, "§11-3",
          "Each lot shall have a minimum area of two (2) acres (87,120 square feet) and shall be of such shape that a square with two hundred (200) feet on each side will fit on the lot."),
        v(U, "Residence C", "Two-family", "Allowed BY RIGHT as a principal use", wp, "§18-2.1.2",
          "18-2.1.1 Any use permitted in a Residence AAA District, as specified in §11-2.1, herein. 18-2.1.2Two-family dwellings."),
        v(D, "Residence C", "Min. lot size", "5,000 sq ft", wp, "§18-3",
          "Each lot within a Res. C shall have a minimum area of 5,000 square feet, a minimum depth of 75 ft., a minimum width of 50 ft. and a minimum frontage of 50 ft. on a public street."),
        v(D, "Residence C", "Max density", "10 units/gross acre", wp, "§18-4.1",
          "The maximum unit density shall not exceed one dwelling unit for each 4,350 square feet of gross lot area. The total number of dwelling units shall not exceed a density of 10.0 units per gross acre."),
        v(D, "Residence C", "Town-wide aggregate cap", "120 total dwelling units under this zone", wp, "§18-4.2",
          "The total aggregate number of dwelling units permitted on all Res. C lots within the Town of Westport shall not exceed 120 cumulative dwelling units under these Res. C regulations."),
        v(U, "Residence C", "Affordability requirement", "≥15% of market-rate units workforce/affordable (or 17.5% fee-in-lieu)", wp, "§18-17.1",
          "A minimum of fifteen percent (15%) of the total number of market rate dwelling units shall be designated as workforce or affordable housing"),
        v(A, "Residence AAA", "ADU max size (structural, no owner-occ.)", "850 sq ft (≤1.5 ac) / 1,000 sq ft (>1.5 ac)", wp, "§11-2.4.8A",
          "Lots up to and including 1½ acres (0-65,340 sq. ft.) 850 sq. ft. Lots over 1½ acres (65,340 sq. ft. or greater) 1,000 sq. ft."),
        v(A, "Residence AAA", "ADU max size (internal apartment, owner-occ. req.)", "1,500 sq ft or 25% of total floor area, whichever smaller", wp, "§11-2.4.12A",
          "The additional dwelling unit shall not exceed 1500 square feet of floor area or 25% of the total floor area in the dwelling, whichever is smaller."),
        v(A, "Residence C", "ADU availability", "Excluded — §11-2.4.12 accessory apartment provision not carried over", wp, "§18-2.2.1",
          "Any Special Permit use allowed in a Residence AAA District, as specified in §11-2.2 & 11-2.3 herein, except §11-2.4.12 (Accessory Apartment) and §11-2.4.5 (Leasing of Rooms) is not allowed."),
        v(P, "Town-wide", "Parking, developments ≤16 units", "No minimum (2026 amendment, §34-14.1), except in a Conservation & Traffic Mitigation District", wp, "§34-14.1",
          "A development with sixteen (16) or fewer dwelling units does not need to provide a minimum number of off-street parking spaces unless such development is located in a Conservation and Traffic Mitigation District (CTMD)."),
        v(OA, "Town-wide", "Min. unit size", "Not found as a minimum; only caps located (e.g. ADU ≤800 sq ft, GBD units averaging ≤2,100 sq ft)", wp, "full-text search, not completed within research budget"),
        v(OA, "IHZ (split-zoned lots ≥3 ac.) + R-AHZ/W district", "Inclusionary zoning", "IHZ: ≥20% of floor area deed-restricted affordable. R-AHZ/W: reported 30% affordable/workforce split", wp, "§39A-18.1 (IHZ); R-AHZ/W section unconfirmed",
          "In conjunction with residential units proposed as part of this regulation, at least twenty percent (20%) of the floor area of all residential units shall be deed restricted as affordable"),
        v(OA, "§39 (non-res.), §30 (Historic Design District), §36 (Village District, 2017)", "Historic overlay", "Multi-layered system — the most elaborate of the CT-4 towns researched; section text not independently re-verified", wp, "§39, §30, §36 — secondary-sourced"),
        v(OA, "Town-wide", "Demolition delay", "180 days for structures ≥50 years old and ≥500 sq ft (raised from 90 days in 2008)",
          link("westport-demo", "Town of Westport, Demolition Delay Ordinance", "https://www.westportct.gov/government/appointed-boards-a-z/historic-district-commission/demolition-delay-ordinance"),
          "§14-21",
          "The Town of Westport has a demolition delay ordinance, §14-21, that provides a 180 day waiting period following the filing of a demolition permit application for buildings 500 sq. ft. or larger and 50 years or older."),
        v(OA, "Coastal Area Management, §31-10", "Coastal/flood overlay", "Applies — Long Island Sound frontage; ~3,100 properties in the 100-year flood zone per town staff reports", wp, "§31-10, §31-11 — secondary-sourced"),
    ],
    "A 2026 amendment (§34-14.1) eliminated minimum parking entirely for residential developments of 16 units or fewer townwide. No local PDF mirror exists for Westport (browsable encodeplus code site, not a single PDF), so these facts carry citations but not independently re-verified quotes.")

# ================= WILTON =================
wl = link("wilton", "Wilton Zoning Regulations (last revised Sept. 2026)", "https://www.wiltonct.gov/planning-zoning-department/files/regulations-document-october-7")
add("wilton", "Wilton", 330, 19255, None, 19, 95.4,
    nza_block(330, 98.5, 98.7, 98.7, 88.8, 100), wl, "R-2A", "HODD",
    [
        v(U, "R-2A", "\"Two-family\" / \"three-family\"", "Do not exist anywhere in the 337-page code", wl, "full-text search"),
        v(U, "R-2A", "Multifamily", "Prohibited", wl, "§29-5.A.2.a",
          "Permitted Uses: The following principal uses shall be permitted in all single-family residential districts as a matter of right: a. Single-family detached dwellings."),
        v(D, "R-2A", "Min. lot size", "2 acres (87,120 sq ft)", wl, "§29-5.D table"),
        v(U, "HODD", "Multi-family attached dwellings", "Permitted as a matter of right", wl, "§29-5.E.8",
          "Permitted Uses. The following principal uses shall be permitted in the HODD as a matter of right: a. Multi-family attached dwellings. b. Open space. c. Single-family detached dwellings."),
        v(D, "HODD", "Lot area", "9–11 acres", wl, "§29-5.E.9.a-b",
          "a. Minimum Lot Area  9 acres  b. Maximum Lot Area  11 acres"),
        v(U, "HODD", "Density / affordability", "10 units/gross acre, 30% affordable required", wl, "§29-5.E.9.c-d",
          "c. Maximum Density  10 units per gross acre  d. Percentage of Units Required to be Affordable  30 percent"),
        v(A, "Town-wide", "ADU max size", "¼ of gross floor area or 750 sq ft, whichever greater; max 2 bedrooms", wl, "§29-4.D.1",
          "Maximum Size: The floor area of the accessory dwelling unit may not exceed one-fourth of the gross floor area of the building or 750 square feet, whichever is greater. No more than two bedrooms are permitted in the accessory dwelling unit."),
        v(A, "Town-wide", "ADU owner-occupancy", "Required (one unit, annual certification)", wl, "§29-4.D.1",
          "Occupancy: One of the dwelling units shall be owner-occupied at all times."),
        v(P, "DRD/multifamily <17 units", "Parking minimum", "None, unless in a Conservation & Traffic Mitigation District", wl, "§29-8.B.5",
          "Off-street parking shall not be required for multifamily developments of less than seventeen (17) dwelling units unless that development is located in a Conservation and Traffic Mitigation District."),
        v(P, "R-2A", "Parking, single-family", "2/unit + 1 per guest sleeping room for roomers/boarders", wl, "§29-8.B.5.a(1)",
          "Single-family dwellings   2 per dwelling unit, plus 1 per guest sleeping room for roomers and boarders"),
        v(OA, "Town-wide", "Min. unit size", "Not found — regulations PDF blocked by bot-detection during this research pass", wl, "wiltonct.gov regs PDF — not retrieved"),
        v(OA, "4 overlay zones only (CRA-10, THRD, HODD, DE-5R)", "Inclusionary zoning", "10% (CRA-10, DE-5R) to 30% (HODD) affordable, confined to overlay zones — no town-wide mandate. A broader 30% proposal was circulating as of June 2026, adoption unconfirmed", wl, "zoning regs — secondary-sourced from P&Z meeting minutes"),
        v(OA, "Historic District & Historic Property Commission", "Historic overlay", "Commission's demolition-review authority applies town-wide, not limited to a mapped district; boundaries of any mapped district not independently confirmed", wl, "zoning code — not independently retrieved"),
        v(OA, "Town-wide", "Demolition delay", "Up to 90 days for structures >50 years old and >500 sq ft, regardless of historic-district location",
          link("wilton-demo", "Town of Wilton, Ordinance Concerning Stay of Demolition of Historic Buildings", "https://www.wiltonct.gov/historic-district-historic-property-commission/pages/demolition-delay"),
          "demolition delay ordinance",
          "The Historic District and Historic Properties Commission reviews requests for demolition of any structures or part thereof larger than 500 square feet and over 50 years of age, whether or not they are located in an Historic District."),
        v(OA, "None — inland town", "Coastal/flood overlay", "No coastal boundary; flood provisions exist as a general regulation (§29-9.F), not a distinct overlay zone", wl, "§29-9.F — text not retrieved, PDF blocked"),
    ],
    "HODD sites are capped between 9 and 11 acres — a narrow, purpose-built carve-out, not a general-purpose multifamily zone. No downloadable PDF mirror exists for Wilton (the live file is bot-blocked), but its full text was extracted directly from the live document and most figures above now carry an independently re-verified quote; a few (min. lot size table, min. unit size, inclusionary %, historic overlay) remain citation-only where the table or section wasn't cleanly extractable as text.")

# ================= RIDGEFIELD =================
rf = pdf("ridgefield", "ridgefield-zoning.pdf", "Ridgefield Zoning Regulations (revised through Aug. 2026)", "https://ridgefieldct.gov/Documents/Boards%20Committees%20and%20Commissions/Planning%20and%20Zoning%20Commission/About%20PZC%20Meetings/Zoning%20Regulations/Zoning%20Regulations%20August%202026.pdf")
add("ridgefield", "Ridgefield", 323, 25300, None, 21, 61.8,
    nza_block(323, 95.8, 95.6, 95.6, 0.0, 97), rf, "RAAA", "MFDD",
    [
        v(U, "RAAA", "Single-family", "Allowed, requires Zoning Permit (ZEO)", rf, "§3.2.B.1",
          "PERMITTED WITH ZONING PERMIT (ZEO) 1. Residential Uses - A single-family detached dwelling."),
        v(U, "RAAA", "2-/3-family", "Bundled & prohibited except by Special Permit in the separate SD R-20 overlay", rf, "§3.2.C.10.d"),
        v(D, "RAAA", "Min. lot size", "130,680 sq ft (3 acres)", rf, "§3.5.A table",
          "RAAA Zone              3.0 acres                 130,680 sq. ft."),
        v(D, "R-7.5", "Min. lot size (least restrictive base district)", "7,500 sq ft", rf, "§3.5.A table",
          "R-7.5 Zone             0.17 acres                 7,500 sq. ft."),
        v(U, "MFDD", "Multifamily", "Special Permit only — town's only multifamily pathway", rf, "§4.2.B",
          "PERMITTED BY SPECIAL PERMIT (COMMISSION) 1. Detached dwelling units. 2. Attached dwelling units with individual exterior entrances. 3. Multiple dwelling units in one building."),
        v(D, "MFDD", "Density", "6 units/acre (8 with 15% affordable)", rf, "§4.2.C",
          "a. Six (6) dwelling units per acre. b. Eight (8) dwelling units per acre provided: i. at least fifteen (15) percent of the total number of dwelling units are preserved in perpetuity as affordable housing"),
        v(A, "RAAA", "ADU max size", "900 sq ft (main dwelling <3,000 sf) or 1,200 sq ft (≥3,000 sf)", rf, "§3.3.B.2",
          "not exceed 900 square feet in total habitable floor area for properties with a main dwelling 2,999 square feet and under. For properties with a main dwelling that is 3,000 square feet or more, the accessory dwelling unit shall not exceed 1,200 square feet in total habitable area."),
        v(A, "RAAA", "ADU approval pathway", "Zoning Permit (ZEO), not Special Permit", rf, "§3.3.B.2",
          "Allows accessory dwelling units (and affordable ADUs) to be permitted via Zoning Permit instead of, and by deleting, Site Plan"),
        v(P, "RAAA", "Parking, one-/two-family", "2 spaces/unit", rf, "§7.3.B table",
          "One-family and two-family structures  Two (2) parking spaces for each dwelling"),
        v(P, "RAAA", "Parking, ADU + principal", "3 spaces combined", rf, "§3.3.B.2.h",
          "at least three (3) off-street parking spaces (which may include garage spaces) shall be provided to serve both the principal dwelling and the accessory dwelling unit and such parking shall not be located in the required front yard setback."),
        v(OA, "Town-wide", "Min. unit size", "Not found as a general dwelling minimum; only ADU caps located", rf, "zoning regs — not located in sections reviewed"),
        v(OA, "All zones except RAAA/RAA (≥5 units)", "Inclusionary zoning", "Tiered minimum affordable units (14% rounded up at scale); density bonus up to 30% for exceeding it by ≥5%", rf, "§8.8, adopted 5/16/2023",
          "All applications for development resulting in the creation of five (5) or more dwelling units shall designate a minimum number of dwelling units as per the Minimum Affordable Housing Chart"),
        v(OA, "Historic District Commission + Village District (downtown, 1998)", "Historic overlay", "HDC review limited to exterior features visible from a public way; separate Village District design-compatibility overlay downtown", rf, "Village District FAQ; CGS §7-147c"),
        v(OA, "Town-wide", "Demolition delay", "Up to 90 days for structures ≥50 years old, if written objection filed within 30 days of notice", rf, "Ch. 136, §136-4.A",
          "to authorize the Town of Ridgefield, as allowed by C.G.S.§ 29-406(b), to impose a waiting period of not more than 90 days before granting a demolition permit for certain structures of architectural, historical, or cultural importance."),
        v(OA, "Floodplain Overlay Zone, §6.1 (inland, no coastal boundary)", "Coastal/flood overlay", "Applies to FEMA Zones A and AE; no coastal area management provision (inland town)", rf, "§6.1",
          "The Floodplain Overlay Zone is hereby declared to be an overlay to any other zone, and the regulations, restrictions and requirements contained herein shall be in addition to those applicable in the underlying zone."),
    ],
    "Ridgefield has no as-of-right multifamily district of any kind — every multi-unit path requires a discretionary Special Permit hearing. A local PDF mirror now exists, and most figures below have been independently re-verified with a verbatim quote; a few (the 2-/3-family use-table row, min. unit size, and historic overlay) are still flagged as citation-only because the exact use-table row text couldn't be located in the mirrored document.")

# ================= WESTON =================
ws = pdf("weston", "weston-zoning.pdf", "Weston Zoning Regulations (amended through July 7, 2025)", "https://www.westonct.gov/home/showpublisheddocument/15463/638937003479630000")
add("weston", "Weston", 328, 10490, 12157, 3, 100.0,
    nza_block(328, 99.9, 99.9, 99.9, 100.0, 100), ws, "R-2A", "Village District / VD-R",
    [
        v(U, "R-2A", "Entire town's base zone", "2-/3-/4+-family prohibited, not addressed anywhere in the code", ws, "Sec. 321",
          "Single Family Dwelling, not to exceed one per lot."),
        v(D, "R-2A", "Min. lot size", "2 acres", ws, "Sec. 321.4",
          "321.4 Minimum Lot Area: Two Acres"),
        v(U, "Village District / VD-R", "All uses, incl. multifamily", "Require Special Permit", ws, "Sec. 322.1",
          "All uses within the Village District shall be subject to the approval of a special permit"),
        v(D, "Village District / VD-R", "Min. lot size (zone)", "1 acre, 200 ft min. width and depth", ws, "Sec. 322.2.d",
          "Minimum lot area                        1 acre"),
        v(U, "Village District / VD-R", "Affordability", "5+ unit projects must set aside ≥15% affordable", ws, "Sec. 322.4",
          "where five or more residential dwelling units are proposed under this Section 322, a minimum of 15% of such the units (rounded up to the nearest whole number of units) shall be affordable"),
        v(U, "VD-R", "Unit size cap (2025 amendment, unverified)", "2 bedrooms / 1,200 sq ft max", ws, "§322.3(c)(ii)"),
        v(A, "R-2A", "ADU max size", "Lesser of 900 sq ft or 30% of main dwelling floor area, max 1 bedroom", ws, "Sec. 345.4",
          "The floor space devoted to any apartment shall not exceed nine hundred (900) square feet in gross floor area, nor shall it exceed thirty percent (30%) of the entire floor area of the main dwelling"),
        v(A, "R-2A", "ADU owner-occupancy", "Required — owner must occupy main house or apartment", ws, "Sec. 345.5",
          "The owner (someone who owns not less than one-quarter (1/4) interest in the lot of the residence)"),
        v(P, "Village District / VD-R", "Parking (stated as a cap, not a minimum)", "Maximum 1 space (1BR unit); 2 spaces (2+BR units)", ws, "Sec. 363, Schedule",
          "Residential Dwellings in the Village District           Maximum of 1 space in the case of one bedroom; 2 spaces in the case of two or more bedrooms"),
        v(OA, "Town-wide", "Min. unit size", "Not found as a general minimum; only ADU/VD-R unit-size caps located", ws, "zoning regs — not located"),
        v(OA, "Village District only", "Inclusionary zoning", "≥15% of units affordable (CGS §8-30g eligibility) in VD projects of ≥5 units; no density bonus or fee-in-lieu provision", ws, "§322.4",
          "where five or more residential dwelling units are proposed under this Section 322, a minimum of 15% of such the units (rounded up to the nearest whole number of units) shall be affordable"),
        v(OA, "5–7 local districts, Town Code Ch. 93 (discrepancy in town's own sources on exact count)", "Historic overlay", "Separately administered local historic districts under CGS §7-147a; Village District zoning overlay geographically overlaps the Norfield Historic District", ws, "Town Code §93-1 to §93-5"),
        v(OA, "Town-wide", "Demolition delay", "Ordinance referenced on permit applications, but exact waiting period could not be confirmed in available sources", ws, "\"the Demolition Ordinance, of the Town of Weston\" — full text not located"),
        v(OA, "Floodplain Management Regs, eff. 2010 (inland, no coastal boundary)", "Coastal/flood overlay", "New construction must be elevated ≥1 ft above Base Flood Elevation; no coastal area management provision (inland town)", ws, "Floodplain Mgmt Regs §IV.A",
          "shall have the lowest floor elevated one foot or more above the Base Flood Elevation"),
    ],
    "Town's own PDF was blocked by a bot-detection wall during research; base-district figures came from a 2021-dated third-party copy (no local mirror exists, so no quotes could be independently re-verified), and the R-2A single-family parking minimum could not be located at all — flagged for direct verification with Weston Land Use.")

# ================= EASTON =================
es = pdf("easton", "easton-zoning.pdf", "Easton Zoning Regulations (last revised July 7, 2024)", "https://ct-easton.civicplus.com/DocumentCenter/View/3109")
add("easton", "Easton", 316, 7815, 17110, 3, 96.9,
    nza_block(316, 100, 100, 100, 91.4, 100), es, "Residence A / Residence B", "None exists",
    [
        v(U, "Residence A/B", "\"Two-family\", \"duplex\", \"multi-family\", \"three-family\"", "Zero matches in a full-text search of the 6,576-line regulations", es, "exhaustive keyword search"),
        v(D, "Residence A", "Min. lot size", "40,000 sq ft", es, "§3510 table",
          "Minimum Lot Area                                 40,000 square feet"),
        v(D, "Residence B", "Min. lot size", "3 acres (130,680 sq ft)", es, "§3510 table",
          "130,680 square feet"),
        v(U, "Any district", "Multifamily pathway", "None — not even by special permit", es, "full code review"),
        v(A, "Residence A/B", "ADU max size (attached)", "Lesser of 40% of dwelling area or 1,500 sq ft", es, "§5220.2.a",
          "Forty percent (40%) of the area of the principal dwelling (exclusive of garage, attic, and cellar) or 1,500 square feet, whichever is the more restrictive requirement"),
        v(A, "Residence A/B", "ADU max size (detached)", "Lesser of 30%/1,000 sq ft (≥87,120 sf lot) or 20%/800 sq ft (≥34,000 sf lot)", es, "§5220.2.b",
          "Twenty percent (20%) of the area of the principal dwelling (exclusive of garage, attic, and cellar) or 800 square feet, whichever is the more restrictive requirement"),
        v(A, "Residence A/B", "ADU owner-occupancy", "Required (annual affidavit)", es, "§5220.1",
          "The owner of the property shall occupy either the principal dwelling or the ADU and an annual affidavit shall be filed by January 31 of each year attesting to such occupancy."),
        v(A, "Residence A/B", "ADU bedroom cap", "2 bedrooms (attached) / 1 bedroom (detached)", es, "§5220.3",
          "An ADU within/attached to the principal dwelling shall not contain more than two bedrooms"),
        v(P, "Residence A/B", "Parking, single-family dwelling", "2.0 spaces", es, "§6221 table",
          "Single‐family dwelling                         2.0 spaces"),
        v(P, "Residence A/B", "Parking, ADU", "+2.0 spaces (4 total with ADU)", es, "§6221 table",
          "Accessory dwelling unit                        2.0 spaces in addition to residence requirement"),
        v(OA, "Town-wide", "Min. unit size", "Not found as a general minimum beyond ADU caps already captured above", es, "zoning regs — not located"),
        v(OA, "Town-wide", "Inclusionary zoning", "None found — no local ordinance. A 2022 developer proposal with 30% affordable (105 units) was DENIED by P&Z under state CGS §8-30g process, not a town mandate", es, "full-text search; P&Z denial Feb. 2022"),
        v(OA, "Town-wide", "Historic overlay", "None found — no local CGS §7-147a historic district commission/ordinance; only an honorary National Register listing (Aspetuck Historic District, spans Easton/Weston)", es, "full-text search"),
        v(OA, "Town-wide", "Demolition delay", "Up to 90 days for structures on the town's \"Index to Historic Homes\" (≥50 years old, significant)", es, "Ch. 254, adopted 2022, amended 2024",
          "To encourage the preservation, documentation, and protection of historically sensitive buildings."),
        v(OA, "\"4100 Floodplain Overlay District\" (inland, no coastal boundary)", "Coastal/flood overlay", "Overlay confirmed to exist in the zoning table of contents; full text not independently verified (current PDF link dead on eastonct.gov)", es, "zoning regs Table of Contents, p.35 (2019 ed.)"),
    ],
    "Of all 17 towns researched, Easton is the single clearest case of total legal exclusion of 2+-family housing — confirmed by exhaustive keyword search, not an oversight. No local PDF mirror exists for Easton, so these facts rest on the search method itself rather than a re-verifiable quote.")

# ================= FAIRFIELD =================
ff = pdf("fairfield", "fairfield-zoning.pdf", "Fairfield Zoning Regulations (eff. Sept. 6, 2025)", "https://fairfieldct.gov/Fairfield_ZoningRegulations_Adopted_Effective_09062025%20-%20updated%209.28.26.pdf")
add("fairfield", "Fairfield", 315, 65300, 18618, 17, 78.6,
    nza_block(315, 91.2, 95.8, 95.1, 47.1, 100), ff, "AAA/AA/R-3/R-2/A", "District C",
    [
        v(U, "AAA/AA/R-3/R-2/A", "No multi-unit housing category", "Exists at all in these five districts", ff, "§1.2, §3.1 preamble",
          "No use shall be permitted in said Districts, except as these Single-Family Residence District regulations"),
        v(U, "AAA/AA/R-3/R-2/A", "How many districts", "There shall be five Single-Family Residence Districts", ff, "§1.1",
          "There shall be five Single-Family Residence Districts, “AAA”, “AA”, “R-3”, “R-2”, and “A”."),
        v(D, "AAA", "Min. lot size", "2 acres", ff, "§3.3.1 table",
          "A. Minimum Lot Area (sf or acres if noted)                2 ac"),
        v(D, "A", "Min. lot size", "9,375 sq ft", ff, "§3.3.1 table",
          "20,000           14,000          9,375"),
        v(D, "AAA/AA/R-3/R-2", "Max. height", "40 ft / 3 stories", ff, "§3.3.1 table",
          "D. Maximum Allowed Height of Buildings                     40          40                40              40               32"),
        v(D, "A", "Max. height", "32 ft / 2.5 stories", ff, "§3.3.1 table",
          "40               32"),
        v(D, "AAA", "Min. street-line / side / rear setback", "60 ft / 30 ft / 50 ft", ff, "§3.4.1 table",
          "A. Street Line Setback (ft)                       60             50              40           30            30"),
        v(D, "A", "Min. street-line / side / rear setback", "30 ft / 7 ft / 30 ft", ff, "§3.4.1 table",
          "B.     Side Line Setback (ft)                     30             25              15           10             7"),
        v(U, "District B/C", "Two-family", "Permitted (\"P\") in both B and C", ff, "§5.2 use table",
          "A. Two-Family Dwellings                                                             P               P      Section 5.3"),
        v(U, "District C", "Three-family", "Permitted (\"P\") in C only (— in B)", ff, "§5.2 use table",
          "B.     Three-Family Dwellings                                                   —                   P"),
        v(U, "District C", "Four-family", "Permitted (\"P\") in C only (— in B)", ff, "§5.2 use table",
          "C. Four-Family Dwellings                                                        —                   P"),
        v(D, "District B/C", "Lot minimums (2F / 3F / 4F)", "9,000 (B) / 7,500 (C) — 10,000 (C) — 12,500 (C) sq ft", ff, "§5.3.1 table",
          "Minimum Lot Area for Two-Family (sf)                                                9,000              7,500"),
        v(A, "AAA/AA/R-3", "ADU (detached) availability", "Permitted; not available in R-2 or A", ff, "§3.2 table, item T",
          "T.    Accessory Dwelling Units (Detached)                  A       A       A"),
        v(A, "Town-wide", "ADU max size", "Lesser of 40% of original residence floor area or 1,500 sq ft", ff, "§13.3.B",
          "The accessory apartment shall contain no more than 40% of the floor area of the originally existing residence or 1,500 square feet, whichever is less."),
        v(A, "Town-wide", "ADU owner-occupancy", "Required throughout the duration of the permit", ff, "§13.3.A",
          "A principal owner of the residence must reside in either the primary dwelling or the accessory apartment throughout the duration of the permit."),
        v(P, "Town-wide", "Parking, single-family", "2 spaces", ff, "§25.4.1 table, item K",
          "Single-family residential - 2 spaces"),
        v(P, "District B/C", "Parking, multifamily (≤16 units)", "1 space/1BR unit, 2 spaces/2BR+ unit", ff, "§25.4.1 table, item K",
          "Multi-family: 1 space for up to each 1-bedroom and 2 spaces for each 2-bedroom unit or larger."),
        v(OA, "Town-wide", "Min. unit size", "Not independently confirmed in the current (Sept. 2025) zoning text; an earlier (2021) version reportedly had a detailed per-district minimum floor-area schedule that may have been superseded in the 2025 recodification", ff, "current zoning regs — not located; flagged version discrepancy"),
        v(OA, "Town-wide (≥5 net new units) / 15% in TOD areas & DRD overlay", "Inclusionary zoning", "12% of units must be set aside as Below Market Rate (BMR); 15% in Commerce Drive/TOD/DRD/Transit-Oriented Downtown", ff, "§15.3",
          "Any project that results in a net increase of 5 or more dwelling units, whether by new construction or by the alteration, expansion, reconstruction, or change of existing residential or nonresidential space shall include provision to set aside not less than 12% of said units as below market rate (BMR) units."),
        v(OA, "Southport Historic District (est. 1966/67, ~225 acres)", "Historic overlay", "Reviewed by Fairfield HDC; case law confirms review scope limited to changes visible from a public way", ff, "CGS §7-147a et seq.; Gibbons v. Fairfield HDC, 285 Conn. 755 (2008)"),
        v(OA, "Town-wide", "Demolition delay", "10 days for structures <100 years old; 60 days for structures ≥100 years old",
          link("fairfield-ch57", "Fairfield Code of Ordinances, Ch. 57 (Demolition, adopted 2007) — exact URL not captured during research", "https://fairfieldct.gov"),
          "§57-2C/D (not independently re-verified — lives in the Code of Ordinances, not the zoning regulations PDF)"),
        v(OA, "Coastal Site Plan Review, Section 34 (true coastal town)", "Coastal/flood overlay", "Applies — Long Island Sound frontage; FEMA Zones A/AE/VE, Zone VE also a Coastal High Hazard Area", ff, "§34.1",
          "All buildings, uses and structures fully or partially within the coastal boundary as defined by Section 22a-94 of the Connecticut General Statutes and as delineated on the Coastal Boundary Map for the Town of Fairfield, shall be subject to the coastal site plan review requirements and procedures in Sections 22a-105 through 22a-109 of the Connecticut General Statutes."),
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
        v(D, "R-4", "Min. lot size (most restrictive tier)", "174,200 sq ft (4 acres)", rd, "§4.6 table",
          "Square feet                  174,200   87,120   43,560    21,780"),
        v(D, "R-1", "Max. height", "40 ft", rd, "§4.6 table",
          "BUILDING HEIGHT                40       40          40     40             40     40     40      40     40"),
        v(D, "R-1", "Min. front / side / rear yard", "45 ft / 25 ft / 40 ft", rd, "§4.6 table",
          "Front Yard (feet)              60       50          45*    40             25     25     50      10    100"),
        v(U, "RV", "Multifamily", "Special Permit only, capped at 1 unit/8,000 sq ft of site area", rd, "§4.2.3(o)",
          "Within RV Residential Zone only, residential apartments, townhouses or condominiums not exceeding a density of one (1) residential unit per 8,000 square feet of site area"),
        v(D, "RV", "Min. lot size (zone)", "No acreage minimum (NR)", rd, "§4.6 table"),
        v(A, "Town-wide", "ADU approval pathway", "Special Permit required (not by-right)", rd, "§5.12.1",
          "One (1) accessory residential apartment (see Definitions, Section 8.1.11) may be permitted on a lot, subject to a Special Permit granted by the Commission."),
        v(A, "Town-wide", "ADU owner-occupancy", "Required throughout the duration of the apartment use", rd, "§5.12.3(a)",
          "The owner of the premises shall be resident in either the accessory or principal dwelling throughout the duration of the apartment use."),
        v(A, "Town-wide", "ADU max size (attached)", "Lesser of 30% of dwelling floor area or 1,000 sq ft", rd, "§5.12.4(c)",
          "comprising no more than 30% of the total finished floor area of the dwelling, or 1000 square feet of gross (total) floor area, whichever is less."),
        v(P, "Town-wide", "Parking, single-family dwelling", "2 spaces/dwelling", rd, "§5.6.2 table",
          "Single-family dwelling, including family              2 per dwelling"),
        v(OA, "Town-wide (accessory apartments)", "Min. unit size", "Accessory apartments must be ≥300 sq ft — notable as an actual floor (not just a cap); no general minimum found for principal dwellings", rd, "§5.12.3(b)",
          "Gross (total) floor area of the apartment shall be not less than 300 square feet."),
        v(OA, "Historic Mill Center (HMC) Zone only (incentive, not mandate)", "Inclusionary zoning", "Density bonus to 10 units/acre (from base 4) if ≥30% of units are deed-restricted affordable in restored historic buildings", rd, "§4.5.3(a)",
          "10 dwelling units per acre of developed site area if the units are wholly within restored historic buildings and at least 30% of the units are dedicated and deed restricted to meet Affordable Housing requirements."),
        v(OA, "None — deliberately chosen over regulation", "Historic overlay", "No local CGS §7-147a historic district; town uses a voluntary preservation-easement program instead, explicitly framed as more flexible than additional regulations", rd, "Town \"Historic Homes\" page"),
        v(OA, "Town-wide", "Demolition delay", "180 days (longer than most CT-4 towns' 90-day default), enacted 2013", rd, "Demolition Delay Ordinance (town website, codified chapter not independently verified)",
          "Encourage the preservation, documentation, and protection of historically sensitive buildings"),
        v(OA, "Flood Safety, §5.4.5 (inland, no coastal boundary)", "Coastal/flood overlay", "Applies to flood-prone areas under CGS §8-2 delegation; no coastal area management provision (inland town)", rd, "§5.4.5",
          "to promote the public health, safety and general welfare and to minimize public and private losses due to flood conditions"),
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
        v(D, "RF-1", "Max. height", "2.5 stories / 35 ft", mn, "§3.1.6(A)",
          "No building or other structure shall exceed a height of two-and-one-half"),
        v(D, "RF-1", "Min. front / side-rear yard", "50 ft / 25 ft", mn, "§3.1.5(A)",
          "No building or other structure shall extend within less than fifty (50) feet of any front lot line, nor within twenty-five (25) feet of any side or rear lot line."),
        v(U, "MFR", "Multifamily density", "2.5 units/gross acre (attached)", mn, "§3.4.5(A)(1)",
          "Attached single-family units: two-and-half (2.5) units per gross acre of the parcel"),
        v(D, "MFR", "Min. parcel to create district", "70 contiguous acres", mn, "§3.4.5(B)",
          "Minimum parcel size shall be seventy (70) acres under same ownership in a single continuous"),
        v(A, "RF-1/RF-2/RF-3", "ADU approval pathway", "By-right (\"ACC\" — Certificate of Use, no special-permit hearing)", mn, "§6.9.2(H)",
          "Accessory Apartment                ACC     ACC     ACC"),
        v(A, "RF-1/RF-2", "ADU attachment requirement", "Attached only (RF-3 also permits detached)", mn, "§6.9.1(B)",
          "the RF-3 District can include the conversion of an existing detached accessory structure or new construction of a detached ADU."),
        v(A, "Town-wide", "ADU owner-occupancy", "Required at all times", mn, "§6.9.2(A)",
          "Either the principal dwelling or accessory apartment shall be occupied by the owner of the premises at all times."),
        v(A, "Town-wide", "ADU size range", "400–1,000 sq ft, max 1 bedroom, ≤30% of gross livable floor area", mn, "§6.9.1(C)",
          "Living area of an accessory apartment shall contain a minimum of four-hundred (400) square feet and shall not exceed a maximum of one-thousand (1,000) square feet; there shall be no more than one (1) bedroom in such apartment."),
        v(P, "Town-wide", "Parking, studio/1BR", "1.0 space/unit", mn, "§10.2 Schedule",
          "Studio, One Bedroom                      1.0 space per unit with adequate driveway turnaround."),
        v(P, "Town-wide", "Parking, 2BR+", "2.0 spaces/unit", mn, "§10.2 Schedule",
          "Two-Bedroom or more                       2.0 spaces per unit with adequate driveway turnaround."),
        v(OA, "Town-wide", "Min. unit size", "A 2018 Bulk Schedule reportedly showed a 1,100 sq ft figure, but the source document is now a dead link and the applicable district column could not be confirmed", mn, "2018 Bulk Schedule PDF — not independently verified"),
        v(OA, "Town-wide", "Inclusionary zoning", "None found — no local §8-2i ordinance; town affordable-housing stock reported at ~1.33% of units", mn, "full-text search; town data"),
        v(OA, "Monroe Center Historic District (est. 1969)", "Historic overlay", "Overseen by a local Historic District Commission; full regulatory text (CGS §7-147a procedures) not independently retrieved", mn, "Local Historic Districts CT database — not independently verified"),
        v(OA, "Town-wide", "Demolition delay", "180 days for structures ≥60 years old (or pre-1950) and ≥500 sq ft; HDC chair can waive, or it lapses automatically after 60 days of HDC inaction",
          link("monroe-demo", "Monroe Town Code, Demolition Delay (adopted 2003, amended 2009/2011) — exact URL not captured during research", "https://www.monroect.gov"),
          "Town Code (ecode360) — not in the zoning regulations PDF"),
        v(OA, "Not confirmed (inland, no coastal boundary expected)", "Coastal/flood overlay", "No Monroe-specific floodplain overlay text was retrievable; town is inland so no coastal area management provision would be expected regardless", mn, "not independently verified — all source links dead"),
    ],
    "Monroe's code does not distinguish a 3-unit tier from larger multifamily — its own definition of \"multi-family\" legally includes buildings with as few as 2 units.")

# ================= TRUMBULL =================
tb = pdf("trumbull", "trumbull-zoning.pdf", "Trumbull Zoning Regulations (amended through Aug. 19, 2026)", "https://trumbull-ct.gov/DocumentCenter/View/1323")
add("trumbull", "Trumbull", 327, 38073, 14786, 25, 63.6,
    nza_block(327, 99.6, 98.8, 98.0, 0.0, 99), tb, "Residence A/AA/AAA", "MFO",
    [
        v(U, "Residence A/AA/AAA", "Single-family only", "Only use permitted: \"One-Family Dwelling\"", tb, "Art. II §1.1.1",
          "Within the Residence AAA, AA or A Zone no Building or Structure shall be erected, altered, occupied or used, arranged or designed to be used for other than one or more of the following specified purposes: 1. One-Family Dwelling;"),
        v(D, "Residence A", "Min. lot size", "21,780 sq ft (½ acre)", tb, "Art. I §2",
          "acre, 21,780 sq. ft.)"),
        v(D, "Residence AA/AAA", "Min. lot size", "43,560 sq ft (1 acre)", tb, "Art. I §2",
          "Residence Zone AAA              (minimum lot size 1 acre, 43,560 sq. ft.)"),
        v(D, "Residence AAA", "Max. height / F.A.R.", "40 ft, 0.29 F.A.R.", tb, "Art. III Exhibit",
          "Residence AAA         1 acre                   1 story          1500"),
        v(D, "Residence AAA", "Min. front / side / rear yard", "50 ft / 20 ft / 50 ft", tb, "Art. III Exhibit",
          "40(g)         50      20     50"),
        v(D, "Residence A", "Max. building coverage", "25%", tb, "Art. III Exhibit",
          "40a(g)         50a     20a   50a      25%"),
        v(U, "Town-wide", "Multifamily rental moratorium", "No new applications above 50 units (except 55+ housing) until Feb. 28, 2027", tb, "Art. XVII",
          "the Planning and Zoning Commission hereby declares an immediate moratorium on all applications for, and approvals of, any multi-family residential rental housing to determine the additional need of this type of housing in the Town."),
        v(U, "MFO", "Multifamily", "Special Permit only, existing I-L/I-L2 industrial land ≥10 acres", tb, "§7.6.2",
          "An MFO Zone may be located only on properties that meet all of the following criteria: a. Currently zone IL or IL-2"),
        v(U, "MFO", "Density / town-wide cap", "20 units/acre, capped at 600 units town-wide", tb, "§7.6.4(1)",
          "The maximum number of dwelling units shall be 20 units per acre. The maximum number of dwelling units that may be developed pursuant to this MFO shall be 600, provided that no more than 220 units may be approved by the Commission within any 12 month period."),
        v(D, "MFO", "Unit types", "1BR (min 700 sf) and 2BR (min 950 sf) only — no studios, no 3BR+", tb, "§7.6.4(9)"),
        v(D, "MFO", "Height cap", "65 ft / 5 stories", tb, "§7.6.4(2)",
          "The maximum height of any principal building shall not exceed 65 feet or five (5) stories."),
        v(A, "Residence A/AA/AAA", "ADU approval pathway", "Administrative (ZEO) if within existing footprint; Special Permit otherwise", tb, "§1.1.2(7)(D)",
          "If a proposed accessory apartment is (i) entirely within the existing footprint of the house and (ii) there are no exterior changes to the"),
        v(A, "Residence A/AA/AAA", "ADU owner-occupancy", "Required for at least one unit", tb, "§1.1.2(7)(C)(b)",
          "At least one (1) Dwelling Unit in the converted single-family home shall be owner-occupied"),
        v(A, "Residence A/AA/AAA", "ADU size", "≥300 sq ft, max 30% of principal dwelling's livable floor area", tb, "§1.1.2(7)(C)(a)",
          "An accessory apartment must have at least three hundred (300) square feet of Livable Floor Area. Maximum size shall not exceed thirty (30%) per cent of the Livable Floor Area of the Principal Dwelling"),
        v(A, "Residence A/AA/AAA", "ADU deed restriction", "40-year affordable-housing deed restriction under CGS §8-30g(k)", tb, "§1.1.2(7)(D)",
          "Every accessory apartment approved under this section of the Zoning Regulations shall be deemed an"),
        v(P, "MFO", "Parking", "1.8 spaces/1BR unit, 2.0 spaces/2BR unit, + 1.0 guest space/20 units", tb, "§7.6.4(5)"),
        v(OA, "Residence AAA (1-story)", "Min. unit size", "1,500 sq ft first-floor minimum for a 1-story home", tb, "Art. III Exhibit",
          "Residence AAA         1 acre                   1 story          1500"),
        v(OA, "Reservoir Apartment District (RAD) overlay only", "Inclusionary zoning", "15% of units must be affordable (80% AMI); a broader townwide provision (Art. 7.4) was repealed in 2008", tb, "§2.8(n)",
          "At least 15% of the total units shall be designated as affordable units. Affordable units shall mean units restricted to individuals earning 80% of the area median income"),
        v(OA, "None — incentive-based Adaptive Reuse tool instead", "Historic overlay", "No local CGS §7-147a historic district; an Adaptive Reuse provision (§6.1-6.3) waives dimensional standards for qualifying historic-building reuse, reviewed by a Historical/Demolition Review Committee", tb, "§6.1-6.3"),
        v(OA, "Town-wide", "Demolition delay", "A Demolition Review Committee exists (Town Charter) and is active, but no specific waiting-period length (e.g. 90 or 180 days) could be confirmed", tb, "Town Charter — exact waiting period not located"),
        v(OA, "Art. XI, Flood Damage Prevention Ordinance (inland, no coastal boundary)", "Coastal/flood overlay", "Variances available for reconstruction of National/State Register historic structures; no coastal area management provision (inland town)", tb, "§4.4-1/4.4-2",
          "Variances may be issued for the reconstruction, rehabilitation or restoration of structures listed on the National Register of Historic Places or the State Inventory of Historic Places, without regard to the procedures set forth in the remainder of this section."),
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
        v(OA, "Room-and-board use", "Min. unit size", "200 sq ft per occupant (room-and-board); a general single-family minimum (\"Schedule B\") is referenced but was not legible via OCR", sh, "§44.4.2"),
        v(OA, "Town-wide", "Inclusionary zoning", "Not found as a specific percentage requirement; only an incidental fee-waiver reference for deed-restricted affordable units", sh, "fee schedule — not located as a mandate"),
        v(OA, "Huntington Center Historic District (National Register, 2000)", "Historic overlay", "Federal/honorary listing only; no local CGS §7-147 regulatory commission confirmed", sh, "zoning regs reference the concept at §48.6, but no dedicated chapter located"),
        v(OA, "Town-wide", "Demolition delay", "Not found — no Shelton-specific demolition delay ordinance located in available sources", sh, "not located"),
        v(OA, "Coastal Site Plan Review, §45.5 (Housatonic River, tidal)", "Coastal/flood overlay", "Applies — tidal river frontage, CT Coastal Management Act review; a separate floodplain/flood-hazard ordinance was not located (surprising for a river town, may be in the general Code of Ordinances)", sh, "§45.5"),
    ],
    "Shelton's own code is a scanned, image-only PDF with NO embedded text layer — it cannot be text-searched or highlighted in the in-app viewer at all. Every figure above was OCR'd and visually verified against the table images directly during research; open the original source to see the actual scanned tables.")

# ================= STRATFORD =================
st = link("stratford", "Stratford Zoning Code Ch. A220 (eff. Jan. 1, 2025)", "https://ecode360.com/9207545")
add("stratford", "Stratford", 326, 53610, 11017, 28, 33.8,
    nza_block(326, 84.2, 1.5, 0.9, 0.0, 100), st, "RS-1", "RM-1",
    [
        v(U, "RS-1", "Two- and three-family", "One combined use-table row, \"Two and Three Family Dwellings,\" not permitted", st, "§4.2.4 Use Table",
          "Two and Three Family Dwellings"),
        v(D, "RS-4", "Min. lot size", "7,500 sq ft", st, "§3.2.1 table"),
        v(D, "RS-1", "Min. lot size", "40,000 sq ft", st, "§3.2.1 table",
          "RS-1\n\t\n40,000"),
        v(U, "RS-1/RM-1", "4+-unit multifamily", "Special Permit (threshold inconsistently stated as \"4 or more\" vs. \"3+\")", st, "§5.1.2-3",
          "Multifamily Dwellings (4 or more)"),
        v(U, "RM-1", "2- and 3-family", "Allowed BY RIGHT (\"P¹\")", st, "§4.2.4 Use Table",
          "Two and Three Family Dwellings"),
        v(D, "RM-1", "Min. lot area per unit", "2,500 sq ft", st, "§3.2.2, footnote 1",
          "The minimum lot area per family dwelling unit shall be 2,500 square feet, or as specified in Section 5.1."),
        v(A, "RS-1/RM-1 (town-wide)", "ADU approval pathway", "Administrative review (\"A\")", st, "§4.4.2",
          "Applications for accessory residential apartments must be submitted to the Zoning Commission for an administrative site plan review."),
        v(A, "RS-1/RM-1 (town-wide)", "ADU owner-occupancy", "Required for duration of the permit", st, "§4.4.2.E",
          "The principal owner of the residence must reside in either the primary dwelling or the accessory residential apartment throughout the duration of the permit."),
        v(A, "RS-1/RM-1 (town-wide)", "ADU max size", "1,000 sq ft, max 1 bedroom", st, "§4.4.2.E",
          "The accessory residential apartment shall contain no more than 1,000 square feet."),
        v(P, "RS-1", "Parking, single-family dwelling", "1 space/unit", st, "§6.8.4.A table",
          "Single-family dwelling\n\t\n1 per unit"),
        v(P, "RM-1", "Parking, multifamily (3+)", "1/unit (studio-1BR), 1.5/unit (2BR), 2/unit (3+BR), + 10% guest", st, "§6.8.4.A table",
          "Efficiency or 1-bedroom: 1 per unit\n2-bedroom: 1.5 per unit\n3+ bedroom: 2 per unit\nGuest parking: additional 10% of total required spaces"),
        v(OA, "Town-wide", "Min. unit size", "Confirmed absent — the RS-1–RS-4 and RM-1 dimensional tables have no \"Minimum Floor Area\" row; only a maximum (2,100 sq ft) for older-adult housing", st, "§A220-3.2.1(C), §A220-3.2.2(C), §5.1.7"),
        v(OA, "Multifamily (3+ units), OP District or ≥8 net new units elsewhere", "Inclusionary zoning", "12% of units affordable (OP District) or 10% (≥8 net new units elsewhere), ≤80% AMI/SMI", st, "§5.1.5(C)",
          "shall designate a minimum of 12% of the development's units as affordable units"),
        v(OA, "Academy Hill Historic District, Town Code Ch. 121", "Historic overlay", "Certificate of Appropriateness required for alteration/demolition; decision within 65 days or deemed approved", st, "§121-6A, §121-7B",
          "No building or structure shall be erected or altered within the historic district or on historic property"),
        v(OA, "Academy Hill Historic District only (unclear if a broader townwide ordinance exists)", "Demolition delay", "90 days from permit issuance while the Commission or state seeks an alternative", st, "§121-11B",
          "Demolition of a building in the district is delayed 90 days from permit issuance while the Commission or the state seeks an alternative."),
        v(OA, "Flood Damage Prevention, Town Code Ch. 102 (true coastal town)", "Coastal/flood overlay", "Applies — Long Island Sound frontage; FEMA Zones A/AE/VE, Zone VE also a Coastal High Hazard Area; dedicated waterfront zoning districts (WF, WR, RC) exist", st, "§102-6/102-7",
          "This chapter shall apply to all areas of special flood hazard within the jurisdiction of Stratford, Connecticut."),
    ],
    "An apparent inconsistency exists between the Use Table's \"4 or more units\" threshold and §5.1's \"(3+)\" heading for Special Permit review — flagged for follow-up. Stratford's code is hosted as a browsable eCode360 site rather than a single PDF, so there's no local mirror — but every figure below has now been independently re-verified against the live eCode360 text and carries a verbatim quote.")

# ================= HAP RESTRICTIVENESS SCORE =================
# Our own composite index, built entirely from the Variables tables above (not NZA's
# data). 0 = least restrictive, 100 = most restrictive. Six weighted components, each
# scored against a fixed, published rubric from one or two concrete facts already shown
# on the town's own page -- so every point is traceable back to a quoted, cited fact
# rather than a black box. If a component's underlying fact wasn't independently
# confirmed for a town (e.g. an unconfirmed demolition-delay period), that component is
# left out and the composite is renormalized over the components that *were* available.
import math

USE_PERMISSIONS_RUBRIC = {
    "none": 30,            # no multifamily pathway exists anywhere, not even by special permit
    "discretionary": 25,   # multifamily only via Special Permit/discretionary hearing, town-wide
    "narrow_by_right": 17, # by-right but confined to a tiny or high-barrier-to-create district
    "capped_by_right": 12, # by-right in a real district, but a hard unit/density cap limits it
    "by_right": 6,         # by-right multifamily in at least one meaningful, uncapped district
}
APPROVAL_PROCESS_RUBRIC = {
    "none": 10, "discretionary": 9, "narrow_by_right": 6, "capped_by_right": 4, "by_right": 1,
}
ADU_PATHWAY_RUBRIC = {
    "prohibited": 15, "special_permit": 12, "zoning_permit": 7, "administrative": 4, "by_right": 1,
}

def lot_size_points(sqft, floor=2500, ceiling=174240, max_pts=20):
    if sqft is None:
        return None
    if sqft <= floor:
        return 0.0
    frac = (math.log10(sqft) - math.log10(floor)) / (math.log10(ceiling) - math.log10(floor))
    return round(max(0.0, min(max_pts, frac * max_pts)), 1)

def parking_points(spaces, max_pts=10, ceiling=2.5):
    if spaces is None:
        return None
    return round(max(0.0, min(max_pts, (spaces / ceiling) * max_pts)), 1)

def demolition_points(days, max_pts=15, ceiling=180):
    if days is None:
        return None
    return round(max(0.0, min(max_pts, (days / ceiling) * max_pts)), 1)

# Raw inputs, hand-scored per town against the rubric above using the Variable rows
# already shown on that town's page. (use_tier, note), (min_lot_sqft, note),
# (adu_tier, note), (parking_spaces, note), (demolition_days or None, note)
SCORE_INPUTS = {
    "bridgeport": {
        "use": ("by_right", 'NX2 zone: "Up to 4 units (House A) = By-right, no special permit"'),
        "lot": (0, 'N1 base district: "Min. lot width = 45 ft (no lot area minimum)"'),
        "adu": ("by_right", 'N1: "ADU = allowed by-right"'),
        "parking": (0, '"Parking minimum = None — citywide"'),
        "demo": (90, '"Demolition delay = Up to 90 days for qualifying structures"'),
    },
    "darien": {
        "use": ("discretionary", 'DMR (town\'s only multifamily zone): "Multifamily = Special Permit only"'),
        "lot": (43560, 'R-1 (smallest base district): "Min. lot size = 43,560 sq ft (1 acre)"'),
        "adu": ("administrative", 'No special-permit hearing required; owner-occupancy affidavit filed administratively'),
        "parking": (2, 'R-1/R-2: "Parking, one-/two-family residences = 2 spaces/unit"'),
        "demo": (None, 'Delay likely exists but exact codified period not independently located'),
    },
    "easton": {
        "use": ("none", '"Multifamily pathway = None — not even by special permit"'),
        "lot": (40000, 'Residence A: "Min. lot size = 40,000 sq ft"'),
        "adu": ("administrative", 'Annual owner-occupancy affidavit, no special-permit hearing required'),
        "parking": (2, 'Residence A/B: "Parking, single-family dwelling = 2.0 spaces"'),
        "demo": (90, '"Demolition delay = Up to 90 days for structures on the town\'s Index to Historic Homes"'),
    },
    "fairfield": {
        "use": ("by_right", 'District B/C: "Two-Family Dwellings = P" and three-/four-family "P" in C'),
        "lot": (9375, 'District A (smallest single-family tier): "Min. lot size = 9,375 sq ft"'),
        "adu": ("administrative", 'AAA/AA/R-3: "ADU (detached) availability = Permitted", no hearing required'),
        "parking": (2, 'District B/C: "Parking, multifamily (≤16 units)" = 2 spaces for 2BR+ unit'),
        "demo": (10, '"Demolition delay = 10 days for structures <100 years old" (the common case)'),
    },
    "greenwich": {
        "use": ("discretionary", 'R-MF: "Two-family / multifamily = Special Permit only, no distinct 3-unit tier"'),
        "lot": (12000, 'R-12 (smallest base district): "Min. lot size = 12,000 sq ft"'),
        "adu": ("zoning_permit", '"ADU approval pathway = By Zoning Permit (not Special Permit, unless oversized)"'),
        "parking": (2, 'R-MF: "Parking, 1–2BR unit = 1 garage space + 1 outdoor space"'),
        "demo": (90, '"Demolition delay = Up to 90 days (45 + 45 if an objection is filed)"'),
    },
    "monroe": {
        "use": ("narrow_by_right", 'MFR district requires "Min. parcel to create district = 70 contiguous acres" before any multifamily can exist'),
        "lot": (43560, 'RF-1 (only base district tracked): "Min. lot size = 43,560 sq ft (1 acre)"'),
        "adu": ("by_right", '"ADU approval pathway = By-right (ACC — Certificate of Use, no special-permit hearing)"'),
        "parking": (2, '"Parking, 2BR+ = 2.0 spaces/unit"'),
        "demo": (180, '"Demolition delay = 180 days for structures ≥60 years old (or pre-1950) and ≥500 sq ft"'),
    },
    "new-canaan": {
        "use": ("discretionary", 'Apartment Zone: "Two-family & multifamily = Both Special Permit only"'),
        "lot": (7500, 'B Residence Zone (smallest base district): "Min. lot size = 7,500 sq ft"'),
        "adu": ("administrative", '"ADU owner-occupancy = Required", no special-permit hearing noted'),
        "parking": (2, 'B Residence Zone: "Parking, two-family = 2 spaces/unit (4 total)"'),
        "demo": (90, '"Demolition delay = Up to 90 days for structures >50 years old and ≥500 sq ft"'),
    },
    "norwalk": {
        "use": ("capped_by_right", 'CD-2: "Two-family = P — permitted by right; multifamily still NP"'),
        "lot": (5000, 'CD-2 (smallest base district): "Min. lot size = 5,000 sq ft"'),
        "adu": ("by_right", 'CD-1S: "ADU = Permitted by-right with limitations"'),
        "parking": (0, '"Parking minimum = Not regulated for buildings of ≤16 units"'),
        "demo": (120, '"Demolition delay = Up to 120 days (2023 rewrite raised the ceiling from the 90-day state default)"'),
    },
    "redding": {
        "use": ("discretionary", 'RV (town\'s only multifamily zone): "Multifamily = Special Permit only, capped at 1 unit/8,000 sq ft"'),
        "lot": (43560, 'R-1 (general base district): "Min. lot size = 43,560 sq ft (1 acre)"'),
        "adu": ("special_permit", '"ADU approval pathway = Special Permit required (not by-right)"'),
        "parking": (2, '"Parking, single-family dwelling = 2 spaces/dwelling"'),
        "demo": (180, '"Demolition delay = 180 days (longer than most CT-4 towns\' 90-day default), enacted 2013"'),
    },
    "ridgefield": {
        "use": ("discretionary", 'MFDD: "Multifamily = Special Permit only — town\'s only multifamily pathway"'),
        "lot": (7500, 'R-7.5 (least restrictive base district): "Min. lot size = 7,500 sq ft"'),
        "adu": ("zoning_permit", '"ADU approval pathway = Zoning Permit (ZEO), not Special Permit"'),
        "parking": (2, 'RAAA: "Parking, one-/two-family = 2 spaces/unit"'),
        "demo": (90, '"Demolition delay = Up to 90 days for structures ≥50 years old"'),
    },
    "shelton": {
        "use": ("discretionary", 'R-4: "2-/3-family & multifamily (4-12 units) = Allowed by Special Exception" (functionally a special permit)'),
        "lot": (40000, 'R-1 (base district): "Min. lot size = 40,000 sq ft"'),
        "adu": ("by_right", '"ADU approval pathway = By-right on use table, subject to detailed standards"'),
        "parking": (2, '"Parking, 1–2 unit dwellings = 2 spaces/unit"'),
        "demo": (0, 'No Shelton-specific demolition-delay ordinance was located in available sources'),
    },
    "stamford": {
        "use": ("capped_by_right", 'R-6: "Two-family = Allowed by-right", but "Multifamily (3+) = Still prohibited"'),
        "lot": (5000, 'R-6 (smallest base district): "Min. lot size = 5,000 sq ft (1F)"'),
        "adu": ("administrative", 'Eligibility-restricted but no special-permit hearing noted; owner-occupancy required'),
        "parking": (2, 'R-20/R-6: "Parking, single-family house = 2 spaces"'),
        "demo": (20, 'Notice-to-deadline gaps of roughly 20–21 days observed in published legal notices (exact statutory period unconfirmed)'),
    },
    "stratford": {
        "use": ("by_right", 'RM-1: "2- and 3-family = Allowed BY RIGHT (P¹)"'),
        "lot": (7500, 'RS-4 (smallest single-family district, §3.2.1 table): "7,500" sq ft minimum area'),
        "adu": ("administrative", '"ADU approval pathway = Administrative review (A)"'),
        "parking": (1.5, 'RM-1: "Parking, multifamily (3+)" = 1.5 spaces/unit for a 2BR unit'),
        "demo": (90, 'Academy Hill Historic District: "Demolition delay = 90 days from permit issuance"'),
    },
    "trumbull": {
        "use": ("discretionary", 'MFO: "Multifamily = Special Permit only, existing I-L/I-L2 industrial land ≥10 acres", plus an active >50-unit application moratorium through Feb. 2027'),
        "lot": (21780, 'Residence A (smallest base district): "Min. lot size = 21,780 sq ft (½ acre)"'),
        "adu": ("zoning_permit", '"ADU approval pathway = Administrative (ZEO) if within existing footprint; Special Permit otherwise"'),
        "parking": (2.0, 'MFO: "Parking = 1.8 spaces/1BR unit, 2.0 spaces/2BR unit"'),
        "demo": (None, 'A Demolition Review Committee exists and is active, but no specific waiting-period length could be confirmed'),
    },
    "weston": {
        "use": ("discretionary", 'R-2A (entire base zone) bans 2-/3-/4+-family outright; VD-R: "All uses, incl. multifamily = Require Special Permit"'),
        "lot": (87120, 'R-2A (base zone): "Min. lot size = 2 acres"'),
        "adu": ("administrative", 'Owner-occupancy affidavit required, no special-permit hearing noted'),
        "parking": (0, 'Village District: parking is "stated as a cap, not a minimum" — no off-street minimum actually required'),
        "demo": (None, 'A delay ordinance is referenced on permit applications, but the exact waiting period could not be confirmed'),
    },
    "westport": {
        "use": ("capped_by_right", 'Residence C: "Two-family = Allowed BY RIGHT", but capped at "120 total dwelling units under this zone" town-wide'),
        "lot": (5000, 'Residence C (smallest by-right single-family district, §18-3): "Each lot within a Res. C shall have a minimum area of 5,000 square feet"'),
        "adu": ("administrative", 'Residence AAA: structural ADU permitted without owner-occupancy, no special-permit hearing noted'),
        "parking": (0, '"Parking, developments ≤16 units = No minimum (2026 amendment, §34-14.1)"'),
        "demo": (180, '"Demolition delay = 180 days for structures ≥50 years old (raised from 90 days in 2008)"'),
    },
    "wilton": {
        "use": ("narrow_by_right", 'HODD allows multifamily by-right, but only on specially-zoned "9–11 acres" sites; the R-2A base zone bans multifamily entirely'),
        "lot": (87120, 'R-2A (base zone): "Min. lot size = 2 acres (87,120 sq ft)"'),
        "adu": ("administrative", 'Annual owner-occupancy certification required, no special-permit hearing noted'),
        "parking": (2, 'R-2A single-family (the dominant residential use): "Single-family dwellings — 2 per dwelling unit, plus 1 per guest sleeping room" (§29-8.B.5.a(1)); the multifamily <17-unit exemption is a narrower case'),
        "demo": (90, '"Demolition delay = Up to 90 days for structures >50 years old and >500 sq ft"'),
    },
}

def compute_hap_score(slug):
    inputs = SCORE_INPUTS[slug]
    use_tier, use_note = inputs["use"]
    lot_sqft, lot_note = inputs["lot"]
    adu_tier, adu_note = inputs["adu"]
    parking_spaces, parking_note = inputs["parking"]
    demo_days, demo_note = inputs["demo"]

    factors = [
        {"category": U, "label": "Multifamily Access", "tier": use_tier,
         "input_value": use_tier.replace("_", " "), "note": use_note,
         "points": USE_PERMISSIONS_RUBRIC[use_tier], "max_points": 30},
        {"category": AP, "label": "Approval Discretion", "tier": use_tier,
         "input_value": use_tier.replace("_", " "), "note": use_note,
         "points": APPROVAL_PROCESS_RUBRIC[use_tier], "max_points": 10},
        {"category": D, "label": "Minimum Lot Size", "tier": "scaled",
         "input_value": (f"{lot_sqft:,} sq ft" if lot_sqft else "no minimum"), "note": lot_note,
         "points": lot_size_points(lot_sqft), "max_points": 20},
        {"category": A, "label": "ADU Approval Pathway", "tier": adu_tier,
         "input_value": adu_tier.replace("_", " "), "note": adu_note,
         "points": ADU_PATHWAY_RUBRIC[adu_tier], "max_points": 15},
        {"category": P, "label": "Parking Mandate", "tier": "scaled",
         "input_value": f"{parking_spaces} spaces/unit", "note": parking_note,
         "points": parking_points(parking_spaces), "max_points": 10},
        {"category": OA, "label": "Demolition Delay", "tier": "scaled",
         "input_value": (f"{demo_days} days" if demo_days is not None else "not independently confirmed"),
         "note": demo_note, "points": demolition_points(demo_days), "max_points": 15},
    ]

    scored = [f for f in factors if f["points"] is not None]
    achieved = sum(f["points"] for f in scored)
    max_total = sum(f["max_points"] for f in scored)
    composite = round(achieved / max_total * 100, 1) if max_total else 0.0

    unscored_n = len(factors) - len(scored)
    renorm_note = (
        f" {unscored_n} of 6 components had no independently-confirmed input for this town "
        f"and were excluded; the composite is renormalized over the remaining {len(scored)}."
        if unscored_n else ""
    )

    return {
        "composite": composite,
        "factors": factors,
        "methodology_note": (
            "Computed from the Variables table on this page, not from the NZA data below. "
            "Six weighted components (Multifamily Access 30pts, Approval Discretion 10pts, "
            "Minimum Lot Size 20pts, ADU Approval Pathway 15pts, Parking Mandate 10pts, "
            "Demolition Delay 15pts) are each scored against a fixed, published rubric from "
            "a specific cited fact above. Higher = more restrictive." + renorm_note
        ),
    }

for slug in TOWNS:
    TOWNS[slug]["hap_score"] = compute_hap_score(slug)

# ================= V2: PER-DISTRICT SCORES, LAND-WEIGHTED =================
# Each district is scored with the same six-component rubric as the town score, using only
# that district's own rules. Inputs that could not be confirmed for a district are None and
# the district score renormalizes over the components that were confirmed. Town V2 score is
# the land-area-weighted mean of the included districts' scores (acres from data/land_area).
LAND_DIR = os.path.join(ROOT, "data", "land_area")

V2_DISTRICTS = {
    "bridgeport": {
        "N1": {"use": "none", "approval": "none", "lot": 0, "adu": "by_right", "parking": 0, "demo": None,
               "note": "House A only (one unit per lot); no lot-area minimum (45 ft width); ADU by right per N1 rule; parking none citywide"},
        "N2": {"use": "discretionary", "approval": "discretionary", "lot": 0, "adu": "special_permit", "parking": 0, "demo": None,
               "note": "House B only: 1 principal unit, 2 with special permit (§3.100.9); no lot-area minimum (45 ft width); accessory apartment only as backyard cottage with special permit; parking none citywide"},
        "N3": {"use": "none", "approval": "none", "lot": 9000, "adu": "by_right", "parking": 0, "demo": None,
               "note": "House C only; 9,000 sq ft minimum lot (§3.110); up to 2 accessory units, 1 in house and/or 1 in backyard cottage, by right (§3.110 table); the general rule in §4.70.2(B)(2) caps accessory apartments at one per lot, so the second unit is unresolved"},
        "N4": {"use": "none", "approval": "none", "lot": 7500, "adu": "by_right", "parking": 0, "demo": None,
               "note": "House D only; 7,500 sq ft minimum lot (§3.120); 1 accessory apartment in house or backyard cottage, by right (§3.120 table)"},
        "NX1": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 0, "adu": "by_right", "parking": 0, "demo": None,
                "note": "House A, Row (4 units max) and Double House A permitted by right with administrative site plan; no lot-area minimum (45 ft width for House A); House A allows up to 3 units plus 1 backyard-cottage unit (§3.90.9); size cap 49% of principal GFA or 800 sq ft (§4.70.2). Row amendment 25-06 was still pending in 2025"},
        "NX2": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 0, "adu": "by_right", "parking": 0, "demo": None,
                "note": "Small General, Row (8 units max), Double House A and House A permitted by right with administrative site plan; no lot-area minimum; House A allows up to 4 units plus 1 backyard-cottage unit (§3.90.9)"},
        "NX3": {"use": "by_right", "approval": "by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "General Building (3 units minimum, no maximum) by right (§3.50.9); no lot-area row in the General Building table; accessory apartments are not listed because multi-unit buildings are already allowed"},
        "NX4": {"use": "by_right", "approval": "by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "General Building (3 units minimum, no maximum) by right (§3.50.9, NX3/NX4 column); no lot-area row in the General Building table"},
        "DX1": {"use": "by_right", "approval": "by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "Storefront building type, no limit on principal units (§3.20.9); downtown form-based district, no lot-area row"},
        "DX2": {"use": "by_right", "approval": "by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "General Building (3 units minimum, no maximum) by right (§3.50.9)"},
        "MX1": {"use": "by_right", "approval": "by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "Storefront building type, no limit on principal units (§3.20.9)"},
        "MX2": {"use": "by_right", "approval": "by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "Storefront building type, no limit on principal units (§3.20.9)"},
        "MXN": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "Storefront building type capped at 8 principal units (§3.20.9)"},
        "RX2": {"use": "by_right", "approval": "by_right", "lot": 0, "adu": "n/a", "parking": 0, "demo": None,
                "note": "General Building (3 units minimum, no maximum) by right (§3.50.9)"},
    },
    "stamford": {
        "RA-3": {"use": "none", "approval": "none", "lot": 130680, "adu": "zoning_permit", "parking": 3, "demo": None,
                 "note": "One Family Residence District (§5.X.3); single-family only; ADU by zoning permit (ADU def., 2024 text, §4): lot ≥10,000 sq ft, 800 sq ft cap, 1 ADU parking space; single-family parking is 3 in Parking Category 3 (Table 12.7), which is everything outside the mapped downtown areas (Map 12.8)"},
        "RA-2": {"use": "none", "approval": "none", "lot": 87120, "adu": "zoning_permit", "parking": 3, "demo": None,
                 "note": "One Family Residence District (§5.X.3); single-family only; ADU by zoning permit, lot ≥10,000 sq ft; parking as RA-3"},
        "RA-1": {"use": "none", "approval": "none", "lot": 43560, "adu": "zoning_permit", "parking": 3, "demo": None,
                 "note": "One Family Residence District (§5.X.3); single-family only; ADU by zoning permit, lot ≥10,000 sq ft; parking as RA-3"},
        "R-20": {"use": "none", "approval": "none", "lot": 20000, "adu": "zoning_permit", "parking": 3, "demo": None,
                 "note": "One Family, single-family only; ADU by zoning permit (lot ≥10,000 sq ft); parking as RA-3"},
        "R-10": {"use": "none", "approval": "none", "lot": 10000, "adu": "zoning_permit", "parking": 3, "demo": None,
                 "note": "One Family Residence District, 10,000 sq ft minimum (§5.Y.3); ADU by zoning permit at exactly the 10,000 sq ft threshold; parking as RA-3"},
        "R-7 1/2": {"use": "none", "approval": "none", "lot": 7500, "adu": "zoning_permit", "parking": 3, "demo": None,
                    "note": "One Family Residence District, 7,500 sq ft minimum (§5.Y.3); ADU by zoning permit only on lots of at least 10,000 sq ft (ADU def., §4), so lots of 7,500 to 9,999 sq ft cannot have one; scored at the qualifying-lot tier, as R-10 and R-20; parking 3 (Category 3), though parts near downtown are Category 1 or 2"},
        "R-6": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 5000, "adu": "zoning_permit", "parking": 2, "demo": None,
                "note": "One- and Two-Family (§5.Z); two-family detached by right, multiple dwellings prohibited; 5,000 sq ft one-family minimum, 6,000 sq ft two-family (§5.Z.4(a)); ADU by zoning permit only on lots of at least 10,000 sq ft (ADU def., §4); parking scored at the Category 1/2 value of 2 because much of R-6 lies in the West Side, East Side and South End areas of Map 12.8 (Category 3 would be 3)"},
        "R-5": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 5000, "adu": "zoning_permit", "parking": 1.75, "demo": None,
                "note": "R-5 Multi-Family Medium Density: multi-family is a permitted use; projects on lots under 30,000 sq ft are reviewed by the Zoning Enforcement Officer, larger ones by the Zoning Board (§5.AA); one-family lot 5,000 sq ft (multi-family 9,000); parking scored at the 2-bedroom market-rate multifamily value (Table 12.7); ADU by zoning permit on single-family lots (ADU def., §4)"},
        "RM-1": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 5000, "adu": "zoning_permit", "parking": 1.75, "demo": None,
                 "note": "RM-1 Multi-Family Residence: single-family, two-family and multi-family dwellings permitted (§5.EE.3); 5,000 sq ft minimum lot, 3,750 sq ft per dwelling unit (§5.EE.5); parking and ADU as R-5"},
        "R-MF": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 5000, "adu": "zoning_permit", "parking": 1.75, "demo": None,
                 "note": "R-MF Multi-Family Residence Design District: projects on lots under 20,000 sq ft are reviewed by the Zoning Enforcement Officer, larger ones by the Zoning Board (§5.FF.2); 5,000 sq ft minimum lot, 2,000 sq ft per dwelling unit (§5.FF.6); parking and ADU as R-5"},
    },
    "greenwich": {
        "RA-4": {"use": "none", "approval": "none", "lot": 174240, "adu": "zoning_permit", "parking": None, "demo": 90,
                 "note": "Single-family only (Sec. 6-93); 4-acre minimum (div. 21 table); ADU by zoning permit, external ADU up to 1,200 sq ft (§6-99(3)(D)); ADU adds 1 dedicated off-street space (§6-99(3)(F)); single-family parking (§6-154) sets no number, so it is not scored; demolition: 90-day ceiling for pre-1940 buildings of 500 sq ft or more (Municipal Code §6-316, from the town's web page, not the mirrored zoning text)"},
        "RA-2": {"use": "none", "approval": "none", "lot": 87120, "adu": "zoning_permit", "parking": None, "demo": 90,
                 "note": "Single-family only (Sec. 6-93); 2-acre minimum; ADU by zoning permit, external ADU up to 1,200 sq ft (§6-99(3)(D)); single-family parking sets no number; demolition as RA-4"},
        "RA-1": {"use": "none", "approval": "none", "lot": 43560, "adu": "zoning_permit", "parking": None, "demo": 90,
                 "note": "Single-family only (Sec. 6-93); 1-acre minimum; ADU by zoning permit, external ADU up to 1,000 sq ft (§6-99(3)(D)); single-family parking sets no number; demolition as RA-4"},
        "R-20": {"use": "none", "approval": "none", "lot": 20000, "adu": "zoning_permit", "parking": None, "demo": 90,
                 "note": "Single-family only (Sec. 6-93); 20,000 sq ft minimum; ADU by zoning permit, external ADU up to 1,000 sq ft (§6-99(3)(D)); single-family parking sets no number; demolition as RA-4"},
        "R-12": {"use": "none", "approval": "none", "lot": 12000, "adu": "zoning_permit", "parking": None, "demo": 90,
                 "note": "Single-family only (Sec. 6-93); 12,000 sq ft minimum; ADU by zoning permit, external ADU up to 800 sq ft (§6-99(3)(D)); single-family parking sets no number; demolition as RA-4"},
        "R-7": {"use": "none", "approval": "none", "lot": 7500, "adu": "zoning_permit", "parking": None, "demo": 90,
                "note": "Sec. 6-97: uses of RA-4 only plus §6-94; 7,500 sq ft minimum (div. 21 table); ADU by zoning permit, external ADU up to 800 sq ft (§6-99(3)(D)); single-family parking sets no number; demolition as RA-4"},
        "R-6": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 7500, "adu": "zoning_permit", "parking": None, "demo": 90,
                "note": "Sec. 6-98: two-family by administrative site plan approval on lots ≥7,500 sq ft; 7,500 sq ft minimum (div. 21 table); ADU external up to 800 sq ft; single-family parking sets no number (two-family parking in §6-155 is one garage plus one outdoor space per dwelling); demolition as RA-4"},
        "R-MF": {"use": "discretionary", "approval": "discretionary", "lot": 3600, "adu": None, "parking": 2, "demo": 90,
                 "note": "Two-family / multifamily by Special Permit (§6-98.1); lot area 3,600 sq ft for single and two-family, 2,400 sq ft per family for multifamily (div. 21 table); parking one garage plus one outdoor space per 1-2 bedroom dwelling (§6-155(1)(a); the 2026 PA 25-1 amendment may remove this for projects under 17 units); the ADU section lists no R-MF rule, so ADU is not scored; demolition as RA-4"},
    },
    "norwalk": {
        "CD-1L": {"use": "none", "approval": "none", "lot": 43560, "adu": "zoning_permit", "parking": 2, "demo": 120,
                  "note": "Sub-Urban Large Lot; multifamily and two-family not permitted (Table 4.3.9.A); 43,560 sq ft (Table 4.3.1); ADU by zoning permit when it meets principal-building setbacks (§4.3.9.G.4); 2 spaces per dwelling unit (Table 4.3.12.B-1); demolition: 120-day maximum delay (City Code §55-5, adopted 4-24-1984, not a mirrored PDF)"},
        "CD-1M": {"use": "none", "approval": "none", "lot": 12500, "adu": "zoning_permit", "parking": 2, "demo": 120,
                  "note": "Sub-Urban Medium Lot; multifamily and two-family not permitted; 12,500 sq ft (Table 4.3.1); ADU by zoning permit; 2 spaces per dwelling unit; demolition as CD-1L"},
        "CD-1S": {"use": "none", "approval": "none", "lot": 6250, "adu": "zoning_permit", "parking": 2, "demo": 120,
                  "note": "Sub-Urban Single-Family; multifamily and two-family not permitted; 6,250 sq ft (Table 4.3.1); ADU by zoning permit; 2 spaces per dwelling unit; demolition as CD-1L"},
        "CD-2": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 5000, "adu": "zoning_permit", "parking": 2, "demo": 120,
                 "note": "Sub-Urban Single- and Two-Family; two-family detached permitted, multifamily not; 5,000 sq ft (Table 4.3.1); ADU by zoning permit; 2 spaces per dwelling unit; demolition as CD-1L"},
        "CD-3": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 0, "adu": "zoning_permit", "parking": 1.3, "demo": 120,
                 "note": "General Urban: large and small multifamily permitted with limitations (14-29 units need site plan approval, over 29 a special permit; §4.3.9.G.4); no lot-area minimum (Table 4.3.1 shows NR); 1.3 spaces per dwelling unit; ADU permitted with limitations (Table 4.3.9.D); demolition as CD-1L; acreage is CD-3 from the user-confirmed crosswalk (old D and NB), CD-3W is not separable"},
    },
}

V2_LOOKUP_NORMALIZE = lambda s: s.replace(" ", "").replace("½", "1/2").upper()

# Verbatim citations for V2 district inputs. Each quote is checked against the mirrored
# PDF's extracted text at build time; a quote that is not found stops the build.
V2_SOURCES = {
    "bridgeport": ("bridgeport-zoning.pdf", "Zone Bridgeport form-based code (amended July 2022)", "https://portal.ct.gov/-/media/CSC/1_Dockets-medialibrary/1_MEDIA_DO500_600/DO516/ApplicantSubmissions/Application/UI---City-of-Bridgeport-Zoning-Code-Amended-July-25-2022.pdf"),
    "stamford": ("stamford-zoning.pdf", "Zoning Regulations, City of Stamford (through July 10, 2024)", "https://stamfordct.gov/home/showpublisheddocument/5847/638568338177670000"),
    "greenwich-div9": ("greenwich-div9.pdf", "Building Zone Regulations, Div. 9 (Use Regs, Aug. 2023)", "https://www.greenwichct.gov/DocumentCenter/View/37828"),
    "greenwich-div21": ("greenwich-div21.pdf", "Building Zone Regulations, Div. 21 (Bulk Schedule)", "https://www.greenwichct.gov/DocumentCenter/View/37841"),
    "norwalk-art4": ("norwalk-art4.pdf", "Norwalk Zoning Regulations, Art. 4 (Building & Lot/Building Site Standards, compiled 9/23/2025)", "https://www.norwalkct.gov/DocumentCenter/View/32250"),
    "norwalk-usetable": ("norwalk-usetable.pdf", "Norwalk Zoning Regulations, Use Table extract (7/10/26; ADU text rev. eff. 4/24/26)", "https://norwalkct.gov/DocumentCenter/View/38584"),
    "greenwich-div2": ("greenwich-div2.pdf", "Building Zone Regulations, Div. 2 (Administrative Provisions and Definitions, Sec. 6-5)", "https://www.greenwichct.gov/DocumentCenter/View/37821"),
    "greenwich-div6": ("greenwich-div6.pdf", "Building Zone Regulations, Div. 6 (R-PHD-SU, amended 4-24-2013)", "https://www.greenwichct.gov/DocumentCenter/View/37825"),
    "greenwich-div15": ("greenwich-div15.pdf", "Building Zone Regulations, Div. 15 (Parking and Garages, Aug. 2023)", "https://www.greenwichct.gov/DocumentCenter/View/37834"),
    "norwalk": ("norwalk-art3.pdf", "Norwalk Zoning Regulations, Art. 3 (Zoning Districts, eff. Feb. 2024)", "https://www.norwalkct.gov/DocumentCenter/View/32245"),
}

# (district, field) -> (source key, citation, verbatim quote)
V2_CITES = {
    ("bridgeport", "N1", "use"): ("bridgeport", "§3.90 House A, Number of Principal Units", "Number of Principal Units 1 in House"),
    ("bridgeport", "N1", "adu"): ("bridgeport", "§3.90 House A, Number of Accessory Apartments", "Number of Accessory Apartments 1 in House or Backyard Cottage"),
    ("bridgeport", "N2", "lot"): ("bridgeport", "§3.100 House B, Lot Size", "Lot Size No min."),
    ("bridgeport", "N2", "adu"): ("bridgeport", "§3.100 House B, Number of Accessory Apartments", "Number of Accessory Apartments 1 in Backyard Cottage with special permit"),
    ("bridgeport", "N3", "lot"): ("bridgeport", "§3.110 House C, Lot Size", "Lot Size 9000 sq. ft. min."),
    ("bridgeport", "N3", "adu"): ("bridgeport", "§3.110 House C, Number of Accessory Apartments", "Number of Accessory Apartments up to 2; 1 in House and/or 1 in Backyard Cottage"),
    ("bridgeport", "N4", "lot"): ("bridgeport", "§3.120 House D, Lot Size", "Lot Size 7500 sq. ft. min."),
    ("bridgeport", "N4", "adu"): ("bridgeport", "§3.120 House D, Number of Accessory Apartments", "Number of Accessory Apartments 1 in House or Backyard Cottage"),
    ("bridgeport", "NX1", "lot"): ("bridgeport", "§3.90 House A, Lot Width (N1/NX1/NX2 columns)", "Lot Width 45 ft. min. 45 ft. min. 35 ft. min."),
    ("bridgeport", "NX2", "lot"): ("bridgeport", "§3.90 House A, Lot Width (N1/NX1/NX2 columns)", "Lot Width 45 ft. min. 45 ft. min. 35 ft. min."),
    ("bridgeport", "NX1", "adu_size"): ("bridgeport", "§4.70.2(B)(5) accessory apartment size", "may not exceed 49% of the gross floor area of the"),
    ("bridgeport", "NX2", "adu_size"): ("bridgeport", "§4.70.2(B)(5) accessory apartment size", "may not exceed 49% of the gross floor area of the"),
    ("bridgeport", "NX2", "parking"): ("bridgeport", "§4.70.2(B)(6) accessory apartment parking", "No additional parking is required for an accessory apartment."),
    ("stamford", "RA-3", "lot"): ("stamford", "§5.X.3(a)(1) RA-3 minimum lot area", "(1) Minimum Lot Area: 130,680 sq. ft., designed to contain a circle 200 feet in diameter."),
    ("stamford", "RA-2", "lot"): ("stamford", "§5.X.3(b)(1) RA-2 minimum lot area", "(1) Minimum Lot Area: 87,120 sq. ft., designed to contain a circle 200 feet in diameter."),
    ("stamford", "RA-1", "lot"): ("stamford", "§5.X.3(c)(1) RA-1 minimum lot area", "(1) Minimum Lot Area: 43,560 sq. ft. designed to contain a circle 125 feet in diameter."),
    ("stamford", "R-20", "lot"): ("stamford", "§5.Y.3(a)(1) R-20 minimum lot area", "(1) Minimum Lot Area: 20,000 sq. ft., designed to contain a circle 100 feet in diameter."),
    ("stamford", "R-10", "lot"): ("stamford", "§5.Y.3(b)(1) R-10 minimum lot area", "(1) Minimum Lot Area: 10,000 sq. ft."),
    ("stamford", "R-7 1/2", "lot"): ("stamford", "§5.Y.3(c)(1) R-7½ minimum lot area", "(1) Minimum Lot Area: 7500 sq. ft."),
    ("stamford", "R-6", "lot"): ("stamford", "§5.Z.4(a) R-6 minimum lot area", "a. Minimum Lot Area: Single Family Dwelling 5000 sq. ft."),
    ("stamford", "RA-3", "adu"): ("stamford", "ADU definition, conditions 1 and 4", "Accessory Dwelling Units may only be permitted by Zoning Permit"),
    ("stamford", "RA-3", "adu_size"): ("stamford", "ADU definition, condition 6", "The size of the ADU shall not exceed eight hundred (800) sf in Gross Floor Area;"),
    ("stamford", "RA-3", "use"): ("stamford", "§5.X.1 Purpose, RA-3/RA-2/RA-1", "predominantly for single family"),
    ("greenwich", "RA-4", "use"): ("greenwich-div9", "§6-93(a)(1)", "Detached single family dwellings, one (1) per lot."),
    ("greenwich", "RA-4", "lot"): ("greenwich-div21", "Bulk schedule, RA-4 row", "4 Acres"),
    ("greenwich", "RA-2", "lot"): ("greenwich-div21", "Bulk schedule, RA-2 row", "2 Acres"),
    ("greenwich", "RA-1", "lot"): ("greenwich-div21", "Bulk schedule, RA-1 row", "1 Acre"),
    ("greenwich", "R-20", "lot"): ("greenwich-div21", "Bulk schedule, R-20 row", "20,000"),
    ("greenwich", "R-12", "lot"): ("greenwich-div21", "Bulk schedule, R-12 row", "12,000"),
    ("greenwich", "R-7", "lot"): ("greenwich-div21", "Bulk schedule, R-7 row", "7,500"),
    ("greenwich", "R-6", "lot"): ("greenwich-div21", "Bulk schedule, R-6 row", "7,500 sq. ft. 60 ft."),
    ("greenwich", "R-6", "use"): ("greenwich-div9", "§6-98(a)(3)(A)", "Administrative site plan approval is required on lots of 7,500 square feet or larger for: (A) New two-family dwellings"),
    ("greenwich", "R-7", "use"): ("greenwich-div9", "§6-97(a)(1)", "All uses permitted in RA-4 zones and uses permitted under Sec. 6-94."),
    ("greenwich", "R-MF", "use"): ("greenwich-div9", "§6-98.1(a)(2)", "The following uses are permitted as Special Permit uses"),
    ("greenwich", "RA-4", "adu_size"): ("greenwich-div9", "§6-99(3)(D)(i) external ADU cap", "1,000 square feet in RA-1 and R-20 zones; and 1,200 square feet in RA-2 and RA-4"),
    ("greenwich", "RA-2", "adu_size"): ("greenwich-div9", "§6-99(3)(D)(i) external ADU cap", "1,000 square feet in RA-1 and R-20 zones; and 1,200 square feet in RA-2 and RA-4"),
    ("greenwich", "RA-1", "adu_size"): ("greenwich-div9", "§6-99(3)(D)(i) external ADU cap", "1,000 square feet in RA-1 and R-20 zones; and 1,200 square feet in RA-2 and RA-4"),
    ("greenwich", "R-20", "adu_size"): ("greenwich-div9", "§6-99(3)(D)(i) external ADU cap", "1,000 square feet in RA-1 and R-20 zones; and 1,200 square feet in RA-2 and RA-4"),
    ("greenwich", "R-12", "adu_size"): ("greenwich-div9", "§6-99(3)(D)(i) external ADU cap", "External ADUs shall be limited to 800 square feet in R-12, R-7 and R-6 zones;"),
    ("greenwich", "R-7", "adu_size"): ("greenwich-div9", "§6-99(3)(D)(i) external ADU cap", "External ADUs shall be limited to 800 square feet in R-12, R-7 and R-6 zones;"),
    ("greenwich", "R-6", "adu_size"): ("greenwich-div9", "§6-99(3)(D)(i) external ADU cap", "External ADUs shall be limited to 800 square feet in R-12, R-7 and R-6 zones;"),
    ("greenwich", "R-6", "adu"): ("greenwich-div9", "§6-99(3)(E) special permit only for larger ADU", "Upon an application for a Special Permit, the Planning and Zoning Commission may authorize an ADU"),
}

# Rules stated once in the code apply to every district they cover.
for _d in ["RA-2", "RA-1", "R-20", "R-10", "R-7 1/2"]:
    V2_CITES[("stamford", _d, "adu")] = V2_CITES[("stamford", "RA-3", "adu")]
    V2_CITES[("stamford", _d, "adu_size")] = V2_CITES[("stamford", "RA-3", "adu_size")]
V2_CITES[("stamford", "R-6", "adu")] = V2_CITES[("stamford", "RA-3", "adu")]
V2_CITES[("stamford", "R-6", "use")] = ("stamford", "Zoning district list, R-6", "R-6               One-Family, Two-Family Residence District")
for _d in ["RA-4", "RA-2", "RA-1", "R-20", "R-12", "R-7", "R-6"]:
    V2_CITES[("greenwich", _d, "adu")] = ("greenwich-div9", "§6-99(3)(J) ADU zoning permit", "prior to the issuance of a zoning permit.")
for _d in ["RA-2", "RA-1", "R-20", "R-12", "R-7", "R-6"]:
    V2_CITES[("greenwich", _d, "adu_size")] = V2_CITES[("greenwich", "RA-4", "adu_size")] if _d in ("RA-2", "RA-1", "R-20") else V2_CITES[("greenwich", "R-6", "adu_size")]
for _d in ["RA-2", "RA-1", "R-20", "R-12", "R-7", "R-6"]:
    V2_CITES[("greenwich", _d, "use")] = V2_CITES.get(("greenwich", _d, "use"), ("greenwich-div9", "§6-93(a)(1)", "Detached single family dwellings, one (1) per lot."))
# Citations added after the district-by-district fact check (Nov. 2026).
_BP_PARKING = ("bridgeport", "§8.20.1 Parking", "This zoning code does not establish minimum off-street")
for _d in V2_DISTRICTS["bridgeport"]:
    V2_CITES[("bridgeport", _d, "parking")] = _BP_PARKING
V2_CITES[("bridgeport", "N2", "use")] = ("bridgeport", "§3.100.9 House B, Number of Principal Units", "Number of Principal Units 1 in House, 2 with special permit")
for _d, _sec in (("N3", "§3.110.9"), ("N4", "§3.120.9")):
    V2_CITES[("bridgeport", _d, "use")] = ("bridgeport", f"{_sec} House {'C' if _d == 'N3' else 'D'}, Number of Principal Units", "Number of Principal Units 1 in House")
for _d in ("NX1", "NX2"):
    V2_CITES[("bridgeport", _d, "use")] = ("bridgeport", "§3.70.4 Row, Facade Width per Street Frontage (NX1 / NX2 / NX3 columns)", "4 units max. 8 units max. 10 units max.")
V2_CITES[("bridgeport", "NX1", "adu")] = ("bridgeport", "§3.90.9 House A, units in House (NX1 column)", "up to 3 in House plus 1")
V2_CITES[("bridgeport", "NX2", "adu")] = ("bridgeport", "§3.90.9 House A, units in House (NX2 column)", "up to 4 in House plus 1")
for _d in ("NX3", "NX4", "DX2", "RX2"):
    V2_CITES[("bridgeport", _d, "use")] = ("bridgeport", "§3.50.9 General Building, Number of Principal Units", "Number of Principal Units 3 min. 3 min.")
for _d in ("DX1", "MX1", "MX2", "MXN"):
    V2_CITES[("bridgeport", _d, "use")] = ("bridgeport", "§3.20.9 Storefront, Number of Principal Units (DX1 / MX1 / MX2 / MXN columns)", "Number of Principal Units No limits No limits No limits 8 max.")

_ST_SF_PARKING = ("stamford", "§12.D.2 Table 12.7, single-family house, market rate (Category 1 / 2 / 3)", "Single family 2 2 1 2 2 1 3 2 1 house")
_ST_MF_PARKING = ("stamford", "§12.D.2 Table 12.7, 2-bedroom apartment, market rate (Category 1 / 2 / 3)", "2 BR -Apt 1.25 1 0.33 1.75 1 0.33 1.75 1.5 0.75")
for _d in ("RA-3", "RA-2", "RA-1", "R-20", "R-10", "R-7 1/2", "R-6"):
    V2_CITES[("stamford", _d, "parking")] = _ST_SF_PARKING
for _d in ("R-5", "RM-1", "R-MF"):
    V2_CITES[("stamford", _d, "parking")] = _ST_MF_PARKING
    V2_CITES[("stamford", _d, "adu")] = V2_CITES[("stamford", "RA-3", "adu")]
V2_CITES[("stamford", "R-6", "use")] = ("stamford", "§5.Z.2 R-6 permitted uses", "Multiple Dwellings are specifically prohibited.")
V2_CITES[("stamford", "R-5", "use")] = ("stamford", "§5.AA.2 R-5 site plan review", "R-5 projects located on Lots of less than 30,000 square feet shall be subject to")
V2_CITES[("stamford", "R-5", "lot")] = ("stamford", "§5.AA.5(a) R-5 minimum lot area", "One Family Dwelling: 5000 sq. ft.")
V2_CITES[("stamford", "RM-1", "use")] = ("stamford", "§5.EE.3 RM-1 permitted uses", "Dwellings - single family, two family and multi-family.")
V2_CITES[("stamford", "RM-1", "lot")] = ("stamford", "§5.EE.5(a) RM-1 minimum lot area", "a. Minimum Lot Area: 5000 sq. ft.")
V2_CITES[("stamford", "R-MF", "use")] = ("stamford", "§5.FF.2 R-MF site plan review", "R-MF projects located on Lots of less than 20,000 square feet")
V2_CITES[("stamford", "R-MF", "lot")] = ("stamford", "§5.FF.6(a) R-MF minimum lot area", "a. Minimum Lot Area: 5,000 square feet")

V2_CITES[("greenwich", "R-MF", "parking")] = ("greenwich-div15", "§6-155(1)(a) two-family and multifamily parking", "Dwelling with one or two bedrooms*: one garage space for each dwelling and one outdoor space for each dwelling.")
V2_CITES[("greenwich", "R-MF", "lot")] = ("greenwich-div21", "Bulk schedule, R-MF row", "R-MF 2-1/2 35 ft. 3,600 60 ft.")

_NW_USE_ROW = ("norwalk-usetable", "Table 4.3.9.A Large Multifamily Building row (CD-1L / 1M / 1S / 2 / 3 ... columns)", "Large Multifamily NP NP NP NP PL NP PL PL PL NP NP NP NP SPU NP Building")
_NW_ADU = ("norwalk-usetable", "§4.3.9.G.4.a(3) ADU permitting procedures", "a. Permitted by Zoning Permit in accordance")
_NW_PARK = ("norwalk-art4", "Table 4.3.12.B-1 single-family and two-family parking", "2 per Dwelling Unit; except that within the CD-3, CD-3W,")
_NW_LOT = {"CD-1L": "43,560 sq. ft.", "CD-1M": "12,500 sq. ft.", "CD-1S": "6,250 sq. ft.", "CD-2": "5,000 sq. ft.", "CD-3": "NR"}
for _d in ("CD-1L", "CD-1M", "CD-1S", "CD-3"):
    V2_CITES[("norwalk", _d, "use")] = _NW_USE_ROW
V2_CITES[("norwalk", "CD-2", "use")] = ("norwalk-usetable", "Table 4.3.9.A Two-Family Detached Dwelling row", "Two-Family Detached NP NP NP P P P P NP NP NP NP NP NP NP NP Dwelling")
for _d, _q in _NW_LOT.items():
    V2_CITES[("norwalk", _d, "lot")] = ("norwalk-art4", f"Table 4.3.1 {_d} Lot/Building Site Area", f"Lot/Building Site Area {_q}")
    V2_CITES[("norwalk", _d, "adu")] = _NW_ADU
    V2_CITES[("norwalk", _d, "parking")] = _NW_PARK
V2_CITES[("norwalk", "CD-3", "parking")] = ("norwalk-art4", "Table 4.3.12.B-1 multifamily parking", "Large Multifamily Building and Small Multifamily Building 1.3 per Dwelling Unit")

# Greenwich: districts outside the single-family zones that permit dwellings (Sec. 6-110 business zones,
# WB, R-PHD-SU). Conservation zones, R-PR and R-PHD-E stay out because their ADU rule is not addressed.
_BIZ_NOTE = ("Use Group 3 dwellings permitted in {z} under Sec. 6-110(c)(1); no cap on number of units (6-110(f)(1)); "
             "4 units or fewer need only site plan, 5 or more need special permit + site plan (6-110(F)(1)-(2)); "
             "no numeric minimum lot area in the Sec. 6-205(b) table (area cell reads 'Note 1', which points to 6-110(a), a purpose clause); "
             "{extra}; ADU not applicable because multi-unit buildings are already permitted; parking for multifamily follows Sec. 6-155 (6-110(e)(1)); demolition not scored")

V2_DISTRICTS_GREENWICH_ADD = {
    "LB":   {"use": "capped_by_right", "approval": "discretionary", "lot": 0, "adu": "n/a", "parking": None, "demo": None,
             "note": _BIZ_NOTE.format(z="LB", extra="ground-floor dwellings prohibited unless waived with below-market units (6-110(d)(1)); height 2.5 stories/35 ft")},
    "LBR-2": {"use": "capped_by_right", "approval": "discretionary", "lot": 0, "adu": "n/a", "parking": None, "demo": None,
              "note": _BIZ_NOTE.format(z="LBR-2", extra="dwellings only above the ground floor (6-110(c)(1)B)")},
    "CGB":  {"use": "capped_by_right", "approval": "discretionary", "lot": 0, "adu": "n/a", "parking": None, "demo": None,
             "note": _BIZ_NOTE.format(z="CGB", extra="ground-floor residential permitted (6-110(d)(1)); Use Group 3 listed in 6-104.1(B)")},
    "CGBR": {"use": "capped_by_right", "approval": "discretionary", "lot": 0, "adu": "n/a", "parking": None, "demo": None,
             "note": _BIZ_NOTE.format(z="CGBR (spelled 'CBGR' in 6-110(c)(1))", extra="dwellings only above the ground floor (6-103.1(C), 6-110(c)(1)B)")},
    "GB":   {"use": "capped_by_right", "approval": "discretionary", "lot": 0, "adu": "n/a", "parking": None, "demo": None,
             "note": _BIZ_NOTE.format(z="GB", extra="ground-floor residential permitted (6-110(d)(1)); Use Group 3 listed in 6-105(a)")},
    "GBO":  {"use": "capped_by_right", "approval": "discretionary", "lot": 0, "adu": "n/a", "parking": None, "demo": None,
             "note": _BIZ_NOTE.format(z="GBO", extra="ground-floor residential permitted (6-110(d)(1)); Use Group 3 listed in 6-106(a)")},
    "WB":   {"use": "discretionary", "approval": "discretionary", "lot": 20000, "adu": "prohibited", "parking": None, "demo": None,
             "note": "Multi-family dwellings are Use Group 7c, special permit required (6-100, 6-107(b)); 20,000 sq ft minimum lot for multifamily (6-107(e)(4)(A)); net density 1 unit per 4,200 sq ft and 15% moderate-income units above 5 units (6-107(e)(4)(D)); no dwellings in FEMA V-zones; ADU 'prohibited' is an inference: the Sec. 6-5(18.1) definition allows an ADU only on a property containing or zoned for a single-family dwelling, and WB lists no single-family use"},
    "R-PHD-SU": {"use": "capped_by_right", "approval": "capped_by_right", "lot": 1800, "adu": "n/a", "parking": None, "demo": None,
             "note": "Multi-family dwellings only (6-70(a)); zone exists only where mapped in the Plan of Development after a Commission hearing and plan approval, then built to that plan; density by lot area per unit type (1,800 sq ft for efficiency/1-BR, 3,000 sq ft for 2-BR; 1,350/2,250 for 8-30g applications), building area <=20% and FAR <=0.5; lot=1,800 is the smallest per-unit land requirement, there is no stand-alone minimum lot size; parking per 6-155"},
}

V2_CITES_GREENWICH_ADD = {}
_BIZ_USE = ("greenwich-div9", "§6-110(F)(1)-(2) procedure for business-zone dwellings (page 9-45)",
            "A site plan application is required when the development proposal is four (4) units or fewer, and/or the building’s size does not trigger a special permit as required pursuant to Section 6-101, and/or the development does not use any of the incentives outlined in Section 6-110(c). (2) A special permit and site plan are required when the development proposal is five (5) units or more")
_BIZ_LOT = ("greenwich-div21", "§6-205(b) Business Zones schedule, Note 1 (minimum lot AREA cell for LB, LBR, CGB, CGBR, GB, GBO) (page 21-5)",
            "Note 1. See Sec. 6-110(a) (6/11/86)")
_BIZ_ADU = ("greenwich-div9", "§6-110(f)(1) no limit on number of dwelling units (page 9-44/9-45)",
            "There are not limits on the number of dwelling units permitted within those structures.")
for _d in ["LB", "LBR-2", "CGB", "CGBR", "GB", "GBO"]:
    V2_CITES_GREENWICH_ADD[("greenwich", _d, "use")] = _BIZ_USE
    V2_CITES_GREENWICH_ADD[("greenwich", _d, "lot")] = _BIZ_LOT
    V2_CITES_GREENWICH_ADD[("greenwich", _d, "adu")] = _BIZ_ADU
# Zone-listing quote (verified, usable as the 'use' quote instead if a single zone-naming quote is preferred):
#   ("greenwich-div9", "§6-110(c)(1) (page 9-42)", "Dwelling units are permitted within residential or mixed-use development in the LB, LBR-2, CGB, CBGR, GB and GBO zones provided the units comply")

V2_CITES_GREENWICH_ADD[("greenwich", "WB", "use")] = ("greenwich-div9", "§6-107(b) Permitted uses, Use Group 7c (multi-family is a 7c use per §6-100) (page 9-29)", "Use Group 7c (special permit required)")
V2_CITES_GREENWICH_ADD[("greenwich", "WB", "lot")] = ("greenwich-div9", "§6-107(e)(4)(A) multifamily minimum lot (page 9-30)", "All multi-family residential developments shall have a minimum lot size of 20,000 square feet")
V2_CITES_GREENWICH_ADD[("greenwich", "WB", "adu")] = ("greenwich-div2", "§6-5(18.1) ADU definition (page 2-3)", "An ADU is only permitted on a residential property currently containing or zoned for a single-family dwelling unit")

V2_CITES_GREENWICH_ADD[("greenwich", "R-PHD-SU", "use")] = ("greenwich-div6", "§6-70(a) R-PHD-SU use regulations (page 6-3)", "The principal permitted use shall be: (1) Multi-family dwellings only.")
V2_CITES_GREENWICH_ADD[("greenwich", "R-PHD-SU", "lot")] = ("greenwich-div6", "§6-64(c) minimum lot area per unit type (page 6-2)", "1 Room-Efficiency 450 sq. ft. 1800 sq. ft.")
V2_CITES_GREENWICH_ADD[("greenwich", "R-PHD-SU", "adu")] = ("greenwich-div6", "§6-70(a) multi-family only", "The principal permitted use shall be: (1) Multi-family dwellings only.")


V2_DISTRICTS["greenwich"].update(V2_DISTRICTS_GREENWICH_ADD)
V2_CITES.update(V2_CITES_GREENWICH_ADD)

# Historic-overlay (-HO) polygons keep their base zone's regulations (Sec. 6-109(b)(7)), so their acreage is
# folded into the base zone instead of being scored separately.
V2_ACRE_FOLD = {"greenwich": {"RA-2-HO": "RA-2", "RA-1-HO": "RA-1", "R-20-HO": "R-20", "R-12-HO": "R-12", "R-7-HO": "R-7", "R-6-HO": "R-6",
           "LB-HO": "LB", "CGB-HO": "CGB", "GB-HO": "GB", "CGBR-HO": "CGBR", "LBR-2-HO": "LBR-2",
           "R-C7-HO": "R-C7", "RC-20-HO": "R-C20", "RC-12-HO": "R-C12", "RA-CC4-HO": "RA-CC4", "LBR-1-HO": "LBR-1"}}

# Stamford: districts outside the single-family zones that permit dwellings (Appendix A Table I, Appendix B
# Tables II and III, and each design district's own section of Article 5).
_STAMFORD_ADDED = {
    # R-H: 115.8 acres. Status: include. Source: PDF text pp. 5-105 to 5-107 (Article 5.CC); Appendix B Table II (B-1)
    'R-H': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 5000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'R-H Multiple Family High Density Design (§5.CC): all R-MF as-of-right uses incl. multi-family (§5.CC.3, App. A Table I); lots under 20,000 sq ft follow R-MF (5,000 sq ft minimum, 2,000 sq ft per unit; 1,250 on 20,000+; 725 on 1+ acre); Zoning Enforcement Officer reviews most applications, Zoning Board reviews lots of one acre or more (§5.CC.2, 5.CC.5.c); multi-unit by right so ADU pathway is not applicable'},
    # C-N: 167.8 acres. Status: include. Source: PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
    'C-N': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 5000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'C-N Neighborhood Commercial (App. A Table I): multi-family is a check-mark (as-of-right) use, capped by density of 2,500 sq ft of land per family (App. B Table III); minimum plot 5,000 sq ft; site plan approval may apply (App. A legend); multi-unit by right so ADU pathway not applicable'},
    # C-B: 38.3 acres. Status: include. Source: PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
    'C-B': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 5000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'C-B Community Business (App. A Table I): multi-family is a check-mark (as-of-right) use, capped by density of 1,500 sq ft of land per family (App. B Table III); minimum plot 5,000 sq ft; site plan approval may apply (App. A legend); multi-unit by right so ADU pathway not applicable'},
    # C-L: 73.9 acres. Status: include. Source: PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
    'C-L': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 4000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'C-L Limited Commercial (App. A Table I): multi-family is a check-mark (as-of-right) use, capped by density of 1,250 sq ft of land per family (App. B Table III); minimum plot 4,000 sq ft; site plan approval may apply (App. A legend); multi-unit by right so ADU pathway not applicable'},
    # C-I: 37.5 acres. Status: include. Source: PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
    'C-I': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 4000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'C-I Intermediate Commercial (App. A Table I): multi-family is a check-mark (as-of-right) use, capped by density of 1,250 sq ft of land per family (App. B Table III); minimum plot 4,000 sq ft; site plan approval may apply (App. A legend); multi-unit by right so ADU pathway not applicable'},
    # C-G: 65.5 acres. Status: include. Source: PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
    'C-G': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 4000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'C-G General Commercial (App. A Table I): multi-family is a check-mark (as-of-right) use, capped by density of 1,000 sq ft of land per family (500 sq ft for R-MF-type residential-only buildings, App. B fn 4) (App. B Table III); minimum plot 4,000 sq ft; site plan approval may apply (App. A legend); multi-unit by right so ADU pathway not applicable'},
    # CC: 144.2 acres. Status: include. Source: PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
    'CC': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 4000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'CC Central City (App. A Table I): multi-family is a check-mark (as-of-right) use, capped by density of 450 sq ft of land per family (400 sq ft downtown mixed use by Special Permit, App. B fn 4) (App. B Table III); minimum plot 4,000 sq ft; site plan approval may apply (App. A legend); multi-unit by right so ADU pathway not applicable'},
    # R-HD: 40.5 acres. Status: include. Source: PDF text pp. 5-110 to 5-116 (Article 5.DD)
    'R-HD': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 5000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'R-HD Residential High Density (§5.DD): apartment house, multiple dwelling and town houses authorized as-of-right (§5.DD.3); lots under one acre 5,000 sq ft minimum, one acre or more 43,560 sq ft (§5.DD.4); density by FAR 2.5/3.75 and 1,000 sq ft per market-rate unit; Zoning Board site plan approval on parcels of 20,000 sq ft or more, Land Use Bureau Chief below that (§5.DD.5.d); multi-unit by right so ADU not applicable'},
    # NX-D: 16.2 acres. Status: include. Source: PDF text pp. 5-73 to 5-83 (Article 5.U)
    'NX-D': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 5000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'NX-D Neighborhood Mixed Use Design (§5.U): Dwelling Multiple allowed as of right (§5.U.2); minimum lot 5,000 sq ft for 1- and 2-family, 6,000 sq ft for 3+ family; 1,000 sq ft residential density divider and FAR 1.5 (§5.U.3); Zoning Board site plan review above 20,000 sq ft of lot, Land Use Bureau Chief administrative review below (§5.U.5.e); multi-unit by right so ADU not applicable'},
    # V-C: 75.6 acres. Status: include. Source: PDF text pp. 5-155 to 5-165 (Article 5.JJ)
    'V-C': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 5000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'V-C Village Commercial (§5.JJ): on land beyond 125 ft of Commercial Streets the same uses as R-MF are permitted (§5.JJ.2.b), within 125 ft in Glenbrook/Springdale C-N uses except single- and two-family; minimum lot 5,000 sq ft (§5.JJ.3); Zoning Board Special Permit and site plan only for substantial new construction (over 20,000 sq ft of floor area), otherwise administrative (§5.JJ.f); multi-unit by right so ADU not applicable'},
    # MX-D: 31.8 acres. Status: include. Source: PDF text pp. 5-67 to 5-68 (Article 5.T)
    'MX-D': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 87120, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'MX-D Mixed Use Development (§5.T): Apartment House, Two-Family and Multiple Dwellings permitted subject to Zoning Board authorization within site plan review (§5.T.3); FAR cap 3.0 (§5.T.4); no lot minimum stated, so lot is the two-acre minimum site for designation (§5.T.2) -- JUDGMENT, see report; multi-unit permitted so ADU not applicable'},
    # P-D: 10.4 acres. Status: include. Source: PDF text pp. 5-85 to 5-86 (Article 5.W)
    'P-D': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 30000, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'P-D Planned Development (§5.W): Apartment House or Dwelling permitted subject to Zoning Board authorization as part of site plan review (§5.W.3); density cap 75/108 units per acre (§5.W.4); no lot minimum stated, so lot is the 30,000 sq ft minimum site for designation (§5.W.2) -- JUDGMENT; multi-unit permitted so ADU not applicable'},
    # SRD-N: 22.6 acres. Status: include. Source: PDF text pp. 5-126 to 5-131 (Article 5.GG)
    'SRD-N': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 871200, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'SRD-N South End Redevelopment North (§5.GG): uses are those of SRD-S (which lists Dwelling, Multiple) (§5.GG.4.a); density 50 units per acre (§5.GG.5.a); design district so Zoning Board site and architectural review (§1.B.6); no lot minimum stated, so lot is the 20-acre minimum Zoning Tract (§5.GG.3.b) -- JUDGMENT (a tract threshold, not a building-lot minimum; consider None); ADU not applicable'},
    # SRD-S: 67.5 acres. Status: include. Source: PDF text pp. 5-132 to 5-142 (Article 5.HH)
    'SRD-S': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 871200, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'SRD-S South End Redevelopment South (§5.HH): Dwelling, Multiple allowed (§5.HH.4.a); density 50 units per acre (§5.HH.5.a); design district so Zoning Board site plan review (§1.B.6, §5.HH); no lot minimum stated, so lot is the 20-acre minimum Zoning Tract (§5.HH.3.b) -- JUDGMENT (consider None); ADU not applicable'},
    # TCDD: 56.7 acres. Status: include. Source: PDF text pp. 5-143 to 5-154 (Article 5.II)
    'TCDD': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 0, "adu": 'n/a', "parking": None, "demo": None,
           "note": 'TCD-D Transportation Center Design (§5.II): Dwelling Multiple and town houses permitted (§5.II.3); minimum lot none for zoning lots under one acre, 43,560 sq ft for one acre or more (§5.II.4.a); density by FAR and 700-800 sq ft residential density divider; design district so Zoning Board site and architectural review (§1.B.6); ADU not applicable'},
    # B-D: 10.7 acres. Status: include (flagged). Source: PDF text pp. 5-6 to 5-8 (Article 5.B)
    'B-D': {"use": 'discretionary', "approval": 'discretionary', "lot": 5000, "adu": 'prohibited', "parking": None, "demo": None,
           "note": 'B-D Designed Business (§5.B): residential apartments only on the second floor above commercial uses, lots up to 20,000 sq ft, subject to Zoning Board approval after public hearing (§5.B.3.f, 5.B.4); lot size governed by the C-N schedule (5,000 sq ft); no single-family dwelling is authorized, and the ADU rule requires one (ADU def. cond. 4), so ADU is scored prohibited -- INFERRED'},
    # C-D: 257.1 acres. Status: include (flagged). Source: PDF text pp. 5-11 to 5-14 (Article 5.E)
    'C-D': {"use": 'discretionary', "approval": 'discretionary', "lot": 653400, "adu": 'zoning_permit', "parking": None, "demo": None,
           "note": 'C-D Designed Commercial (§5.E): single-, two- and multi-family dwellings only in contiguous C-D districts with more than 50 acres, and every use only by Special Permit (§5.E.3); density 12-14 units per acre (§5.E.4.c); no lot minimum stated, so lot is the 15-acre minimum designation area (§5.E.2) -- JUDGMENT; single-family is a (Special Permit) use so the generic ADU zoning permit applies; whether any mapped C-D parcel group exceeds 50 acres is not verified'},
    # CW-D: 56.9 acres. Status: include (flagged). Source: PDF text pp. 5-24 to 5-28 (Article 5.K)
    'CW-D': {"use": 'discretionary', "approval": 'discretionary', "lot": 4000, "adu": 'prohibited', "parking": None, "demo": None,
           "note": 'C-WD Coastal Water Dependent (§5.K): multi-family residences only by Special Permit as non-water-dependent uses subordinate to a water-dependent use or as adaptive reuse of existing buildings (§5.K.2.b(3), 5.K.8); minimum lot 4,000 sq ft (§5.K.3.a); no single-family dwelling authorized so ADU scored prohibited -- INFERRED'},
    # DW-D: 43.6 acres. Status: include (flagged). Source: PDF text pp. 5-29 to 5-38 (Article 5.L)
    'DW-D': {"use": 'discretionary', "approval": 'discretionary', "lot": 10000, "adu": 'prohibited', "parking": None, "demo": None,
           "note": "DW-D Designed Waterfront (§5.L): Dwelling, Multiple, town houses and apartments only by Special Permit in the Board's sole discretion (§5.L.3); minimum lot 10,000 sq ft (§5.L.4.a); density up to 44 units per acre with BMR bonus; no single-family dwelling authorized so ADU scored prohibited -- INFERRED"},
}
V2_DISTRICTS["stamford"].update(_STAMFORD_ADDED)
# R-H: source PDF text pp. 5-105 to 5-107 (Article 5.CC); Appendix B Table II (B-1)
V2_CITES[("stamford", 'R-H', 'use')] = ("stamford", '§5.CC.3 R-H authorized uses', 'for all of the uses permitted as-of-right in the R-MF')
V2_CITES[("stamford", 'R-H', 'lot')] = ("stamford", 'Appendix B Table II, R-H row (first line: 5,000 sq ft plot area, 50 ft frontage, 2,000 sq ft per family)', 'R-H 5000 50 - 2000 - 4 40 30 15 40 8 18 30')
V2_CITES[("stamford", 'R-H', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'R-H', 'approval')] = ("stamford", '§5.CC.2 R-H review procedure', 'All other R-H applications shall be subject to review and approval by the Zoning Enforcement Officer.')
# C-N: source PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
V2_CITES[("stamford", 'C-N', 'use')] = ("stamford", 'Appendix A Table I, Dwelling, Multi-Family row (symbols run RA-3..M-G; check mark under C-N)', 'Dwelling, Multi‐Family ‐ ‐ ‐ ‐ ‐ ‐ ‐ √ √ √ √ √ √ √ √ √ √ ‐ ‐')
V2_CITES[("stamford", 'C-N', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'C-N', 'approval')] = ("stamford", 'Appendix A Table I legend, check-mark definition', 'Indicates a Use that is permitted as‐of‐right in the respective district, but Site Plan or Large‐Scale Development Plan approval pursuant to')
V2_CITES[("stamford", 'C-N', 'lot')] = ("stamford", 'Appendix B Table III, C-N row (first figure = minimum plot area)', 'C-N(15) 5000 50 2500(15.1,4) 0.3 2 25 30')
# C-B: source PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
V2_CITES[("stamford", 'C-B', 'use')] = ("stamford", 'Appendix A Table I, Dwelling, Multi-Family row (symbols run RA-3..M-G; check mark under C-B)', 'Dwelling, Multi‐Family ‐ ‐ ‐ ‐ ‐ ‐ ‐ √ √ √ √ √ √ √ √ √ √ ‐ ‐')
V2_CITES[("stamford", 'C-B', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'C-B', 'approval')] = ("stamford", 'Appendix A Table I legend, check-mark definition', 'Indicates a Use that is permitted as‐of‐right in the respective district, but Site Plan or Large‐Scale Development Plan approval pursuant to')
V2_CITES[("stamford", 'C-B', 'lot')] = ("stamford", '§5.C.3(a) C-B minimum lot area', 'a. Minimum Lot Area: 5,000 square feet')
# C-L: source PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
V2_CITES[("stamford", 'C-L', 'use')] = ("stamford", 'Appendix A Table I, Dwelling, Multi-Family row (symbols run RA-3..M-G; check mark under C-L)', 'Dwelling, Multi‐Family ‐ ‐ ‐ ‐ ‐ ‐ ‐ √ √ √ √ √ √ √ √ √ √ ‐ ‐')
V2_CITES[("stamford", 'C-L', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'C-L', 'approval')] = ("stamford", 'Appendix A Table I legend, check-mark definition', 'Indicates a Use that is permitted as‐of‐right in the respective district, but Site Plan or Large‐Scale Development Plan approval pursuant to')
V2_CITES[("stamford", 'C-L', 'lot')] = ("stamford", 'Appendix B Table III, C-L row (first figure = minimum plot area)', 'C-L 4000 40 1250(4) 1.0(13) 4(13) 45(13)')
# C-I: source PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
V2_CITES[("stamford", 'C-I', 'use')] = ("stamford", 'Appendix A Table I, Dwelling, Multi-Family row (symbols run RA-3..M-G; check mark under C-I)', 'Dwelling, Multi‐Family ‐ ‐ ‐ ‐ ‐ ‐ ‐ √ √ √ √ √ √ √ √ √ √ ‐ ‐')
V2_CITES[("stamford", 'C-I', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'C-I', 'approval')] = ("stamford", 'Appendix A Table I legend, check-mark definition', 'Indicates a Use that is permitted as‐of‐right in the respective district, but Site Plan or Large‐Scale Development Plan approval pursuant to')
V2_CITES[("stamford", 'C-I', 'lot')] = ("stamford", 'Appendix B Table III, C-I row (first figure = minimum plot area)', 'C-I(5) 4000 40 1250(4)(9) 1.2(9) 5 55(9)')
# C-G: source PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
V2_CITES[("stamford", 'C-G', 'use')] = ("stamford", 'Appendix A Table I, Dwelling, Multi-Family row (symbols run RA-3..M-G; check mark under C-G)', 'Dwelling, Multi‐Family ‐ ‐ ‐ ‐ ‐ ‐ ‐ √ √ √ √ √ √ √ √ √ √ ‐ ‐')
V2_CITES[("stamford", 'C-G', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'C-G', 'approval')] = ("stamford", 'Appendix A Table I legend, check-mark definition', 'Indicates a Use that is permitted as‐of‐right in the respective district, but Site Plan or Large‐Scale Development Plan approval pursuant to')
V2_CITES[("stamford", 'C-G', 'lot')] = ("stamford", 'Appendix B Table III, C-G row (first figure = minimum plot area)', 'C-G(3.2) 4000 40 1000(4) 1.8(13) - 100(1')
# CC: source PDF text A-1 to A-9 (Appendix A Table I, dwelling rows; PDF pages 436-441) and B-2 (Appendix B Table III); Art. 5.C-5.I just cross-reference App. A/B
V2_CITES[("stamford", 'CC', 'use')] = ("stamford", 'Appendix A Table I, Dwelling, Multi-Family row (symbols run RA-3..M-G; check mark under CC)', 'Dwelling, Multi‐Family ‐ ‐ ‐ ‐ ‐ ‐ ‐ √ √ √ √ √ √ √ √ √ √ ‐ ‐')
V2_CITES[("stamford", 'CC', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'CC', 'approval')] = ("stamford", 'Appendix A Table I legend, check-mark definition', 'Indicates a Use that is permitted as‐of‐right in the respective district, but Site Plan or Large‐Scale Development Plan approval pursuant to')
V2_CITES[("stamford", 'CC', 'lot')] = ("stamford", 'Appendix B Table III, CC row (first figure = minimum plot area)', 'CC (3.2) 4000 40 450(4) 2.0(13,23,24) -(')
# R-HD: source PDF text pp. 5-110 to 5-116 (Article 5.DD)
V2_CITES[("stamford", 'R-HD', 'use')] = ("stamford", '§5.DD.3 R-HD authorized uses', 'Apartment House or Dwelling')
V2_CITES[("stamford", 'R-HD', 'lot')] = ("stamford", '§5.DD.4(a) R-HD minimum lot size (lots less than one acre)', 'a. Minimum Lot Size 5,000 sf')
V2_CITES[("stamford", 'R-HD', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'R-HD', 'approval')] = ("stamford", '§5.DD.5.d(1) R-HD reviewing authority', 'On parcels 20,000 sf and larger, the Zoning Board shall review and determine compliance')
# NX-D: source PDF text pp. 5-73 to 5-83 (Article 5.U)
V2_CITES[("stamford", 'NX-D', 'use')] = ("stamford", '§5.U.2 NX-D as-of-right uses, item 19.1', '19.1 Dwelling, Multiple R')
V2_CITES[("stamford", 'NX-D', 'lot')] = ("stamford", '§5.U.3 NX-D development standards, minimum lot size (1-2 family column first)', 'Minimum 5,000 square feet 6,000 square feet')
V2_CITES[("stamford", 'NX-D', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'NX-D', 'approval')] = ("stamford", '§5.U.5.e(2) NX-D reviewing authority', 'The Land Use Bureau Chief shall conduct an administrative site plan and architectural')
# V-C: source PDF text pp. 5-155 to 5-165 (Article 5.JJ)
V2_CITES[("stamford", 'V-C', 'use')] = ("stamford", '§5.JJ.2(b) V-C authorized uses', 'the same uses as in the R-MF District shall be permitted.')
V2_CITES[("stamford", 'V-C', 'lot')] = ("stamford", '§5.JJ.3(a) V-C minimum lot size', 'a. Minimum Lot 5,000 sf 5,000 sf 5,000sf 5,000sf')
V2_CITES[("stamford", 'V-C', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'V-C', 'approval')] = ("stamford", '§5.JJ f. V-C reviewing authority', 'The Zoning Board shall review and determine compliance with the standards of the V-C')
# MX-D: source PDF text pp. 5-67 to 5-68 (Article 5.T)
V2_CITES[("stamford", 'MX-D', 'use')] = ("stamford", '§5.T.3 MX-D permitted uses', 'a. Agencies; Apartment House or Dwelling; Dwelling, Two-Family;')
V2_CITES[("stamford", 'MX-D', 'lot')] = ("stamford", '§5.T.2 MX-D minimum area (designation threshold, not a per-lot minimum)', 'shall be two acres (87,120 square feet) in area')
V2_CITES[("stamford", 'MX-D', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'MX-D', 'approval')] = ("stamford", '§5.T.3 MX-D approval', 'shall be subject to Zoning Board authorization for each use as a part of site plan review and approval')
# P-D: source PDF text pp. 5-85 to 5-86 (Article 5.W)
V2_CITES[("stamford", 'P-D', 'use')] = ("stamford", '§5.W.3 P-D permitted uses', 'Hotel, Extended Stay; Apartment House or Dwelling;')
V2_CITES[("stamford", 'P-D', 'lot')] = ("stamford", '§5.W.2 P-D minimum area (designation threshold)', 'shall be 30,000 square feet in area')
V2_CITES[("stamford", 'P-D', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'P-D', 'approval')] = ("stamford", '§5.W.3 P-D approval', 'subject Zoning Board authorization for each as a part of its site plan review and approval')
# SRD-N: source PDF text pp. 5-126 to 5-131 (Article 5.GG)
V2_CITES[("stamford", 'SRD-N', 'use')] = ("stamford", '§5.GG.4(a) SRD-N uses (incorporates SRD-S use list)', 'Uses permitted within the SRD-S District with the same Floor Area limitations contained therein')
V2_CITES[("stamford", 'SRD-N', 'lot')] = ("stamford", '§5.GG.3(b) SRD-N minimum acreage (designation threshold)', 'not less than twenty (20) contiguous acres in area')
V2_CITES[("stamford", 'SRD-N', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'SRD-N', 'approval')] = ("stamford", '§1.B.6 Design Districts', 'All Development and Redevelopment in Design Districts (marked with an asterisk (“*”) on the List of Zoning Districts in Subsection 1.B.1.) shall be subject to Site and Architectural Plan Review')
# SRD-S: source PDF text pp. 5-132 to 5-142 (Article 5.HH)
V2_CITES[("stamford", 'SRD-S', 'use')] = ("stamford", '§5.HH.4(a) SRD-S permitted uses', 'Houses; Dwelling, Multiple; Emergency Shelter')
V2_CITES[("stamford", 'SRD-S', 'lot')] = ("stamford", '§5.HH.3(b) SRD-S minimum acreage (designation threshold)', 'single ownership or control, not less than twenty (20) acres in area')
V2_CITES[("stamford", 'SRD-S', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'SRD-S', 'approval')] = ("stamford", '§1.B.6 Design Districts', 'All Development and Redevelopment in Design Districts (marked with an asterisk (“*”) on the List of Zoning Districts in Subsection 1.B.1.) shall be subject to Site and Architectural Plan Review')
# TCDD: source PDF text pp. 5-143 to 5-154 (Article 5.II)
V2_CITES[("stamford", 'TCDD', 'use')] = ("stamford", '§5.II.3 TCD-D permitted uses', 'Dwelling Multiple • Dwelling - Group or Town Houses')
V2_CITES[("stamford", 'TCDD', 'lot')] = ("stamford", '§5.II.4(a) TCD-D minimum lot size (lots under one acre)', 'a. Minimum Lot size none')
V2_CITES[("stamford", 'TCDD', 'adu')] = ("stamford", 'ADU definition, condition 9', 'No Multiple-Family Dwelling, including but not limited to legally non-conforming two- and three-family Dwellings, shall be eligible for Accessory Dwelling Units;')
V2_CITES[("stamford", 'TCDD', 'approval')] = ("stamford", '§1.B.6 Design Districts', 'All Development and Redevelopment in Design Districts (marked with an asterisk (“*”) on the List of Zoning Districts in Subsection 1.B.1.) shall be subject to Site and Architectural Plan Review')
# B-D: source PDF text pp. 5-6 to 5-8 (Article 5.B)
V2_CITES[("stamford", 'B-D', 'use')] = ("stamford", '§5.B.3(f) B-D residential apartments', 'f. Subject to approval by the Zoning Board, residential apartments may be permitted on the second floor above commercial uses')
V2_CITES[("stamford", 'B-D', 'lot')] = ("stamford", '§5.B.3(e) B-D lot size by reference to C-N (5,000 sq ft, App. B Table III)', 'Lot size and Yard space shall be governed by the requirements for the C-N Neighborhood Business District')
V2_CITES[("stamford", 'B-D', 'adu')] = ("stamford", 'ADU definition, condition 4 (single-family principal dwelling required)', 'ADUs shall only be permitted on Lots containing no more than one (1) Single-Family Dwelling and which have a Lot Area of at least 10,000sf;')
V2_CITES[("stamford", 'B-D', 'approval')] = ("stamford", '§5.B.4 B-D procedure', 'who shall not approve same until after a public hearing.')
# C-D: source PDF text pp. 5-11 to 5-14 (Article 5.E)
V2_CITES[("stamford", 'C-D', 'use')] = ("stamford", '§5.E.3(c) C-D residential uses', 'Dwellings in contiguous C-D districts with more than 50 acres')
V2_CITES[("stamford", 'C-D', 'lot')] = ("stamford", '§5.E.2 C-D minimum area (designation threshold)', 'shall be fifteen (15) acres')
V2_CITES[("stamford", 'C-D', 'adu')] = ("stamford", 'ADU definition, preamble (zoning permit)', 'Accessory Dwelling Units may only be permitted by Zoning Permit')
V2_CITES[("stamford", 'C-D', 'approval')] = ("stamford", '§5.E.3 C-D permitted uses', 'Any use in the C-D District shall be permitted only by Special Permit.')
# CW-D: source PDF text pp. 5-24 to 5-28 (Article 5.K)
V2_CITES[("stamford", 'CW-D', 'use')] = ("stamford", '§5.K.2(b)(3) C-WD special permit uses', '(3) Retail, office, multi-family residences, senior housing, service establishments, and')
V2_CITES[("stamford", 'CW-D', 'lot')] = ("stamford", '§5.K.3(a) C-WD minimum lot area', 'a. Minimum Lot Area: 4,000 square feet')
V2_CITES[("stamford", 'CW-D', 'adu')] = ("stamford", 'ADU definition, condition 4 (single-family principal dwelling required)', 'ADUs shall only be permitted on Lots containing no more than one (1) Single-Family Dwelling and which have a Lot Area of at least 10,000sf;')
V2_CITES[("stamford", 'CW-D', 'approval')] = ("stamford", '§5.K.2 C-WD authorized uses', 'subject to the issuance of a Special Permit in accordance with the standards of Subsections 5.K.4. and 5.K.6. herein:')
# DW-D: source PDF text pp. 5-29 to 5-38 (Article 5.L)
V2_CITES[("stamford", 'DW-D', 'use')] = ("stamford", '§5.L.3(b) DW-D additional uses', 'Dwelling, Group or Town Houses • Dwelling, Multiple')
V2_CITES[("stamford", 'DW-D', 'lot')] = ("stamford", '§5.L.4(a) DW-D minimum lot size', 'a. Minimum Lot Size: 10,000 sq. ft.')
V2_CITES[("stamford", 'DW-D', 'adu')] = ("stamford", 'ADU definition, condition 4 (single-family principal dwelling required)', 'ADUs shall only be permitted on Lots containing no more than one (1) Single-Family Dwelling and which have a Lot Area of at least 10,000sf;')
V2_CITES[("stamford", 'DW-D', 'approval')] = ("stamford", '§5.L.3 DW-D permitted uses', 'the Board, in its sole discretion, determines such uses to be appropriate')

# A minimum area needed to designate a district (MX-D, P-D, SRD-N, SRD-S, C-D) is not a per-lot minimum, and an
# ADU rule inferred from a definition is not quoted text, so those inputs stay unconfirmed and the districts out.
for _d in ("MX-D", "P-D", "SRD-N", "SRD-S", "C-D"):
    V2_DISTRICTS["stamford"][_d]["lot"] = None
for _d in ("B-D", "CW-D", "DW-D"):
    V2_DISTRICTS["stamford"][_d]["adu"] = None
# Multi-family by right already allows several units, so no separate ADU pathway applies (same rule as R-H).
for _d in ("R-5", "RM-1", "R-MF"):
    V2_DISTRICTS["stamford"][_d]["adu"] = "n/a"
    V2_CITES[("stamford", _d, "adu")] = V2_CITES[("stamford", "R-H", "adu")]
# Designed-residential (R-D) overlay polygons keep their base district's uses and density (Sec. 5.BB.2.b-c).
V2_ACRE_FOLD["stamford"] = {"R-10/R-D": "R-10", "R-20/R-D": "R-20", "RA-1/R-D": "RA-1", "RA-2/R-D": "RA-2"}

# Easton: Residence A and Residence B only.
_EASTON_SOURCES = {
    "easton": ("easton-zoning.pdf", "Easton Zoning Regulations (last revised July 7, 2024)", "https://ct-easton.civicplus.com/DocumentCenter/View/3109"),
}

# Layer codes: RA ("Residential A") and RB ("Residential B") only; no other zones in the layer.
_EASTON_DISTRICTS = {
    "easton": {
        "Residence A": {"use": "none", "approval": "none", "lot": 40000, "adu": "zoning_permit", "parking": 2, "demo": None,
                        "note": "Single-family dwelling only, one per lot (§3230.1); multifamily and two-family are not listed and unlisted uses are prohibited (§1420); 40,000 sq ft minimum lot (§3510); ADU, attached or detached, by staff zoning permit (§3320.2, §3450.2) subject to §5200 (owner occupancy, size caps); single-family parking 2.0 spaces (§6221), ADU adds 2.0; no demolition delay found in the regulations"},
        "Residence B": {"use": "none", "approval": "none", "lot": 130680, "adu": "zoning_permit", "parking": 2, "demo": None,
                        "note": "Same use rules as Residence A (§3230.1); 3.0 acre (130,680 sq ft) minimum lot (§3510); ADU by staff zoning permit; detached ADU size cap depends on buildable area (§5220.2.b); parking as Residence A"},
    },
}

_EZ = "easton"
_USE = (_EZ, "§3230.1 Residential-Related Uses (printed p.23)", "Dwelling ‐ Single family dwelling, not to exceed one dwelling per lot.")
_ADU = (_EZ, "§3320.2 Accessory Dwelling Unit, Attached (printed p.24); detached ADU §3450.2 (p.45)", "Accessory Dwelling Unit, Attached – An accessory dwelling unit within or attached")
_PARK = (_EZ, "§6221 Minimum parking requirements, single-family dwelling (printed p.70)", "Single‐family dwelling                         2.0 spaces")
_EASTON_CITES = {
    ("easton", "Residence A", "use"): _USE,
    ("easton", "Residence B", "use"): _USE,
    # approval: no multifamily pathway, so the approval tier is the same 'none' as use; same quote
    ("easton", "Residence A", "approval"): (_EZ, "§1420 Prohibited if not permitted (printed p.3)", "Any use or activity within a zoning district which is not explicitly permitted by these Regulations shall be deemed to be prohibited within such district."),
    ("easton", "Residence B", "approval"): (_EZ, "§1420 Prohibited if not permitted (printed p.3)", "Any use or activity within a zoning district which is not explicitly permitted by these Regulations shall be deemed to be prohibited within such district."),
    ("easton", "Residence A", "lot"): (_EZ, "§3510 Lot Area table, Residence A (printed p.31)", "Minimum Lot Area                                 40,000 square feet"),
    ("easton", "Residence B", "lot"): (_EZ, "§3510 Lot Area table, Residence B (printed p.31)", "130,680 square feet"),
    ("easton", "Residence A", "adu"): _ADU,
    ("easton", "Residence B", "adu"): _ADU,
    ("easton", "Residence A", "parking"): _PARK,
    ("easton", "Residence B", "parking"): _PARK,
    # demo: None for both. The regulations contain no demolition-delay provision (only an enforcement reference to a "demolition order" in the plot-plan section).
}

V2_SOURCES.update(_EASTON_SOURCES)
V2_DISTRICTS.update(_EASTON_DISTRICTS)
V2_CITES.update(_EASTON_CITES)

# Monroe: single-family zones RF-1, RF-2, RF-3 and the rural residence zone RR.
V2_SOURCES["monroe"] = ("monroe-zoning.pdf", 'Monroe Zoning Regulations (amended through July 2, 2026)', 'https://www.monroect.gov/Home/DownloadDocument?docId=82b32408-e8ae-4afd-b9ca-58f87c1e35da')
V2_DISTRICTS_MONROE = {
    # MF/ADU/use rows: §10.1 Schedule, Use Schedule p.5-6. Lot: Art. 3. Parking: §10.2 Schedule p.9 (and §6.1.19 caps 17+ unit projects at 1 / 2 spaces).
    "RF-1": {"use": "none", "approval": "none", "lot": 43560, "adu": "zoning_permit", "parking": 2.0, "demo": None,
             "note": "Multi-Family Dwelling not permitted; single-family 1 per lot by right; 1 acre minimum (§3.1.4(A)); ADU is an accessory use ('ACC') needing a Certificate of Use signed by ZEO, Building Inspector, Sanitarian and Fire Marshal (§6.9.2(H)), attached only, owner-occupied; no demolition delay found"},
    "RF-2": {"use": "none", "approval": "none", "lot": 87120, "adu": "zoning_permit", "parking": 2.0, "demo": None,
             "note": "Same use rules as RF-1; 2 acre minimum (§3.2.4(A)); ADU as RF-1"},
    "RF-3": {"use": "none", "approval": "none", "lot": 130680, "adu": "zoning_permit", "parking": 2.0, "demo": None,
             "note": "Same use rules as RF-1; 3 acre minimum (§3.3.4(A)); ADU as RF-1 but detached ADU also allowed, new construction reviewed by the Commission (§6.9.1(B))"},
    "MFR": {"use": "discretionary", "approval": "discretionary", "lot": 3049200, "adu": "prohibited", "parking": 2.0, "demo": None,
            "note": "Multi-Family Dwelling by Special Exception Permit only; floating district needing a 70-acre parcel (§3.4.5(B)) = 3,049,200 sq ft; 2.5 attached units/gross acre; MF units capped at 10% of town single-family count (§3.4.2(A)); accessory apartment 'x'"},
    "ARR": {"use": "discretionary", "approval": "discretionary", "lot": 435600, "adu": "prohibited", "parking": 2.0, "demo": None,
            "note": "Only age-restricted (55+) attached/detached dwellings, by Special Exception Permit; Multi-Family 'x'; 10 acre minimum (§3.5.5(B)) = 435,600 sq ft; 5 attached units/gross acre; accessory apartment 'x'. Age restriction narrows the housing type - judgment call whether to score"},
    "HOD": {"use": "discretionary", "approval": "discretionary", "lot": 871200, "adu": "prohibited", "parking": 2.0, "demo": None,
            "note": "Multi-Family Dwelling by Special Exception Permit; floating district rezoned from a 20-25 acre parcel (§3.7.6(B)) = 871,200 sq ft; 1.5 units/gross acre; 30-year affordable set-aside (§3.7); accessory apartment 'x'"},
    "RR": {"use": "none", "approval": "none", "lot": 32670, "adu": "prohibited", "parking": 2.0, "demo": None,
           "note": "Single-family only (SEP); Multi-Family 'x'; individual lot 3/4 acre = 32,670 sq ft within a 25-acre minimum parcel (§3.6.5(B),(D)); accessory apartment 'x'"},
}

# Not residential-capable on their own (excluded): B-1, B-2, SB-2, LOR (Multi-Family 'x'/'X'; Single-Family 'x'; only SDP mixed-use,
# defined as 2-9 units above ground-floor commercial, eligibility tied to the MDD overlay, §8.2.3(T)); I-1..I-3; AH (not mapped; SDP only, §5.3);
# MDD overlay (not a base district; multi-family on 15+ acre projects by Special Exception, §5.4.6).

_MO_MF = ("monroe", "§10.1 Schedule of Permitted Land Uses, Multi-Family Dwelling row (columns RF-1 RF-2 RF-3 ARR MFR RR HOD AH ...), Use Schedule p.5",
          "Multi-Family Dwelling x x x x SEP x SEP X x x X x x x x")
_MO_ADU = ("monroe", "§10.1 Schedule, Accessory Apartment row (columns RF-1 RF-2 RF-3 ARR MFR RR HOD AH), Use Schedule p.6",
           "Accessory Apartment ACC ACC ACC x x x x X")
_MO_PARK = ("monroe", "§10.2 Schedule of Required Off-Street Parking, Residential, Off-Street Parking Schedule p.9",
            "Two-Bedroom or more 2.0 spaces per unit with adequate driveway turnaround.")
V2_CITES_MONROE = {}
for _d in ("RF-1", "RF-2", "RF-3", "MFR", "ARR", "HOD", "RR"):
    V2_CITES_MONROE[("monroe", _d, "use")] = _MO_MF
    V2_CITES_MONROE[("monroe", _d, "adu")] = _MO_ADU
    V2_CITES_MONROE[("monroe", _d, "parking")] = _MO_PARK
for _d in ("RF-1", "RF-2", "RF-3"):   # ADU process, Art. 6 p.65 (§6.9.2(H)(1)); size/attachment §6.9.1 p.64
    V2_CITES_MONROE[("monroe", _d, "adu")] = _MO_ADU
V2_CITES_MONROE[("monroe", "RF-1", "lot")] = ("monroe", "§3.1.4(A) RF-1 minimum lot area, Art. 3", "Each lot shall have a minimum area of one (1) acre (or 43,560 square feet)")
V2_CITES_MONROE[("monroe", "RF-2", "lot")] = ("monroe", "§3.2.4(A) RF-2 minimum lot area, Art. 3", "Each lot shall have a minimum area of two (2) acres (or 87,120 square feet)")
V2_CITES_MONROE[("monroe", "RF-3", "lot")] = ("monroe", "§3.3.4(A) RF-3 minimum lot area, Art. 3", "Each lot shall have a minimum area of three (3) acres (130,680 square feet)")
V2_CITES_MONROE[("monroe", "MFR", "lot")] = ("monroe", "§3.4.5(B) MFR minimum parcel size, Art. 3 p.10", "Minimum parcel size shall be seventy (70) acres under same ownership in a single continuous")
V2_CITES_MONROE[("monroe", "ARR", "lot")] = ("monroe", "§3.5.5(B) ARR minimum lot area, Art. 3", "Minimum lot area shall be not less than ten (10) acres contained within a single contiguous")
V2_CITES_MONROE[("monroe", "HOD", "lot")] = ("monroe", "§3.7.6(B) HOD minimum parcel size, Art. 3", "not less than twenty (20) nor more than twenty-five (25) contiguous acres")
V2_CITES_MONROE[("monroe", "RR", "lot")] = ("monroe", "§3.6.5(D) RR minimum individual lot, Art. 3", "(3/4 acres or 32,670 square feet)")
# ARR/HOD use refinements (optional, replaces the generic MF row cite)
V2_CITES_MONROE[("monroe", "ARR", "use")] = ("monroe", "§10.1 Schedule, Age Restricted Attached Dwelling row, Use Schedule p.6", "Age Restricted Attached Dwelling x x x SEP x x x X")

V2_DISTRICTS["monroe"] = V2_DISTRICTS_MONROE
V2_CITES.update(V2_CITES_MONROE)
# MFR, ARR and HOD are floating districts: the figure in the code is the minimum parcel needed to create the
# district, not a per-lot minimum, so their lot input stays unconfirmed and they stay out of the score.
for _d in ("MFR", "ARR", "HOD"):
    V2_DISTRICTS["monroe"][_d]["lot"] = None

# Fairfield: single-family zones, the residence B and C zones, and the design districts that permit dwellings.
V2_SOURCES["fairfield"] = ("fairfield-zoning.pdf", "Fairfield Zoning Regulations (eff. Sept. 6, 2025)", "https://fairfieldct.gov/Fairfield_ZoningRegulations_Adopted_Effective_09062025%20-%20updated%209.28.26.pdf")
V2_DISTRICTS_FAIRFIELD = {
    # AAA: status include
    'AAA': {"use": 'none', "approval": 'none', "lot": 87120, "adu": 'zoning_permit', "parking": 2, "demo": None,
        "note": 'Single-Family Residence District (§3.1-3.2), single-family dwellings only; minimum lot 2 ac (§3.3.1); attached and detached ADU (§3.2 rows S and T, §13.3.H), issued as a written permit by the Zoning Enforcement Officer (§13.4); owner-occupancy required and 40%/1,500 sq ft size cap (§13.3); parking 2 spaces per single-family dwelling, 1 for an ADU (§25.4.1 K)'},
    # AA: status include
    'AA': {"use": 'none', "approval": 'none', "lot": 43560, "adu": 'zoning_permit', "parking": 2, "demo": None,
        "note": 'Single-Family Residence District (§3.1-3.2), single-family dwellings only; minimum lot 1 ac (§3.3.1); attached and detached ADU (§3.2 rows S and T, §13.3.H), issued as a written permit by the Zoning Enforcement Officer (§13.4); owner-occupancy required and 40%/1,500 sq ft size cap (§13.3); parking 2 spaces per single-family dwelling, 1 for an ADU (§25.4.1 K)'},
    # R-3: status include
    'R-3': {"use": 'none', "approval": 'none', "lot": 20000, "adu": 'zoning_permit', "parking": 2, "demo": None,
        "note": 'Single-Family Residence District (§3.1-3.2), single-family dwellings only; minimum lot 20,000 (§3.3.1); attached and detached ADU (§3.2 rows S and T, §13.3.H), issued as a written permit by the Zoning Enforcement Officer (§13.4); owner-occupancy required and 40%/1,500 sq ft size cap (§13.3); parking 2 spaces per single-family dwelling, 1 for an ADU (§25.4.1 K)'},
    # R-2: status include
    'R-2': {"use": 'none', "approval": 'none', "lot": 14000, "adu": 'zoning_permit', "parking": 2, "demo": None,
        "note": 'Single-Family Residence District (§3.1-3.2), single-family dwellings only; minimum lot 14,000 (§3.3.1); attached ADU only; detached ADU not allowed in R-2 or A (§3.2 row T blank), issued as a written permit by the Zoning Enforcement Officer (§13.4); owner-occupancy required and 40%/1,500 sq ft size cap (§13.3); parking 2 spaces per single-family dwelling, 1 for an ADU (§25.4.1 K)'},
    # A: status include
    'A': {"use": 'none', "approval": 'none', "lot": 9375, "adu": 'zoning_permit', "parking": 2, "demo": None,
        "note": 'Single-Family Residence District (§3.1-3.2), single-family dwellings only; minimum lot 9,375 (§3.3.1); attached ADU only; detached ADU not allowed in R-2 or A (§3.2 row T blank), issued as a written permit by the Zoning Enforcement Officer (§13.4); owner-occupancy required and 40%/1,500 sq ft size cap (§13.3); parking 2 spaces per single-family dwelling, 1 for an ADU (§25.4.1 K)'},
    # B: status include
    'B': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 6000, "adu": 'zoning_permit', "parking": 2, "demo": None,
        "note": 'Residence B (§5.2): two-family dwellings permitted by right (P), three- and four-family not permitted; minimum lot 6,000 sq ft single-family, 9,000 sq ft two-family (§5.3.1; single-family figure scored, as Stamford R-6); attached ADU only on a lot with a single-family residence (§5.2.2.C) by written ZEO permit (§13.4); parking 2 for a 2-bedroom unit (§25.4.1 K); 5-unit affordable bonus on 15,000 sq ft lots (§5.3.2)'},
    # C: status include
    'C': {"use": 'capped_by_right', "approval": 'capped_by_right', "lot": 5000, "adu": 'zoning_permit', "parking": 2, "demo": None,
        "note": 'Residence C (§5.2): two-, three- and four-family dwellings permitted by right (P), capped at four units; minimum lot 5,000 sq ft single-family, 7,500 two-family, 10,000 three-family, 12,500 four-family (§5.3.1; single-family figure scored); attached ADU only on a single-family lot (§5.2.2.C), written ZEO permit (§13.4); parking 2 for a 2-bedroom unit (§25.4.1 K)'},
    # BD: status include (flag ADU inference)
    'BD': {"use": 'none', "approval": 'none', "lot": 9375, "adu": 'prohibited', "parking": 2, "demo": None,
        "note": 'Beach District (§4.2): one single detached dwelling per lot, nothing else; 9,375 sq ft minimum, each lot a 50 ft square (§4.4); multiple dwellings only to rebuild an existing multi-unit lot with the same unit count by Special Exception (§4.5); ADU scored prohibited by INFERENCE: §13.3 lists AAA, AA, A, R-3, R-2, B and C but not Beach, §4.2.D bars livable detached accessory structures, and §2.4.A prohibits unlisted uses; parking per §25 (2 per single-family)'},
    # CDD: status include (flag)
    'CDD': {"use": 'capped_by_right', "approval": 'discretionary', "lot": 0, "adu": 'n/a', "parking": 2, "demo": None,
        "note": "Center Designed Business District (§6.3 row Z): residential uses permitted (P) but not on the ground floor; new construction, alterations or additions need a Special Permit under Section 31 (§6.2); conversion of an existing commercial building to residential is a no-hearing Compliance Application, 65 days (§6.3.2, PA 25-164); no minimum lot size (§6.4 row B); 4 stories/52 ft, 90% lot coverage, floor area 325%; no unit cap stated, only bulk limits; ADU treated n/a because multi-unit residential is permitted (Greenwich business-zone precedent) -- JUDGMENT; use tier could alternatively be 'discretionary'"},
    # DCD: status include (flag)
    'DCD': {"use": 'capped_by_right', "approval": 'discretionary', "lot": 0, "adu": 'n/a', "parking": 2, "demo": None,
        "note": "Designed Commercial District (§6.3 row Z): residential uses permitted (P) but not on the ground floor; new construction, alterations or additions need a Special Permit under Section 31 (§6.2); conversion of an existing commercial building to residential is a no-hearing Compliance Application, 65 days (§6.3.2, PA 25-164); no minimum lot size (§6.4 row B); 4 stories/52 ft, 80% coverage, floor area 275%; no unit cap stated, only bulk limits; ADU treated n/a because multi-unit residential is permitted (Greenwich business-zone precedent) -- JUDGMENT; use tier could alternatively be 'discretionary'"},
    # NDD: status include (flag)
    'NDD': {"use": 'capped_by_right', "approval": 'discretionary', "lot": 0, "adu": 'n/a', "parking": 2, "demo": None,
        "note": "Neighborhood Designed Business District (§6.3 row Z): residential uses permitted (P) but not on the ground floor; new construction, alterations or additions need a Special Permit under Section 31 (§6.2); conversion of an existing commercial building to residential is a no-hearing Compliance Application, 65 days (§6.3.2, PA 25-164); no minimum lot size (§6.4 row B); 3 stories/40 ft, 75% coverage, floor area 150%; ground-floor residential only in a second building set back 70 ft, residential at most 50% of floor area (§6.3.1.C); no unit cap stated, only bulk limits; ADU treated n/a because multi-unit residential is permitted (Greenwich business-zone precedent) -- JUDGMENT; use tier could alternatively be 'discretionary'"},
    # DRD: status include (flag)
    'DRD': {"use": 'discretionary', "approval": 'discretionary', "lot": 43560, "adu": 'n/a', "parking": 2, "demo": None,
        "note": 'Designed Residence District (§10): dwelling for one or more families only by Special Permit (§10.4.A); density 1 unit for first 9,375 sq ft plus 1 per additional 3,000 sq ft, with minimum lot by underlying zone AAA 30 ac, AA 10 ac, R-3 5 ac, R-2 2 ac, A/B/C 1 ac (§10.6.1), 10 units/acre and 1-acre lot on other parcels (§10.6.2.B), 17 units/acre near I-95 or a station on former business/industrial land; max 4 units per building (§10.9); the underlying zone is not in the mapped layer, so lot scored at the 1-acre floor (43,560) -- JUDGMENT; where the underlying zone was residential its prior uses also stay permitted (§10.3.B), so ADU is not resolved and is scored n/a because multi-unit is permitted -- JUDGMENT'},
    # DI: status exclude (recommended)
    'DI': {"use": 'discretionary', "approval": 'discretionary', "lot": 435600, "adu": 'n/a', "parking": 1.25, "demo": None,
        "note": 'Designed Industrial District: dwellings only inside a Transportation/Commercial Park (§8.8.3.A), which must be 10+ acres with some part within 300 ft of a railroad passenger station (§8.8.5.A), determined by Commission application (§8.8.6) and built by Special Permit (§8.8.2); 50 bedrooms/acre and residential at most 70% of floor area (§8.8.10.E); residential parking lesser of 1 per bedroom or 1.25 per household (§8.8.7.C). Otherwise industrial. Lot = 10-acre qualifying tract (a designation threshold, not a building-lot minimum) -- JUDGMENT. Recommend EXCLUDE: DI is an industrial district and the residential path applies to only a few station-adjacent parcels'},
}

V2_CITES_FAIRFIELD = {}
# page [PDF [11]]
V2_CITES_FAIRFIELD[("fairfield", 'AAA', 'use')] = ("fairfield", '§3.2 Permitted Uses preamble', 'No use shall be permitted in said Districts, except as these Single-Family Residence District regulations provide')
# page [PDF [13]]
V2_CITES_FAIRFIELD[("fairfield", 'AAA', 'lot')] = ("fairfield", '§3.3.1 Minimum Lot Area row', 'A. Minimum Lot Area (sf or acres if noted) 2 ac 1 ac 20,000 14,000 9,375')
# page [PDF [64]]
V2_CITES_FAIRFIELD[("fairfield", 'AAA', 'adu')] = ("fairfield", '§13.4 Application Procedure (permit from Zoning Enforcement Officer)', 'has received a written permit from the Zoning Enforcement Officer')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'AAA', 'parking')] = ("fairfield", '§25.4.1(K) single-family parking', 'Single-family residential - 2 spaces')
# page [PDF [11]]
V2_CITES_FAIRFIELD[("fairfield", 'AA', 'use')] = ("fairfield", '§3.2 Permitted Uses preamble', 'No use shall be permitted in said Districts, except as these Single-Family Residence District regulations provide')
# page [PDF [13]]
V2_CITES_FAIRFIELD[("fairfield", 'AA', 'lot')] = ("fairfield", '§3.3.1 Minimum Lot Area row', 'A. Minimum Lot Area (sf or acres if noted) 2 ac 1 ac 20,000 14,000 9,375')
# page [PDF [64]]
V2_CITES_FAIRFIELD[("fairfield", 'AA', 'adu')] = ("fairfield", '§13.4 Application Procedure (permit from Zoning Enforcement Officer)', 'has received a written permit from the Zoning Enforcement Officer')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'AA', 'parking')] = ("fairfield", '§25.4.1(K) single-family parking', 'Single-family residential - 2 spaces')
# page [PDF [11]]
V2_CITES_FAIRFIELD[("fairfield", 'R-3', 'use')] = ("fairfield", '§3.2 Permitted Uses preamble', 'No use shall be permitted in said Districts, except as these Single-Family Residence District regulations provide')
# page [PDF [13]]
V2_CITES_FAIRFIELD[("fairfield", 'R-3', 'lot')] = ("fairfield", '§3.3.1 Minimum Lot Area row', 'A. Minimum Lot Area (sf or acres if noted) 2 ac 1 ac 20,000 14,000 9,375')
# page [PDF [64]]
V2_CITES_FAIRFIELD[("fairfield", 'R-3', 'adu')] = ("fairfield", '§13.4 Application Procedure (permit from Zoning Enforcement Officer)', 'has received a written permit from the Zoning Enforcement Officer')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'R-3', 'parking')] = ("fairfield", '§25.4.1(K) single-family parking', 'Single-family residential - 2 spaces')
# page [PDF [11]]
V2_CITES_FAIRFIELD[("fairfield", 'R-2', 'use')] = ("fairfield", '§3.2 Permitted Uses preamble', 'No use shall be permitted in said Districts, except as these Single-Family Residence District regulations provide')
# page [PDF [13]]
V2_CITES_FAIRFIELD[("fairfield", 'R-2', 'lot')] = ("fairfield", '§3.3.1 Minimum Lot Area row', 'A. Minimum Lot Area (sf or acres if noted) 2 ac 1 ac 20,000 14,000 9,375')
# page [PDF [64]]
V2_CITES_FAIRFIELD[("fairfield", 'R-2', 'adu')] = ("fairfield", '§13.4 Application Procedure (permit from Zoning Enforcement Officer)', 'has received a written permit from the Zoning Enforcement Officer')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'R-2', 'parking')] = ("fairfield", '§25.4.1(K) single-family parking', 'Single-family residential - 2 spaces')
# page [PDF [11]]
V2_CITES_FAIRFIELD[("fairfield", 'A', 'use')] = ("fairfield", '§3.2 Permitted Uses preamble', 'No use shall be permitted in said Districts, except as these Single-Family Residence District regulations provide')
# page [PDF [13]]
V2_CITES_FAIRFIELD[("fairfield", 'A', 'lot')] = ("fairfield", '§3.3.1 Minimum Lot Area row', 'A. Minimum Lot Area (sf or acres if noted) 2 ac 1 ac 20,000 14,000 9,375')
# page [PDF [64]]
V2_CITES_FAIRFIELD[("fairfield", 'A', 'adu')] = ("fairfield", '§13.4 Application Procedure (permit from Zoning Enforcement Officer)', 'has received a written permit from the Zoning Enforcement Officer')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'A', 'parking')] = ("fairfield", '§25.4.1(K) single-family parking', 'Single-family residential - 2 spaces')
# page [PDF [22]]
V2_CITES_FAIRFIELD[("fairfield", 'B', 'use')] = ("fairfield", '§5.2 permitted uses table, Two-Family row', 'A. Two-Family Dwellings P P Section 5.3')
# page [PDF [22]]
V2_CITES_FAIRFIELD[("fairfield", 'B', 'approval')] = ("fairfield", '§5.2 permitted uses table, Two-Family row', 'A. Two-Family Dwellings P P Section 5.3')
# page [PDF [23]]
V2_CITES_FAIRFIELD[("fairfield", 'B', 'lot')] = ("fairfield", '§5.3.1 Minimum Lot Area for Single-Family', 'Minimum Lot Area for Single-Family (sf) 6,000 5,000')
# page [PDF [22]]
V2_CITES_FAIRFIELD[("fairfield", 'B', 'adu')] = ("fairfield", '§5.2.2(C) attached ADUs', 'Attached Accessory Dwelling Units are permitted per the standards of Section 13, but only where the minimum lot requirements are met and where there exists only a single-family residence on the parcel.')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'B', 'parking')] = ("fairfield", '§25.4.1(K) multi-family parking (16 units or fewer)', 'Multi-family: 1 space for up to each 1-bedroom and 2 spaces for each 2-bedroom unit or larger.')
# page [PDF [22]]
V2_CITES_FAIRFIELD[("fairfield", 'C', 'use')] = ("fairfield", '§5.2 permitted uses table, Four-Family row', 'C. Four-Family Dwellings — P')
# page [PDF [22]]
V2_CITES_FAIRFIELD[("fairfield", 'C', 'approval')] = ("fairfield", '§5.2 permitted uses table, Four-Family row', 'C. Four-Family Dwellings — P')
# page [PDF [23]]
V2_CITES_FAIRFIELD[("fairfield", 'C', 'lot')] = ("fairfield", '§5.3.1 Minimum Lot Area for Single-Family', 'Minimum Lot Area for Single-Family (sf) 6,000 5,000')
# page [PDF [22]]
V2_CITES_FAIRFIELD[("fairfield", 'C', 'adu')] = ("fairfield", '§5.2.2(C) attached ADUs', 'Attached Accessory Dwelling Units are permitted per the standards of Section 13, but only where the minimum lot requirements are met and where there exists only a single-family residence on the parcel.')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'C', 'parking')] = ("fairfield", '§25.4.1(K) multi-family parking (16 units or fewer)', 'Multi-family: 1 space for up to each 1-bedroom and 2 spaces for each 2-bedroom unit or larger.')
# page [PDF [17]]
V2_CITES_FAIRFIELD[("fairfield", 'BD', 'use')] = ("fairfield", '§4.2(A) Beach District permitted use', 'A single detached dwelling for one family and not more than one such dwelling per lot')
# page [PDF [18]]
V2_CITES_FAIRFIELD[("fairfield", 'BD', 'lot')] = ("fairfield", '§4.4 Conforming Lots', 'Each lot shall have a minimum area of 9,375 square feet')
# page [PDF [17]]
V2_CITES_FAIRFIELD[("fairfield", 'BD', 'adu')] = ("fairfield", '§4.2(D)(1) Beach District accessory structures', 'no detached accessory structure shall contain any finished livable floor area, plumbing fixtures or heat')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'BD', 'parking')] = ("fairfield", '§25.4.1(K) single-family parking', 'Single-family residential - 2 spaces')
# page [PDF [28]]
V2_CITES_FAIRFIELD[("fairfield", 'CDD', 'use')] = ("fairfield", '§6.3 permitted uses table, row Z (CDD / DCD / NDD columns)', 'Z. Residential uses provided it shall not be located on a ground P P P 6.3.4')
# page [PDF [26]]
V2_CITES_FAIRFIELD[("fairfield", 'CDD', 'approval')] = ("fairfield", '§6.2 Special Permit Uses', 'A Special Permit under Section 31 of these regulations shall be required for any new construction, re-construction, exterior alterations, or addition for a use permitted in Section 6.3')
# page [PDF [31]]
V2_CITES_FAIRFIELD[("fairfield", 'CDD', 'lot')] = ("fairfield", '§6.4 table row B, minimum lot size', 'B. Minimum Lot Size (sf) No minimum No minimum No minimum')
# page [PDF [28]]
V2_CITES_FAIRFIELD[("fairfield", 'CDD', 'adu')] = ("fairfield", '§6.3 permitted uses table, row Z (CDD / DCD / NDD columns)', 'Z. Residential uses provided it shall not be located on a ground P P P 6.3.4')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'CDD', 'parking')] = ("fairfield", '§25.4.1(K) multi-family parking (16 units or fewer)', 'Multi-family: 1 space for up to each 1-bedroom and 2 spaces for each 2-bedroom unit or larger.')
# page [PDF [28]]
V2_CITES_FAIRFIELD[("fairfield", 'DCD', 'use')] = ("fairfield", '§6.3 permitted uses table, row Z (CDD / DCD / NDD columns)', 'Z. Residential uses provided it shall not be located on a ground P P P 6.3.4')
# page [PDF [26]]
V2_CITES_FAIRFIELD[("fairfield", 'DCD', 'approval')] = ("fairfield", '§6.2 Special Permit Uses', 'A Special Permit under Section 31 of these regulations shall be required for any new construction, re-construction, exterior alterations, or addition for a use permitted in Section 6.3')
# page [PDF [31]]
V2_CITES_FAIRFIELD[("fairfield", 'DCD', 'lot')] = ("fairfield", '§6.4 table row B, minimum lot size', 'B. Minimum Lot Size (sf) No minimum No minimum No minimum')
# page [PDF [28]]
V2_CITES_FAIRFIELD[("fairfield", 'DCD', 'adu')] = ("fairfield", '§6.3 permitted uses table, row Z (CDD / DCD / NDD columns)', 'Z. Residential uses provided it shall not be located on a ground P P P 6.3.4')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'DCD', 'parking')] = ("fairfield", '§25.4.1(K) multi-family parking (16 units or fewer)', 'Multi-family: 1 space for up to each 1-bedroom and 2 spaces for each 2-bedroom unit or larger.')
# page [PDF [28]]
V2_CITES_FAIRFIELD[("fairfield", 'NDD', 'use')] = ("fairfield", '§6.3 permitted uses table, row Z (CDD / DCD / NDD columns)', 'Z. Residential uses provided it shall not be located on a ground P P P 6.3.4')
# page [PDF [26]]
V2_CITES_FAIRFIELD[("fairfield", 'NDD', 'approval')] = ("fairfield", '§6.2 Special Permit Uses', 'A Special Permit under Section 31 of these regulations shall be required for any new construction, re-construction, exterior alterations, or addition for a use permitted in Section 6.3')
# page [PDF [31]]
V2_CITES_FAIRFIELD[("fairfield", 'NDD', 'lot')] = ("fairfield", '§6.4 table row B, minimum lot size', 'B. Minimum Lot Size (sf) No minimum No minimum No minimum')
# page [PDF [28]]
V2_CITES_FAIRFIELD[("fairfield", 'NDD', 'adu')] = ("fairfield", '§6.3 permitted uses table, row Z (CDD / DCD / NDD columns)', 'Z. Residential uses provided it shall not be located on a ground P P P 6.3.4')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'NDD', 'parking')] = ("fairfield", '§25.4.1(K) multi-family parking (16 units or fewer)', 'Multi-family: 1 space for up to each 1-bedroom and 2 spaces for each 2-bedroom unit or larger.')
# page [PDF [52]]
V2_CITES_FAIRFIELD[("fairfield", 'DRD', 'use')] = ("fairfield", '§10.4(A) Designed Residence special permit use', 'A dwelling for one or more families and accessory uses, customary with and incidental to such use')
# page [PDF [52]]
V2_CITES_FAIRFIELD[("fairfield", 'DRD', 'approval')] = ("fairfield", '§10.4 Special Permit Uses preamble', 'the use of land, buildings and other structures shall be subject to securing a Special Permit from the Commission as provided for in Section 31')
# page [PDF [54]]
V2_CITES_FAIRFIELD[("fairfield", 'DRD', 'lot')] = ("fairfield", '§10.6.2(B) other parcels', 'On all other parcels, the maximum allowable dwelling unit density shall be 10 units per acre and each lot shall have a minimum area of 1 acre.')
# page [PDF [52]]
V2_CITES_FAIRFIELD[("fairfield", 'DRD', 'adu')] = ("fairfield", '§10.4(A) Designed Residence special permit use', 'A dwelling for one or more families and accessory uses, customary with and incidental to such use')
# page [PDF [97]]
V2_CITES_FAIRFIELD[("fairfield", 'DRD', 'parking')] = ("fairfield", '§25.4.1(K) multi-family parking (16 units or fewer)', 'Multi-family: 1 space for up to each 1-bedroom and 2 spaces for each 2-bedroom unit or larger.')
# page [PDF [45]]
V2_CITES_FAIRFIELD[("fairfield", 'DI', 'use')] = ("fairfield", '§8.8.3(A) Transportation/Commercial Park permitted uses', 'Residential uses for one or more families.')
# page [PDF [45]]
V2_CITES_FAIRFIELD[("fairfield", 'DI', 'approval')] = ("fairfield", '§8.8.2 Transportation/Commercial Park special permit', 'A Special Permit under Section 31 of these regulations shall be required for any new construction, reconstruction, exterior alteration or addition for a use permitted by Section 8.8.3.')
# page [PDF [46]]
V2_CITES_FAIRFIELD[("fairfield", 'DI', 'lot')] = ("fairfield", '§8.8.5(A) qualifying park', 'having a minimum of 10 acres in an area adjacent to a railroad passenger station')
# page [PDF [45]]
V2_CITES_FAIRFIELD[("fairfield", 'DI', 'adu')] = ("fairfield", '§8.8.3(A) Transportation/Commercial Park permitted uses', 'Residential uses for one or more families.')
# page [PDF [47]]
V2_CITES_FAIRFIELD[("fairfield", 'DI', 'parking')] = ("fairfield", '§8.8.7(C) residential parking', 'C. Residential Uses: Lesser of 1 parking space per bedroom or 1.25 spaces per household.')

V2_DISTRICTS["fairfield"] = V2_DISTRICTS_FAIRFIELD
V2_CITES.update(V2_CITES_FAIRFIELD)
# Demolition: no demolition-delay rule appears anywhere in the mirrored zoning regulations (searched 'demoli' and 'delay'); demo stays None for every district.

V2_DISTRICTS["fairfield"] = V2_DISTRICTS_FAIRFIELD
V2_CITES.update(V2_CITES_FAIRFIELD)
# Only quoted text is scored: BD's ADU rule is inferred, DRD has no underlying zone in the map layer, and DI's
# 10-acre figure is a tract threshold, not a lot minimum, so those inputs stay unconfirmed.
V2_DISTRICTS["fairfield"]["BD"]["adu"] = None
V2_DISTRICTS["fairfield"]["DRD"]["adu"] = None
V2_DISTRICTS["fairfield"]["DI"]["lot"] = None

# Trumbull: Residence AAA, AA and A.
V2_SOURCES["trumbull"] = ("trumbull-zoning.pdf", "Trumbull Zoning Regulations (amended through Aug. 19, 2026)", "https://trumbull-ct.gov/DocumentCenter/View/1323")
_ADU_SP = ("trumbull", "Art. II §1.1.2(7)(D) Accessory apartment application procedure (p. 47)",
           "All other applications for accessory apartments shall be a Special Permit application made to the Planning and Zoning Commission")
_ADU_ADMIN = ("trumbull", "Art. II §1.1.2(7)(D) Accessory apartment application procedure (p. 47)",
              "then an application may be made to, and approved by, the Zoning Enforcement Officer.")
_SF_USE = ("trumbull", "Art. II §1.1.1 Residence AAA/AA/A permitted uses (p. 42)",
           "no Building or Structure shall be erected, altered, occupied or used, arranged or designed to be used for other than one or more of the following specified purposes: 1. One-Family Dwelling;")

V2_DISTRICTS_TRUMBULL = {
    # AAA: 1,433.7 acres. Include. Art. I §2 (p. 3), Art. II §1.1 (pp. 42-47), Art. III Exhibit
    "AAA": {"use": "none", "approval": "none", "lot": 43560, "adu": "administrative", "parking": None, "demo": None,
            "note": "Residence AAA (Art. II §1.1): One-Family Dwelling only; 1 acre minimum (Art. I §2); attached accessory apartment only: ZEO approval if inside the existing footprint, otherwise Special Permit, detached ADU barred, owner-occupancy, 40-year 8-30g deed restriction, 4 off-street spaces (§1.1.2(7)) -- ADU tier is a JUDGMENT (best-case qualifying pathway, as Stamford R-6; alternative special_permit); no per-unit parking minimum found, only a 4-vehicle maximum (§1.1.6), so parking None; no demolition waiting period in the code"},
    # AA: 6,752.6 acres. Include.
    "AA": {"use": "none", "approval": "none", "lot": 43560, "adu": "administrative", "parking": None, "demo": None,
           "note": "Residence AA: as AAA (shared Art. II §1.1); 1 acre minimum (Art. I §2)"},
    # A: 3,629.7 acres. Include.
    "A": {"use": "none", "approval": "none", "lot": 21780, "adu": "administrative", "parking": None, "demo": None,
          "note": "Residence A: as AAA (shared Art. II §1.1); 1/2 acre minimum (Art. I §2)"},
    # B-C LHGTHN: 30.3 acres. Include (flagged). Art. II §3.2 (pp. 117-123); Art. III Exhibit (B-C row)
    "B-C LHGTHN": {"use": "discretionary", "approval": "discretionary", "lot": 87120, "adu": "prohibited", "parking": None, "demo": None,
                   "note": "B-C Long Hill Green / Town Hall Node (§3.2): Multi-Family Dwellings are item 14 of a numbered list that runs on from the §3.2.4 Special Permit list (items 1-5 post offices..gas stations, 6-14 day care, fast food, ..., multi-family); §3.2.1 permitted list stops at item 5 (and excludes Fast Food) -- Special Permit reading is INFERRED from list numbering, confirm against the adopted text; cap 12 units/gross acre, max 50% of floor area, upper floors on parcels under 1 acre, studios-2BR only, 10% affordable (§3.2.1 item 14); lot 2 acres = underlying B-C minimum (Art. III Exhibit) -- JUDGMENT, §3.2.5(1) deems existing lots buildable; no single-family dwelling or accessory-apartment rule applies in this zone (ADU rule sits in §1.1.2 for Residence A/AA/AAA only) so ADU scored prohibited -- INFERRED; parking sufficient per ITE (§3.2.7), no ratio"},
    # MDD: 83.9 acres. Include (flagged). Art. II §3.4 (pp. 134-139)
    "MDD": {"use": "discretionary", "approval": "discretionary", "lot": 87120, "adu": "prohibited", "parking": None, "demo": None,
            "note": "Mixed-Use Design District (§3.4): any multi-family residential use must receive Special Permit (§3.4.5); no multi-family in the §3.4.2 permitted list; separate parcels must be at least 2 acres (§3.4.6(1)) -- lot is that parcel minimum; no single-family or ADU provision applies so ADU prohibited -- INFERRED; age-restricted units 1.5 spaces/unit (§3.4.7) but that is a subcategory, parking None"},
    # MFO overlay: 50.2 acres (overlay layer; overlaps I-L/I-L2). Include (flagged). Art. II §7.6 (pp. 171-173)
    "MFO": {"use": "discretionary", "approval": "discretionary", "lot": 435600, "adu": "prohibited", "parking": 2.0, "demo": None,
            "note": "Multi-Family Overlay (§7.6): requires rezoning of existing I-L/I-L2 land of at least 10 acres without direct state-highway access (§7.6.2), then Special Permit for up to 220 units (§7.6.3); 20 units/acre, 600-unit town-wide cap, 220 per 12 months (§7.6.4(1)); lot = 10-acre eligibility minimum (435,600 sq ft) -- JUDGMENT, tract threshold; parking 1.8/1BR, 2.0/2BR plus 1 guest per 20 units (§7.6.4(5)), scored 2.0; ADU prohibited -- INFERRED (multi-family only, no ADU rule); Art. XVII moratorium on rental housing applications over 50 units runs to Feb. 28, 2027"},
}

V2_CITES_TRUMBULL = {}
for _d in ("AAA", "AA", "A"):
    V2_CITES_TRUMBULL[("trumbull", _d, "use")] = _SF_USE
    V2_CITES_TRUMBULL[("trumbull", _d, "adu")] = _ADU_ADMIN
V2_CITES_TRUMBULL[("trumbull", "AAA", "lot")] = ("trumbull", "Art. I §2 Classes of Zones, Residence AAA (p. 3)", "Residence Zone AAA              (minimum lot size 1 acre, 43,560 sq. ft.)")
V2_CITES_TRUMBULL[("trumbull", "AA", "lot")] = ("trumbull", "Art. I §2 Classes of Zones, Residence AA (p. 3)", "Residence Zone AA               (minimum lot size 1 acre, 43,560 sq. ft.)")
V2_CITES_TRUMBULL[("trumbull", "A", "lot")] = ("trumbull", "Art. I §2 Classes of Zones, Residence A (p. 3)", "Residence Zone A                (minimum lot size ½ acre, 21,780 sq. ft.)")
# Parking (A/AA/AAA): NOT a minimum. Only a maximum is stated; quote kept for the record, parking stays None.
TRUMBULL_PARKING_CONTEXT = ("trumbull", "Art. II §1.1.6(1) Maximum Outdoor Parking for a Dwelling (p. 53)", "No more than four (4) motor vehicles shall be parked on any Lot, other than motor vehicles parked within a Private Garage.")

V2_CITES_TRUMBULL[("trumbull", "B-C LHGTHN", "use")] = ("trumbull", "Art. II §3.2.4 Special Permit list, item 14 Multi-Family Dwellings (pp. 119-120)", "Multi-family dwellings in this zone may be permitted subject to the following regulations:")
V2_CITES_TRUMBULL[("trumbull", "B-C LHGTHN", "lot")] = ("trumbull", "Art. III Exhibit, Commercial B-C row (p. 183)", "Commercial B-C        2 acres        250")
V2_CITES_TRUMBULL[("trumbull", "B-C LHGTHN", "adu")] = ("trumbull", "Art. II §3.2.1 permitted-use limiting clause (p. 117)", "no Building or Structure shall be erected, altered, occupied or used, arranged or designed to be used for other than one or more of the following specified uses")
V2_CITES_TRUMBULL[("trumbull", "MDD", "use")] = ("trumbull", "Art. II §3.4.5 MDD site plan / special permit (p. 137)", "any multi- family residential use must receive Special")
V2_CITES_TRUMBULL[("trumbull", "MDD", "lot")] = ("trumbull", "Art. II §3.4.6(1) MDD bulk (p. 137)", "must have a minimum lot size of 2 (two) acres")
V2_CITES_TRUMBULL[("trumbull", "MDD", "adu")] = ("trumbull", "Art. II §3.4.2 MDD permitted uses (p. 133)", "no building or structure shall be erected, altered, occupied, or used, arranged or designed to be used for other than one or more of the following")
V2_CITES_TRUMBULL[("trumbull", "MFO", "use")] = ("trumbull", "Art. II §7.6.3 Uses Permitted by Special Permit (p. 172)", "Multi-family residential development of not more than 220 units")
V2_CITES_TRUMBULL[("trumbull", "MFO", "lot")] = ("trumbull", "Art. II §7.6.2(b) MFO location criteria (p. 171)", "b. Not less than 10 acres; and")
V2_CITES_TRUMBULL[("trumbull", "MFO", "adu")] = ("trumbull", "Art. II §7.6.3 Uses Permitted by Special Permit (p. 172)", "Multi-family residential development of not more than 220 units and associated clubhouse and amenity and/or active recreational space")
V2_CITES_TRUMBULL[("trumbull", "MFO", "parking")] = ("trumbull", "Art. II §7.6.4(5) MFO parking (p. 172)", "Parking for residential units shall be provided at 2.0 spaces per two bedroom unit and 1.8 spaces per one bedroom unit.")

V2_DISTRICTS["trumbull"] = V2_DISTRICTS_TRUMBULL
V2_CITES.update(V2_CITES_TRUMBULL)
# Accessory apartments inside the existing footprint go to the Zoning Enforcement Officer, but every other
# application is a Special Permit (Art. II 1.1.2(7)(D)); score the pathway most new ADUs face.
for _d in ("AAA", "AA", "A"):
    V2_DISTRICTS["trumbull"][_d]["adu"] = "special_permit"
    V2_CITES[("trumbull", _d, "adu")] = _ADU_SP
# The non-residential districts' ADU rule would be inferred from a closed use list, and MFO's 10 acres is a
# site threshold, so these stay unconfirmed and out of the score.
for _d in ("B-C LHGTHN", "MDD", "MFO"):
    V2_DISTRICTS["trumbull"][_d]["adu"] = None

# Corrections from the evidence audit (Nov. 2026). Each one is a rule the quoted text does not support as written,
# so the input is either narrowed to the value the text states or left unconfirmed (and the district drops out).
_AUDIT_FIXES = [
    # Stamford: lot minimums must match the multifamily column the tier describes; C-D and TCDD follow the code.
    ("stamford", "NX-D", {"lot": 6000}),
    ("stamford", "R-5", {"lot": 9000}),
    ("stamford", "TCDD", {"lot": 43560}),
    ("stamford", "C-D", {"adu": None}),
    # Greenwich: business zones state no area minimum (the table points to a purpose clause); WB's accessory-unit
    # rule is inferred; R-PHD-SU is a floating zone created by map change, and its 1,800 sq ft figure is per unit.
    ("greenwich", "LB", {"lot": None}), ("greenwich", "LBR-2", {"lot": None}),
    ("greenwich", "CGB", {"lot": None}), ("greenwich", "CGBR", {"lot": None}),
    ("greenwich", "GB", {"lot": None}), ("greenwich", "GBO", {"lot": None}),
    ("greenwich", "WB", {"adu": None}),
    ("greenwich", "R-PHD-SU", {"lot": None, "approval": "discretionary", "use": "narrow_by_right"}),
    # Fairfield: B and C are scored on the two-family minimum (the tier is two-family by right); CDD, DCD and NDD
    # need a Special Permit for new construction; DRD's 1-acre figure is only a floor; DI's use is Special Permit only.
    ("fairfield", "B", {"lot": 9000}), ("fairfield", "C", {"lot": 7500}),
    ("fairfield", "CDD", {"use": "discretionary"}), ("fairfield", "DCD", {"use": "discretionary"}),
    ("fairfield", "NDD", {"use": "discretionary"}),
    ("fairfield", "DRD", {"lot": None}), ("fairfield", "DI", {"adu": None}),
    # Bridgeport: NX1 and NX2 already allow several units by right, so the accessory-unit pathway is not applicable.
    ("bridgeport", "NX1", {"adu": "n/a"}), ("bridgeport", "NX2", {"adu": "n/a"}),
]
for _slug, _d, _changes in _AUDIT_FIXES:
    V2_DISTRICTS[_slug][_d].update(_changes)
# Trumbull's Residence A/AA/AAA note still described the administrative pathway that the scored value no longer uses.
# Scored on the easiest pathway open to an ordinary owner, the same rule applied to Stamford and Greenwich: a
# Zoning Enforcement Officer approval for an accessory apartment inside the existing footprint (Art. II 1.1.2(7)(D)).
# Other applications need a Special Permit, which is the harder pathway and is stated in the note.
for _d in ("AAA", "AA", "A"):
    V2_DISTRICTS["trumbull"][_d]["adu"] = "zoning_permit"
    V2_CITES[("trumbull", _d, "adu")] = _ADU_ADMIN
    V2_DISTRICTS["trumbull"][_d]["note"] = (
        "Single-family dwelling only (Art. II 1.1.1); minimum lot per Art. I 2 (AAA and AA 43,560 sq ft, A 21,780 sq ft). "
        "Accessory apartments inside the existing footprint are approved by the Zoning Enforcement Officer (scored: easiest pathway); "
        "all other applications need a Special Permit (Art. II 1.1.2(7)(D)); owner occupancy and a deed restriction apply."
    )

def _pdf_compact_text(filename):
    import subprocess
    path = os.path.join(ROOT, "public", "sources", filename)
    out = subprocess.run(["pdftotext", "-q", "-layout", path, "-"], capture_output=True, text=True, check=True).stdout
    return re.sub(r"\s+", "", out).lower()

_PDF_TEXT_CACHE = {}
def v2_citation(slug, district, field):
    key = (slug, district, field)
    if key not in V2_CITES:
        return None
    src_key, cite, quote = V2_CITES[key]
    filename, title, url = V2_SOURCES[src_key]
    if filename not in _PDF_TEXT_CACHE:
        _PDF_TEXT_CACHE[filename] = _pdf_compact_text(filename)
    if re.sub(r"\s+", "", quote).lower() not in _PDF_TEXT_CACHE[filename]:
        raise SystemExit(f"V2 quote not found in {filename}: {key}: {quote[:80]}")
    return {"field": field, "cite": cite, "quote": quote, "source_title": title, "url": url, "file": f"/sources/{filename}"}

V2_TIER_SCALES = {
    "use": [
        ("by_right", "Multifamily allowed by right in a meaningful district with no cap"),
        ("capped_by_right", "Multifamily or two-family by right, but capped by unit count or density"),
        ("narrow_by_right", "By right only in a narrow or hard-to-create district"),
        ("discretionary", "Multifamily allowed only through a special permit or hearing"),
        ("none", "No multifamily pathway in this district"),
    ],
    "approval": [
        ("by_right", "Approved administratively, no hearing"),
        ("capped_by_right", "Administrative site-plan approval with a cap"),
        ("narrow_by_right", "By right only in a narrow district"),
        ("discretionary", "Special permit or hearing required"),
        ("none", "No approval pathway for multifamily"),
    ],
    "adu": [
        ("by_right", "Accessory unit allowed by right"),
        ("administrative", "Administrative review only"),
        ("zoning_permit", "Zoning permit (staff level)"),
        ("special_permit", "Special permit with a public hearing"),
        ("prohibited", "Accessory units not allowed"),
    ],
}
V2_TIER_LABELS = {
    "by_right": "By right", "capped_by_right": "By right, capped", "narrow_by_right": "By right, narrow",
    "discretionary": "Discretionary (special permit)", "none": "Not allowed", "administrative": "Administrative",
    "zoning_permit": "Zoning permit", "special_permit": "Special permit", "prohibited": "Prohibited",
}
V2_FACTOR_FIELD = {"Multifamily Access": "use", "Approval Discretion": "use", "Minimum Lot Size": "lot",
                   "ADU Approval Pathway": "adu", "Parking Mandate": "parking", "Demolition Delay": None}
V2_FACTOR_SCALE_NOTE = {
    "Multifamily Access": "No tier scores 0 in this rubric; the most permissive tier is 6 of 30.",
    "Approval Discretion": "The most permissive approval tier is 1 of 10.",
    "Minimum Lot Size": "Scored on a log scale: lots at or below 2,500 sq ft score 0; lots of 174,240 sq ft (4 acres) or more score 20.",
    "ADU Approval Pathway": "The most permissive ADU tier is 1 of 15.",
    "Parking Mandate": "Scored linearly: 0 spaces per unit = 0; 2.5 spaces per unit or more = 10.",
    "Demolition Delay": "Scored linearly: 0 days = 0; 180 days or more = 15.",
}

def _factor_explanation(label, inputs, points):
    use, approval, adu, lot, parking, demo = (inputs["use"], inputs["approval"], inputs["adu"],
                                              inputs["lot"], inputs["parking"], inputs["demo"])
    if label in ("Multifamily Access", "Approval Discretion", "ADU Approval Pathway"):
        tier = {"Multifamily Access": use, "Approval Discretion": approval, "ADU Approval Pathway": adu}[label]
        if tier == "n/a":
            return None, ("Not applicable: the code already allows several units by right in the principal "
                          "building here, so a separate accessory-unit pathway adds no restriction. The component "
                          "is left out of the score (it still counts as confirmed for the five-of-six rule)."), "Not applicable"
        if tier is None:
            return None, "Not confirmed for this district.", V2_TIER_LABELS.get(tier, "Not confirmed")
        scale_key = {"Multifamily Access": "use", "Approval Discretion": "approval", "ADU Approval Pathway": "adu"}[label]
        meaning = dict(V2_TIER_SCALES[scale_key]).get(tier, "")
        return tier, f"Tier \"{V2_TIER_LABELS.get(tier, tier)}\": {meaning}.", V2_TIER_LABELS.get(tier, tier)
    if label == "Minimum Lot Size":
        if lot is None:
            return None, "No lot-size rule could be confirmed for this district.", "Not confirmed"
        if lot == 0:
            return "no_minimum", "The district has no lot-area minimum, so the lot component scores 0.", "No lot-area minimum"
        return "area", f"Smallest lot is {lot:,} sq ft; the log scale gives {points:.1f} of 20.", f"{lot:,} sq ft"
    if label == "Parking Mandate":
        if parking is None:
            return None, "No parking requirement was confirmed for this district's single-family use.", "Not confirmed"
        return "spaces", f"{parking} space(s) per unit; scored at {parking}/2.5 of the 10-point scale.", f"{parking} per unit"
    if label == "Demolition Delay":
        if demo is None:
            return None, "No demolition-delay period was confirmed in the source text for this district, so the component is excluded.", "Not confirmed"
        return "days", f"{demo}-day delay; scored at {demo}/180 of the 15-point scale.", f"{demo} days"
    return None, "", ""

V2_CORE_COMPONENTS = ("Multifamily Access", "Approval Discretion", "Minimum Lot Size", "ADU Approval Pathway")

def compute_v2_district(inputs, citations=None):
    use, approval, adu, lot, parking, demo = (inputs["use"], inputs["approval"], inputs["adu"],
                                              inputs["lot"], inputs["parking"], inputs["demo"])
    factors = [
        {"label": "Multifamily Access", "points": USE_PERMISSIONS_RUBRIC[use] if use else None, "max_points": 30},
        {"label": "Approval Discretion", "points": APPROVAL_PROCESS_RUBRIC[approval] if approval else None, "max_points": 10},
        {"label": "Minimum Lot Size", "points": lot_size_points(lot) if lot is not None else None, "max_points": 20},
        {"label": "ADU Approval Pathway", "points": ADU_PATHWAY_RUBRIC[adu] if adu and adu != "n/a" else None, "max_points": 15},
        {"label": "Parking Mandate", "points": parking_points(parking) if parking is not None else None, "max_points": 10},
        {"label": "Demolition Delay", "points": demolition_points(demo) if demo is not None else None, "max_points": 15},
    ]
    citations = citations or []
    for f in factors:
        _, reason, value = _factor_explanation(f["label"], inputs, f["points"])
        f["reason"] = reason
        f["value"] = value
        key = {"Multifamily Access": "use", "Approval Discretion": "use", "Minimum Lot Size": "lot",
               "ADU Approval Pathway": "adu", "Parking Mandate": "parking"}.get(f["label"])
        ev = next((c for c in citations if c["field"] == key), None) if key else None
        f["evidence"] = ev
        scale_key = {"Multifamily Access": "use", "Approval Discretion": "approval", "ADU Approval Pathway": "adu"}.get(f["label"])
        if scale_key:
            tier = {"use": use, "approval": approval, "adu": adu}[scale_key]
            rubric = {"use": USE_PERMISSIONS_RUBRIC, "approval": APPROVAL_PROCESS_RUBRIC, "adu": ADU_PATHWAY_RUBRIC}[scale_key]
            f["scale"] = [{"tier": t, "label": V2_TIER_LABELS[t], "points": rubric[t], "meaning": m, "active": t == tier}
                          for t, m in V2_TIER_SCALES[scale_key]]
        else:
            f["scale"] = None
        f["scale_note"] = V2_FACTOR_SCALE_NOTE[f["label"]]
    # Cross-town basis: only the components every compared town can document (the core four)
    # count toward the score. Parking and demolition delay stay on each district as context,
    # because Greenwich has no numeric single-family parking rule and Stamford and Bridgeport
    # have no quoted demolition-delay period, so including them would put towns on different scales.
    for f in factors:
        f["in_score"] = f["label"] in V2_CORE_COMPONENTS
    core = [f for f in factors if f["in_score"] and f["points"] is not None]
    achieved = sum(f["points"] for f in core)
    possible = sum(f["max_points"] for f in core)
    extended = [f for f in factors if f["points"] is not None]
    ext_possible = sum(f["max_points"] for f in extended)
    return {"score": round(achieved / possible * 100, 1) if possible else None,
            "score_extended": round(sum(f["points"] for f in extended) / ext_possible * 100, 1) if ext_possible else None,
            "components_scored": len(core),
            "components_confirmed": len(core) + (1 if adu == "n/a" else 0), "factors": factors}

def compute_v2_town(slug):
    land_path = os.path.join(LAND_DIR, f"{slug}.json")
    land = json.load(open(land_path))
    if slug == "norwalk":
        acres_by_code = {k: v["acres"] for k, v in land["districts_current_code"].items()}
    else:
        acres_by_code = {k: v["acres"] for k, v in land["districts"].items()}
    for alias, base in V2_ACRE_FOLD.get(slug, {}).items():
        if alias in acres_by_code and base not in acres_by_code:
            raise SystemExit(f"{slug}: acreage fold {alias} -> {base}: base district missing from land-area file")
        if alias in acres_by_code:
            acres_by_code[base] = acres_by_code[base] + acres_by_code.pop(alias)
    acres_norm = {V2_LOOKUP_NORMALIZE(k): (k, a) for k, a in acres_by_code.items()}
    results = []
    for code, inputs in V2_DISTRICTS[slug].items():
        key = V2_LOOKUP_NORMALIZE(code)
        if key not in acres_norm:
            raise SystemExit(f"{slug}: district {code} missing from land-area file")
        _, acres = acres_norm[key]
        cites = [c for c in (v2_citation(slug, code, f) for f in ("use", "lot", "adu", "adu_size", "parking")) if c]
        r = compute_v2_district(inputs, cites)
        results.append({"district": code, "acres": round(acres, 1), "score": r["score"],
                        "components_scored": r["components_scored"],
                        "components_confirmed": r["components_confirmed"], "score_extended": r["score_extended"],
                        "factors": r["factors"],
                        "note": inputs["note"], "citations": cites})
    V2_MIN_COMPONENTS = len(V2_CORE_COMPONENTS)
    for r in results:
        r["included"] = r["score"] is not None and r["components_confirmed"] >= V2_MIN_COMPONENTS
    scored = [r for r in results if r["included"]]
    total_acres = sum(r["acres"] for r in scored)
    for r in results:
        r["land_share"] = round(r["acres"] / total_acres * 100, 1) if r["included"] and total_acres else None
        r["contribution"] = round(r["score"] * r["acres"] / total_acres, 2) if r["included"] and total_acres else None
        if not r["included"]:
            r["exclusion_reason"] = ("No score: the district has no confirmed inputs." if r["score"] is None
                                     else f"Excluded: only {r['components_confirmed']} of the {V2_MIN_COMPONENTS} scored components are confirmed (all {V2_MIN_COMPONENTS} are required).")
    weighted = sum(r["score"] * r["acres"] for r in scored) / total_acres if total_acres else None
    return {
        "land_weighted_score": round(weighted, 1) if weighted is not None else None,
        "districts_included": len(scored),
        "acres_included": round(total_acres, 1),
        "districts": results,
        "formula": "V2 = sum(district score x acres) / sum(acres) over included districts",
        "method": ("Each district is scored with the same six-component rubric using only its own rules. "
                   "The score uses four components that every town can document (multifamily access, approval discretion, minimum lot size, ADU pathway); a district is included only if all four are confirmed. Parking and demolition delay are shown as context but not scored, so towns share one scale. The town V2 score is the land-area-weighted mean of included district scores; "
                   "acreage is from data/land_area/%s.json. Components with no confirmed input "
                   "are excluded per district." % slug),
    }

for slug in V2_DISTRICTS:
    TOWNS[slug]["v2"] = compute_v2_town(slug)

os.makedirs(TOWNS_DIR, exist_ok=True)
for slug, t in TOWNS.items():
    with open(os.path.join(TOWNS_DIR, f"{slug}.json"), "w") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)

total_vars = sum(len(t["variables"]) for t in TOWNS.values())
print(f"Wrote {len(TOWNS)} town files to {TOWNS_DIR} ({total_vars} variables total, avg {total_vars/len(TOWNS):.1f}/town)")
