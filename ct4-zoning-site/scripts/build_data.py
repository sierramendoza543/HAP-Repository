#!/usr/bin/env python3
"""Builds /data/towns/*.json and /data/sources/*.json from research findings.
Each metric carries a citation: {source, page, cite} so the UI can jump a PDF
viewer straight to the right page (and NZA-sourced metrics link to the live
snapshot instead of a PDF page, since there is no PDF for those numbers)."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOWNS_DIR = os.path.join(ROOT, "data", "towns")
SOURCES_DIR = os.path.join(ROOT, "data", "sources")

def nza(jid):
    return {"kind": "nza", "id": f"nza-{jid}", "url": f"https://edit.zoningatlas.org/statsrollup/jurisdiction/{jid}/", "title": "NZA Jurisdiction Snapshot"}

def pdf(slug, file, title, live_url):
    return {"kind": "pdf", "id": f"{slug}-pdf", "file": f"/sources/{file}", "url": live_url, "title": title}

def link(slug, title, live_url):
    return {"kind": "link", "id": f"{slug}-link", "url": live_url, "title": title}

TOWNS = {}

def add(slug, name, jurisdiction_id, population, land_area_acres, districts_analyzed,
        composite_score, nza_metrics, primary_source, restrictive, permissive, caveat):
    TOWNS[slug] = {
        "slug": slug, "name": name, "jurisdiction_id": jurisdiction_id,
        "population": population, "land_area_acres": land_area_acres,
        "districts_analyzed": districts_analyzed, "composite_score": composite_score,
        "last_checked": "2026-10-15",
        "nza_metrics": nza_metrics,
        "primary_source": primary_source,
        "restrictive": restrictive,
        "permissive": permissive,
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

def fact(label, value, source, cite):
    return {"label": label, "value": value, "source": source, "cite": cite}

# ---------------- GREENWICH ----------------
gw_src = pdf("greenwich", "greenwich-div9.pdf", "Building Zone Regulations, Div. 9 (Use Regs, Aug. 2023)", "https://www.greenwichct.gov/DocumentCenter/View/37828")
gw_src21 = pdf("greenwich21", "greenwich-div21.pdf", "Building Zone Regulations, Div. 21 (Bulk Schedule)", "https://www.greenwichct.gov/DocumentCenter/View/37841")
add("greenwich", "Greenwich", 317, 64594, 30322, 49, 82.7,
    nza_block(317, 95.3, 97.7, 98.3, 59.8, 92),
    gw_src,
    {"district": "R-20 / RA-2 (and RA-4, RA-1, R-12)",
     "facts": [
        fact("Single-family", "Allowed by-right — only permitted use", gw_src, "Sec. 6-93(a)(1)"),
        fact("Two-family", "Prohibited", gw_src, "Sec. 6-93 / 6-94 (no provision)"),
        fact("3-/4+-family", "Prohibited", gw_src, "Sec. 6-93 / 6-94 (no provision)"),
        fact("Min. lot size (RA-2)", "20,000 sq ft (2 acres)", gw_src21, "Sec. 6-205(a) table"),
     ]},
    {"district": "R-MF",
     "facts": [
        fact("Two-family / multifamily", "Special Permit only, no distinct 3-unit tier", gw_src, "Sec. 6-98.1(a)(2)(A)"),
        fact("Min. lot area, multifamily tier", "2,400 sq ft/family", gw_src21, "Sec. 6-205(a)"),
     ]},
    "Town adopted 2025–2026 amendments (nursing-home conversions, multifamily parking per PA 25-1) not fully reflected in the Aug. 2023 PDF — verify against the amendment list before external use.")

# ---------------- BRIDGEPORT ----------------
bp_src = pdf("bridgeport", "bridgeport-zoning.pdf", "\"Zone Bridgeport\" form-based code (amended July 2022)", "https://portal.ct.gov/-/media/CSC/1_Dockets-medialibrary/1_MEDIA_DO500_600/DO516/ApplicantSubmissions/Application/UI---City-of-Bridgeport-Zoning-Code-Amended-July-25-2022.pdf")
add("bridgeport", "Bridgeport", 311, 151599, 10246, 25, 15.5,
    nza_block(311, 31.5, 39.3, 37.9, 0.0, 0),
    bp_src,
    {"district": "N1 (Neighborhood: Traditional)",
     "facts": [
        fact("Single-family", "Allowed by-right, 1 unit in House A", bp_src, "Sec. 3.90.9"),
        fact("Two-family", "No 2-unit option exists in N1", bp_src, "Sec. 3.90.9"),
        fact("Min. lot width", "45 ft (no lot area minimum)", bp_src, "Sec. 3.90.4"),
     ]},
    {"district": "NX2 (Neighborhood Mix)",
     "facts": [
        fact("Up to 4 units", "By-right, no special permit, + 1 backyard cottage", bp_src, "Sec. 3.90.9"),
        fact("Double House A", "Up to 4 by-right / 6 with special permit", bp_src, "Sec. 3.80.9"),
        fact("Parking minimum (citywide)", "None — Sec. 8.20.1 sets no residential minimum", bp_src, "Sec. 8.20.1"),
     ]},
    "A 2025 proposal (25-23) to add residential parking minimums citywide was found but its adoption status is unconfirmed.")

# ---------------- STAMFORD ----------------
sf_src = pdf("stamford", "stamford-zoning.pdf", "Zoning Regulations, City of Stamford (through July 10, 2024)", "https://stamfordct.gov/home/showpublisheddocument/5847/638568338177670000")
add("stamford", "Stamford", 304, 139134, 23707, 46, 64.7,
    nza_block(304, 86.5, 87.9, 73.9, 21.9, 100),
    sf_src,
    {"district": "R-20 (One-Family Residence)",
     "facts": [
        fact("Two-family / multifamily", "Both prohibited", sf_src, "Table I"),
        fact("Min. lot size", "20,000 sq ft", sf_src, "Table II"),
     ]},
    {"district": "R-6 (One-Family, Two-Family Residence)",
     "facts": [
        fact("Two-family", "Allowed by-right", sf_src, "Table I"),
        fact("Multifamily (3+)", "Still prohibited", sf_src, "Table I"),
        fact("Min. lot size", "5,000 sq ft (1F) / 6,000 sq ft (2F)", sf_src, "Table II"),
     ]},
    "Live stamfordct.gov PDF was blocked by bot-protection during research; a Wayback Machine snapshot of the identical text was used — recommend re-verifying the live link.")

# ---------------- NORWALK ----------------
nw_src = pdf("norwalk", "norwalk-art3.pdf", "Norwalk Zoning Regulations, Art. 3 (Zoning Districts, eff. Feb. 2024)", "https://www.norwalkct.gov/DocumentCenter/View/32245")
nw_bulk = pdf("norwalkbulk", "norwalk-bulk.pdf", "Norwalk Bulk & Height Schedule (7/9/2025)", "https://www.norwalkct.gov/DocumentCenter/View/36646")
add("norwalk", "Norwalk", 303, 93661, None, 23, 55.9,
    nza_block(303, 77.5, 81.9, 81.9, 0.0, 100),
    nw_src,
    {"district": "CD-1S (Sub-Urban Single-Family)",
     "facts": [
        fact("Two-family / multifamily", "Both \"NP\" (Not Permitted)", nw_src, "Table 4.3.9.A"),
        fact("Min. lot size", "6,250 sq ft", nw_bulk, "Bulk & Height Schedule"),
     ]},
    {"district": "CD-2 (Sub-Urban Single- & Two-Family)",
     "facts": [
        fact("Two-family", "\"P\" — permitted by right", nw_src, "Table 4.3.9.A"),
        fact("Multifamily", "Still \"NP\"", nw_src, "Table 4.3.9.A"),
        fact("Min. lot size", "5,000 sq ft", nw_bulk, "Bulk & Height Schedule"),
     ]},
    "CD-3/CD-4 allow multifamily by-right-with-limitations, but column alignment for CD-3W/CD-4W sub-variants was ambiguous in the extracted PDF text — not reported to avoid miscitation.")

# ---------------- DARIEN (no local PDF; link out) ----------------
dn_src = link("darien", "Darien Zoning Regulations (last revised May 10, 2026)", "https://www.darienct.gov/DocumentCenter/View/6613")
add("darien", "Darien", 302, 22528, None, 26, 74.5,
    nza_block(302, 97.0, 97.0, 97.0, 32.4, 100),
    dn_src,
    {"district": "R-1 (and R-2 / R-1/2 / R-1/3 / R-1/5)",
     "facts": [
        fact("Only single-family permitted", "2-/3-/4+-family prohibited town-wide", dn_src, "§402.a"),
        fact("Min. lot size (R-1)", "43,560 sq ft (1 acre)", dn_src, "§406"),
     ]},
    {"district": "DMR (Designed Multi-Family Residential)",
     "facts": [
        fact("Multifamily", "Special Permit only", dn_src, "§524.a"),
        fact("Density", "4 DU/net acre by-right (6 with 20% affordable)", dn_src, "§526.1"),
     ]},
    "Darien formally opted OUT of CT's statewide ADU law (PA 21-29) via local vote in 2022; its own local ADU rules sunset for new applications after June 30, 2029 unless readopted.")

# ---------------- NEW CANAAN ----------------
nc_src = pdf("newcanaan", "newcanaan-zoning.pdf", "New Canaan Zoning Regulations (amended through May 1, 2023)", "https://cms3.revize.com/revize/newcanaanct/Departments/Land%20Use/Zoning%20Regulations.pdf")
add("new-canaan", "New Canaan", 319, 21160, None, 24, 92.4,
    nza_block(319, 97.4, 98.3, 98.3, 81.3, 100),
    nc_src,
    {"district": "Four Acre Residence Zone",
     "facts": [
        fact("2-/3-/4+-family", "Prohibited outright (except age-restricted via special permit)", nc_src, "Sec. 3.2.C.2-3"),
        fact("Min. lot size", "174,240 sq ft (4 acres)", nc_src, "Sec. 3.5.A.1"),
     ]},
    {"district": "Apartment Zone",
     "facts": [
        fact("Two-family & multifamily", "Both Special Permit only", nc_src, "Sec. 5.4.C.1-2"),
        fact("Max density", "1 unit / 5,000 sq ft", nc_src, "Sec. 5.4.D.1"),
     ]},
    "No as-of-right multifamily district exists anywhere in New Canaan — every multi-unit pathway requires a discretionary Special Permit hearing.")

# ---------------- WESTPORT (no local PDF; link out) ----------------
wp_src = link("westport", "Westport Zoning Regulations (eff. April 12, 2024)", "https://online.encodeplus.com/regs/westport-ct/")
add("westport", "Westport", 329, 27996, None, 40, 35.2,
    nza_block(329, 0.6, 0.3, 0.2, 38.0, 100),
    wp_src,
    {"district": "Residence AAA",
     "facts": [
        fact("Two-family / multifamily", "Prohibited as normal use (only via §32-12 Special Permit)", wp_src, "§11-2.1.1"),
        fact("Min. lot size", "2 acres", wp_src, "§11-3"),
     ]},
    {"district": "Residence C",
     "facts": [
        fact("Two-family", "Allowed BY RIGHT as a principal use", wp_src, "§18-2.1.2"),
        fact("Max density", "Up to 10 units/gross acre", wp_src, "§18-4.1"),
     ]},
    "A 2026 amendment (§34-14.1) eliminated minimum parking entirely for residential developments of 16 units or fewer townwide.")

# ---------------- WILTON (no local PDF; link out) ----------------
wl_src = link("wilton", "Wilton Zoning Regulations (last revised Sept. 2026)", "https://www.wiltonct.gov/planning-zoning-department/files/regulations-document-october-7")
add("wilton", "Wilton", 330, 19255, None, 19, 95.4,
    nza_block(330, 98.5, 98.7, 98.7, 88.8, 100),
    wl_src,
    {"district": "R-2A",
     "facts": [
        fact("\"Two-family\"/\"three-family\"", "Do not exist anywhere in the 337-page code", wl_src, "full-text search"),
        fact("Multifamily", "Prohibited in R-2A", wl_src, "§29-5.A.2.a"),
        fact("Min. lot size", "2 acres", wl_src, "§29-5.D"),
     ]},
    {"district": "HODD (Housing Opportunity Development District)",
     "facts": [
        fact("Multi-family attached dwellings", "Permitted \"as a matter of right\"", wl_src, "§29-5.E.8"),
        fact("Density / affordability", "10 units/gross acre, 30% affordable required", wl_src, "§29-5.E.9"),
     ]},
    "HODD sites are capped between 9 and 11 acres — a narrow, purpose-built carve-out, not a general-purpose multifamily zone.")

# ---------------- RIDGEFIELD (no local PDF; link out) ----------------
rf_src = link("ridgefield", "Ridgefield Zoning Regulations (revised through July 2026)", "https://ridgefieldct.gov/Documents/Boards%20Committees%20and%20Commissions/Planning%20and%20Zoning%20Commission/About%20PZC%20Meetings/Zoning%20Regulations/Zoning%20Regulations%20July%2026.pdf")
add("ridgefield", "Ridgefield", 323, 25300, None, 21, 61.8,
    nza_block(323, 95.8, 95.6, 95.6, 0.0, 97),
    rf_src,
    {"district": "RAAA",
     "facts": [
        fact("Single-family", "Allowed, requires Zoning Permit", rf_src, "Sec. 3.2.B.1"),
        fact("2-/3-family", "Bundled & prohibited except by Special Permit in SD R-20 overlay", rf_src, "Sec. 3.2.C.10.d"),
        fact("Min. lot size", "130,680 sq ft (3 acres)", rf_src, "Sec. 3.5.A"),
     ]},
    {"district": "MFDD (Multi-Family Development District)",
     "facts": [
        fact("Multifamily", "Special Permit only, town's only multifamily pathway", rf_src, "Sec. 4.2.B-C"),
        fact("Density", "6 units/acre (8 with 15% affordable)", rf_src, "Sec. 4.2.C"),
     ]},
    "Ridgefield has no as-of-right multifamily district of any kind — every multi-unit path requires a discretionary Special Permit hearing.")

# ---------------- WESTON (no local PDF; link out, blocked by WAF) ----------------
ws_src = link("weston", "Weston Zoning Regulations (amended through July 7, 2025)", "https://www.westonct.gov/home/showpublisheddocument/15463/638937003479630000")
add("weston", "Weston", 328, 10490, 12157, 3, 100.0,
    nza_block(328, 99.9, 99.9, 99.9, 100.0, 100),
    ws_src,
    {"district": "R-2A (Two Acre Residential and Farming District)",
     "facts": [
        fact("Entire town's base zone", "2-/3-/4+-family prohibited, not addressed anywhere", ws_src, "Sec. 321"),
        fact("Min. lot size", "2 acres", ws_src, "Sec. 321"),
     ]},
    {"district": "Village District / VD-R",
     "facts": [
        fact("All uses, incl. multifamily", "Require Special Permit", ws_src, "Sec. 322"),
        fact("Affordability", "5+ unit projects must set aside ≥15% affordable", ws_src, "Sec. 322"),
     ]},
    "Town's own PDF was blocked by a bot-detection wall during research; base-district figures came from a 2021-dated third-party copy, and the R-2A parking minimum could not be located — flagged for direct verification with Weston Land Use.")

# ---------------- EASTON (no local PDF; link out, HTML error page) ----------------
es_src = link("easton", "Easton Zoning Regulations (last revised July 7, 2024)", "https://ct-easton.civicplus.com/DocumentCenter/View/3109")
add("easton", "Easton", 316, 7815, 17110, 3, 96.9,
    nza_block(316, 100, 100, 100, 91.4, 100),
    es_src,
    {"district": "Residence A / Residence B",
     "facts": [
        fact("\"Two-family\", \"duplex\", \"multi-family\", \"three-family\"", "Zero mentions anywhere in the 6,576-line regulations", es_src, "exhaustive keyword search"),
        fact("Min. lot size", "40,000 sq ft (Res. A) / 3 acres (Res. B)", es_src, "Sec. 3510"),
     ]},
    {"district": "None exists",
     "facts": [
        fact("Multifamily pathway", "None — not even by special permit, in any district", es_src, "full code review"),
     ]},
    "Of all 17 towns researched, Easton is the single clearest case of total legal exclusion of 2+-family housing — confirmed by exhaustive keyword search, not an oversight.")

# ---------------- FAIRFIELD ----------------
ff_src = pdf("fairfield", "fairfield-zoning.pdf", "Fairfield Zoning Regulations (eff. Sept. 6, 2025)", "https://fairfieldct.gov/Fairfield_ZoningRegulations_Adopted_Effective_09062025%20-%20updated%209.28.26.pdf")
add("fairfield", "Fairfield", 315, 65300, 18618, 17, 61.7,
    nza_block(315, 91.2, 95.8, 95.1, 0.0, 100),
    ff_src,
    {"district": "AAA / AA / R-3 / R-2 / A (Single-Family Residence Districts)",
     "facts": [
        fact("No multi-unit housing category", "Exists at all in these five districts", ff_src, "Sec. 3.2"),
        fact("Min. lot size", "2 acres (AAA) down to 9,375 sq ft (A)", ff_src, "Sec. 3.3.1"),
     ]},
    {"district": "District C (Multi-Family Residence)",
     "facts": [
        fact("2-, 3-, AND 4-family", "All permitted BY RIGHT, each with its own lot-area minimum", ff_src, "Sec. 5.2"),
        fact("Lot minimums", "7,500 / 10,000 / 12,500 sq ft", ff_src, "Sec. 5.3.1"),
     ]},
    "Fairfield is the clearest \"permissive\" comparison case among the 17 towns — a genuine, explicitly tiered by-right multifamily district.")

# ---------------- REDDING ----------------
rd_src = pdf("redding", "redding-zoning.pdf", "Redding Zoning Regulations (amendments through Feb. 15, 2024)", "https://reddingct.gov/wp-content/uploads/2025/10/Redding-Zoning-Regulations-1.24.24.pdf")
add("redding", "Redding", 322, 8830, 19732, 12, 99.1,
    nza_block(322, 99.2, 98.9, 98.9, 98.7, 100),
    rd_src,
    {"district": "R-1 (and R-4 / R-2 / R-½)",
     "facts": [
        fact("2-/3-/4+-family", "All prohibited; no 3-unit tier at all", rd_src, "§4.2"),
        fact("Min. lot size (R-1)", "1 acre", rd_src, "§4.6"),
     ]},
    {"district": "RV (Village Residential)",
     "facts": [
        fact("Multifamily", "Special Permit only, capped at 1 unit/8,000 sq ft", rd_src, "§4.2.3(o)"),
     ]},
    "Redding's ADU rules give no size figure for detached ADUs in R-4 — a likely drafting gap rather than a deliberate restriction.")

# ---------------- MONROE ----------------
mn_src = pdf("monroe", "monroe-zoning.pdf", "Monroe Zoning Regulations (amended through July 2, 2026)", "https://www.monroect.gov/Home/DownloadDocument?docId=82b32408-e8ae-4afd-b9ca-58f87c1e35da")
add("monroe", "Monroe", 318, 19269, 16323, 16, 72.8,
    nza_block(318, 95.2, 80.0, 80.0, 48.4, 89),
    mn_src,
    {"district": "RF-1 (Residential and Farming District 1)",
     "facts": [
        fact("Multifamily (incl. 2-unit, by Monroe's own definition)", "Prohibited (\"x\")", mn_src, "§10.1 Use Schedule"),
        fact("Min. lot size", "1 acre", mn_src, "Art. 3 §3.1.4(A)"),
     ]},
    {"district": "MFR (Multifamily Residence District)",
     "facts": [
        fact("Multifamily", "Special Exception Permit, 2.5 units/gross acre (attached)", mn_src, "§3.4.5(A)"),
        fact("Min. parcel to create district", "70 contiguous acres", mn_src, "§3.4.5(B)"),
     ]},
    "Monroe's code does not distinguish a 3-unit tier from larger multifamily — its own definition of \"multi-family\" legally includes buildings with as few as 2 units.")

# ---------------- TRUMBULL ----------------
tb_src = pdf("trumbull", "trumbull-zoning.pdf", "Trumbull Zoning Regulations (amended through Aug. 19, 2026)", "https://trumbull-ct.gov/DocumentCenter/View/1323")
add("trumbull", "Trumbull", 327, 38073, 14786, 25, 63.6,
    nza_block(327, 99.6, 98.8, 98.0, 0.0, 99),
    tb_src,
    {"district": "Residence Zone A / AA / AAA",
     "facts": [
        fact("2-/3-/4+-family", "Prohibited as a base use", tb_src, "Art. II §1.1.1(1)"),
        fact("Min. lot size", "½ to 1 acre", tb_src, "Art. I §2"),
     ]},
    {"district": "MFO (Multi-Family Overlay)",
     "facts": [
        fact("Multifamily", "Special Permit only, existing industrial land ≥10 acres", tb_src, "Art. II §7.6.2"),
        fact("Town-wide cap", "600 units total", tb_src, "Art. II §7.6.4"),
     ]},
    "Trumbull currently has a town-wide moratorium on new multifamily rental applications above 50 units (except 55+ housing), expiring Feb. 28, 2027.")

# ---------------- SHELTON ----------------
sh_src = pdf("shelton", "shelton-zoning.pdf", "City of Shelton Zoning Regulations (recodified April 16, 2024)", "https://shelton.qscendcms.com/ckfinder/connector?command=Proxy&lang=en&type=Files&currentFolder=%2F&hash=c245c263ce0eced480effe66bbede6b4d46c15ae&fileName=2024%20Regulation%20scanned.pdf")
add("shelton", "Shelton", 324, 42805, 19384, 26, 60.4,
    nza_block(324, 90.1, 90.1, 89.8, 4.1, 95),
    sh_src,
    {"district": "R-1",
     "facts": [
        fact("2-/3-family & 4+-family", "Both prohibited (\"X\")", sh_src, "Schedule A Row 2/2A/3"),
        fact("Min. lot size", "40,000 sq ft", sh_src, "Schedule B Row 1"),
     ]},
    {"district": "R-4",
     "facts": [
        fact("2-/3-family & multifamily (4-12 units)", "Allowed by Special Exception", sh_src, "Schedule A Row 2/2A/3"),
        fact("Min. lot area per unit (2F)", "7,500 sq ft", sh_src, "Schedule B Row 2"),
     ]},
    "Shelton's own code is a scanned, image-only PDF with no text layer — all figures were OCR'd and visually verified against the table images directly.")

# ---------------- STRATFORD (no local PDF; ecode360 HTML, link out) ----------------
st_src = link("stratford", "Stratford Zoning Code Ch. A220 (eff. Jan. 1, 2025)", "https://ecode360.com/9207545")
add("stratford", "Stratford", 326, 53610, 11017, 28, 33.8,
    nza_block(326, 84.2, 1.5, 0.9, 0.0, 100),
    st_src,
    {"district": "RS-1",
     "facts": [
        fact("\"Two and Three Family Dwellings\"", "One combined row, not permitted", st_src, "§3.2.1"),
        fact("4+-unit multifamily", "Only by Special Permit", st_src, "§4.2.4 Use Table"),
        fact("Min. lot size", "40,000 sq ft", st_src, "§3.2.1"),
     ]},
    {"district": "RM-1 (Two and Three Family Residence)",
     "facts": [
        fact("2- and 3-family", "Allowed BY RIGHT", st_src, "§3.2.2"),
        fact("Min. lot area per unit", "2,500 sq ft", st_src, "§3.2.2"),
     ]},
    "An apparent inconsistency exists between the Use Table's \"4 or more units\" threshold and §5.1's \"(3+)\" heading for Special Permit review — flagged for follow-up.")

os.makedirs(TOWNS_DIR, exist_ok=True)
for slug, t in TOWNS.items():
    with open(os.path.join(TOWNS_DIR, f"{slug}.json"), "w") as f:
        json.dump(t, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(TOWNS)} town files to {TOWNS_DIR}")
