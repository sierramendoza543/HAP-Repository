"""Recompute the National Zoning Atlas Jurisdiction Snapshot figures for Greenwich from our own
sources: Div. 9 (use regulations), Div. 21 (bulk schedule), Div. 15 (parking) of the Building Zone
Regulations mirrored in public/sources, and our district acreage (data/land_area/greenwich.json).

Run with: python3 -I scripts/replicate_nza_greenwich.py
Writes data/nza_replication/greenwich.json.

Rules of the method
- A district is residential land only if the text of Div. 9 shows at least one dwelling type allowed in it.
- A status is read from the text or it is 'unclassified'. Districts whose rules are not in the mirrored
  Div. 9/15/21 (the RA-C / R-C / RA-CC conservation zones, R-PR, R-PHD-*) are NOT guessed: their acreage is
  reported separately and used only in the lower/upper bounds.
- Every rule quote below is checked against the PDF text at run time; a quote that is not found stops the run.
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "public", "sources")
FAMS = ["1-family", "2-family", "3-family", "4+-family"]
STATUSES = ["as_of_right", "hearing", "prohibited", "unclassified"]
LOT_BINS = [("None", 0, 1), ("Less than 10,000 sq ft", 1, 10000), ("10,000 to 19,999 sq ft", 10000, 20000),
            ("20,000 to 39,999 sq ft", 20000, 40000), ("40,000 to 79,999 sq ft", 40000, 80000),
            ("80,000 sq ft or more", 80000, 10 ** 9)]


def pdf_text(name):
    out = subprocess.run(["pdftotext", "-q", "-layout", os.path.join(SRC, name), "-"],
                         capture_output=True, text=True, check=True).stdout
    return re.sub(r"\s+", " ", out.replace("‐", "-").replace("‑", "-").replace("–", "-"))


TXT = {"div9": pdf_text("greenwich-div9.pdf"), "div21": pdf_text("greenwich-div21.pdf"),
       "div15": pdf_text("greenwich-div15.pdf")}


def q(doc, quote):
    """Return the quote after proving it appears in the PDF text."""
    flat = re.sub(r"\s+", " ", quote.replace("–", "-"))
    if flat not in TXT[doc]:
        raise SystemExit(f"quote not found in {doc}: {quote}")
    return {"doc": f"greenwich-{doc}.pdf", "quote": quote}


# ---------------------------------------------------------------- rule sets (each status cites a section)
def cite(sec, doc, quote, note=None):
    d = {"section": sec, **q(doc, quote)}
    if note:
        d["note"] = note
    return d


C_SF = cite("Sec. 6-93(a)", "div9", "Detached single family dwellings, one (1) per lot.")
C_EXCL = cite("Sec. 6-93(a)", "div9", "and all other principal uses are expressly excluded:")
C_R7 = cite("Sec. 6-97(a)(1)", "div9", "All uses permitted in RA-4 zones and uses permitted under Sec. 6-94.")
C_R7X = cite("Sec. 6-97(a)", "div9", "and all other principal uses are expressly excluded in R-7 zones")
C_R6_1 = cite("Sec. 6-98(a)(1)", "div9", "All uses permitted in R-7 zones.")
C_R6_2 = cite("Sec. 6-98(a)(3)(A)", "div9", "Administrative site plan approval is required on lots of 7,500 square feet or larger for",
              "New two-family dwellings need administrative site plan approval, with no public hearing, on lots of 7,500 sq ft or more. "
              "Special permit is needed on smaller lots (Sec. 6-98(a)(4)(A)). Sec. 6-101(d) separately says a special permit is required "
              "for two or more dwelling units on a lot in residential zones; we read the specific R-6 rule as controlling and flag it as unresolved.")
C_R6X = cite("Sec. 6-98(a)", "div9", "are permitted and all other principal uses are expressly excluded in the R-6",
             "Sec. 6-98(a)(2) allows only additions or renovations to EXISTING two-/multi-family dwellings, not new ones.")
C_MF1 = cite("Sec. 6-98.1(a)(1)", "div9", "All uses permitted in R-7 zones.")
C_MF2 = cite("Sec. 6-98.1(a)(2)(A)", "div9", "The building of a two family dwelling, conversion from a single family to a two-family dwelling")
C_MF3 = cite("Sec. 6-98.1(a)(2)(A)", "div9", "addition or alteration to one or more multi-family dwellings or a combination of single family, two-family",
             "Multi-family is not split by unit count in the text, so 3-family and 4+-family get the same special-permit status.")
C_BIZ_UG3 = cite("Sec. 6-100, Use Group 3", "div9", "Dwelling units conforming to the provisions of Sec. 6-110.")
C_BIZ_SITE = cite("Sec. 6-110(F)(1)", "div9", "A site plan application is required when the development proposal is four (4) units or fewer",
                  "Site plan approval only (no special permit) for 4 or fewer units; the code does not distinguish unit types, so 1-, 2- and 3-family "
                  "are read as site-plan-only. Assumption: a stand-alone single dwelling counts as a 'dwelling unit' under Use Group 3.")
C_BIZ_SP = cite("Sec. 6-110(F)(2)", "div9", "A special permit and site plan are required when the development proposal is five (5) units",
                "5 or more units need a special permit; a 4-unit building is site-plan-only, so 4+-family is split and we code the class 'hearing'.")
C_BIZ_OK = cite("Sec. 6-110(c)(1)", "div9", "Dwelling units are permitted within residential or mixed-use development in the LB, LBR-2, CGB, CBGR, GB and GBO zones")
C_WB_NOLIST = cite("Sec. 6-100", "div9", "Any use not specifically listed in the following Use Groups shall be prohibited",
                   "WB (Sec. 6-107(b)) permits only Use Groups 7a, 7b, 7c; none lists single-family or two-family dwellings by name.")
C_WB_MF = cite("Sec. 6-107(b), Use Group 7c", "div9", "Multi Family Dwellings.",
               "Use Group 7c requires a special permit (Sec. 6-107(b)); multi-family design standards in Sec. 6-107(c)(4).")
C_WB_SP = cite("Sec. 6-107(b)", "div9", "Use Group 7c (special permit required)")
C_INDRE = cite("Sec. 6-112(6)(a)", "div9", "Any proposed use within an IND-RE zone, and any modification of the standards and requirements of the underlying zone")
C_INDRE_B = cite("Sec. 6-112(6)(b)", "div9", "any use or uses permitted in any business zone")


def rule(**kw):
    return kw


RULES = {
    "sf_zone": rule(label="RA-4/RA-2/RA-1/R-20/R-12: single-family only", residential=True,
                    s={"1-family": ("as_of_right", C_SF), "2-family": ("prohibited", C_EXCL),
                       "3-family": ("prohibited", C_EXCL), "4+-family": ("prohibited", C_EXCL)}),
    "r7": rule(label="R-7: uses of RA-4 plus Sec. 6-94 only", residential=True,
               s={"1-family": ("as_of_right", C_R7), "2-family": ("prohibited", C_R7X),
                  "3-family": ("prohibited", C_R7X), "4+-family": ("prohibited", C_R7X)}),
    "r6": rule(label="R-6: single-family, two-family by administrative site plan", residential=True,
               s={"1-family": ("as_of_right", C_R6_1), "2-family": ("as_of_right", C_R6_2),
                  "3-family": ("prohibited", C_R6X), "4+-family": ("prohibited", C_R6X)}),
    "rmf": rule(label="R-MF: two-family and multi-family by special permit", residential=True,
                s={"1-family": ("as_of_right", C_MF1), "2-family": ("hearing", C_MF2),
                   "3-family": ("hearing", C_MF3), "4+-family": ("hearing", C_MF3)}),
    "biz": rule(label="Business zone permitting Use Group 3 dwellings (Sec. 6-110)", residential=True,
                s={"1-family": ("as_of_right", C_BIZ_SITE), "2-family": ("as_of_right", C_BIZ_SITE),
                   "3-family": ("as_of_right", C_BIZ_SITE), "4+-family": ("hearing", C_BIZ_SP)}),
    "wb": rule(label="WB: multi-family by special permit (Use Group 7c)", residential=True,
               s={"1-family": ("prohibited", C_WB_NOLIST), "2-family": ("unclassified", C_WB_MF),
                  "3-family": ("hearing", C_WB_SP), "4+-family": ("hearing", C_WB_SP)}),
    "indre": rule(label="Business zone with IND-RE overlay: any use needs a special permit", residential=True,
                  s={f: ("hearing", C_INDRE) for f in FAMS}),
    "nonres": rule(label="No dwelling use in the zone's use list", residential=False),
}
NONRES_CITE = {
    "BEX-50": cite("Sec. 6-108(b)-(d)", "div9", "Offices Uses (as defined in Section 6-5(a) (38.2) of the Regulations)",
                   "Permitted uses are offices, reservations, cemeteries; only employee lodgings/caretaker quarters as accessory uses (Sec. 6-108(d)(2))."),
    "H": cite("Sec. 6-113(b)", "div9", "The following principal uses are permitted in the Hospital Zones, H-1 and H-2:",
              "Hospital and support uses only; no dwellings."),
}

# district code -> (rule key, note)
OVERLAY_NOTE = ("Historic Overlay (Sec. 6-109): the code treats HO as a rezoning on top of the base district; the base-district use rules still govern, "
                "and the HO only lets the Commission authorize extra units by special permit (Sec. 6-109(d)(3)). Counted at the base district's status.")
DISTRICTS = {}
for c in ("RA-4", "RA-2", "RA-1", "R-20", "R-12"):
    DISTRICTS[c] = ("sf_zone", None)
for c in ("RA-2-HO", "RA-1-HO", "R-20-HO", "R-12-HO"):
    DISTRICTS[c] = ("sf_zone", OVERLAY_NOTE)
DISTRICTS["R-7"] = ("r7", None)
DISTRICTS["R-7-HO"] = ("r7", OVERLAY_NOTE)
DISTRICTS["R-6"] = ("r6", None)
DISTRICTS["R-6-HO"] = ("r6", OVERLAY_NOTE)
DISTRICTS["R-MF"] = ("rmf", None)
for c in ("LB", "LBR-2", "CGB", "CGBR", "GB", "GBO"):
    DISTRICTS[c] = ("biz", None)
for c in ("LB-HO", "LBR-2-HO", "CGB-HO", "CGBR-HO", "GB-HO"):
    DISTRICTS[c] = ("biz", "Historic Overlay on a business zone: base-zone status used (Sec. 6-109(d)(1)).")
DISTRICTS["LBR-1"] = ("biz", "Sec. 6-103(G) lists Use Group 3 for all LBR zones, but Sec. 6-110(c)(1) names only LBR-2; read from Sec. 6-103(G). Flagged.")
DISTRICTS["LBR-1-HO"] = ("biz", "As LBR-1, with Historic Overlay.")
DISTRICTS["WB"] = ("wb", None)
DISTRICTS["GB-IND-RE"] = ("indre", "GB with Industrial Re-Use overlay (Sec. 6-112): every use needs a special permit; dwellings follow the underlying business-zone limits.")
DISTRICTS["BEX-50"] = ("nonres", "BEX-50")
DISTRICTS["H-1"] = ("nonres", "H")
DISTRICTS["H-2"] = ("nonres", "H")

# Districts whose use rules are not in the mirrored Div. 9/15/21. Never guessed.
UNCLASSIFIED_RES = {  # GIS zone_type says Residential, but no text for the district was found
    "RA-C4": "RA-C (conservation) zone family: no use text in Div. 9, 15 or 21",
    "RA-C2": "same", "RA-C1": "same", "RA-CC4": "RA-CC family: no use text in Div. 9, 15 or 21",
    "RA-CC4-HO": "same, with Historic Overlay", "R-C7": "R-C family: no use text in Div. 9, 15 or 21", "R-C12": "same",
    "R-C20": "same", "R-C7-HO": "same, with Historic Overlay", "RC-20-HO": "same, with Historic Overlay",
    "RC-12-HO": "same, with Historic Overlay",
    "R-PR": "Sec. 6-38-type planned-residential zone: Div. 6 is not mirrored in public/sources",
    "R-PHD-SU": "R-PHD (Div. 6) small-unit zone: not in mirrored Div. 9/15/21",
    "R-PHD-E": "R-PHD (Div. 6) elderly zone: not in mirrored Div. 9/15/21 (Sec. 6-155(2) only mentions it for parking)",
    "R-6-HRO": "R-6 base is known, but 'HRO' overlay text is not in the mirrored Div. 9",
}
UNCLASSIFIED_OTHER = {  # type unknown; kept out of the residential base
    "BEX-50-R": "no text for the BEX-50-R district; GIS zone type blank",
    "P": "no text for the P district in Div. 9/15/21",
    "HRO": "'HRO' overlay text not in the mirrored Div. 9",
    "LB-R-C7-HO": "mixed LB / R-C7 overlay code; R-C7 text not available",
}

# Minimum lot area, sq ft, for 1-family (Div. 21, Sec. 6-205(a) residential schedule)
LOT = {"RA-4": (4 * 43560, "4 Acres"), "RA-2": (2 * 43560, "2 Acres"), "RA-1": (43560, "1 Acre"),
       "R-20": (20000, "20,000"), "R-12": (12000, "12,000"), "R-7": (7500, "7,500"),
       "R-6": (7500, "7,500 sq. ft. 60 ft."), "R-MF": (3600, "3,600")}
for _k, (_v, _quote) in LOT.items():
    q("div21", _quote)
LOT_SEC = "Sec. 6-205(a) bulk schedule (Div. 21), row for the district"
BIZ_LOT_NOTE = ("Sec. 6-205(b) lists 'Note 1' (= Sec. 6-110(a), which has no area figure) for minimum lot area in LB, LBR, CGB, CGBR, GB, GBO: "
                "no numeric minimum, so these are binned as 'None' in the main table and left out in the sensitivity.")
q("div21", "Note 1. See Sec. 6-110(a)")


def base_of(code):
    return code[:-3] if code.endswith("-HO") else code


def status_of(code, fam):
    key = DISTRICTS[code][0]
    return RULES[key]["s"][fam]


def pct(x, base):
    return round(x / base * 100, 1) if base else 0.0


def main():
    land = json.load(open(os.path.join(ROOT, "data", "land_area", "greenwich.json")))
    acres = {k: v["acres"] for k, v in land["districts"].items()}
    nza_all = json.load(open(os.path.join(ROOT, "data", "nza_replication", "nza_snapshots.json")))["greenwich"]
    town = json.load(open(os.path.join(ROOT, "data", "towns", "greenwich.json")))

    known = set(DISTRICTS) | set(UNCLASSIFIED_RES) | set(UNCLASSIFIED_OTHER)
    missing = sorted(set(acres) - known)
    if missing:
        raise SystemExit(f"districts with acreage but no decision: {missing}")
    for c in DISTRICTS:
        if c not in acres:
            raise SystemExit(f"{c} has no acreage")

    # quotes for the ADU / parking sections, proven against the PDF text
    adu_q = {
        "owner_occupancy": cite("Sec. 6-99(a)(3)A", "div9", "The owner of record (the “Owner”) must reside in"),
        "zones": cite("Sec. 6-99(a)(3)C", "div9", "R-20, R-12, R-7, or R-6 zone."),
        "procedure": cite("Sec. 6-99(a)(4)A", "div9", "until the Owner has received approval from the Planning and Zoning Office"),
        "r6_limit": cite("Sec. 6-99(a)(3)M", "div9", "An ADU shall be permitted in the R-6 zone only where the existing structure is a single-family dwelling."),
        "special_permit_for_oversize": cite("Sec. 6-99(a)(3)E", "div9", "Upon an application for a Special Permit, the Planning and Zoning Commission may authorize an ADU"),
    }
    park_q = {
        "single_family": cite("Sec. 6-154", "div15", "On lots used for single-family residence purposes",
                              "Requires 'sufficient garage space or outdoor parking space' but sets no number."),
        "two_multi": cite("Sec. 6-155", "div15", "On lots used for two-family and multi-family residential"),
        "table": cite("Sec. 6-155(1)(a)", "div15", "one garage space for each dwelling and one outdoor space for each dwelling"),
        "mixed_use": cite("Sec. 6-155(3)", "div15", "One space per dwelling unit unless a greater or lesser number is deemed appropriate by the Commission."),
        "adu": cite("Sec. 6-99(a)(3)F", "div9", "There must be at least one off-street parking space on an appropriate solid surface dedicated to the ADU."),
    }

    res = [c for c in DISTRICTS if RULES[DISTRICTS[c][0]]["residential"]]
    base = sum(acres[c] for c in res)
    nonres = [c for c in DISTRICTS if c not in res]
    unc_res_ac = sum(acres[c] for c in UNCLASSIFIED_RES)
    unc_oth_ac = sum(acres[c] for c in UNCLASSIFIED_OTHER)

    # ---- NZA reference values (from nza_snapshots.json)
    nza_res = nza_all["land_use_acres"]["Primarily Residential"] + nza_all["land_use_acres"]["Mixed With Residential"]
    nza_housing = nza_all["housing_acres"]
    nza_pct = {f: {s: pct(nza_housing[f][s], nza_res) for s in ("as_of_right", "hearing", "prohibited")} for f in FAMS}

    out = {
        "town": "Greenwich, CT (NZA jurisdiction 317)",
        "method": "A district is residential land if the text of Div. 9 shows at least one dwelling type allowed there. Statuses are read "
                  "from Div. 9 (use regulations); lot sizes from Div. 21 (bulk schedule); parking from Div. 15. Shares use our gross district "
                  "acreage from the town's zoning layer (before NZA's removal of protected and unzoned land). Districts whose rules are not in "
                  "the mirrored text are reported as unclassified and never guessed; their acreage appears in bounds, not in the base. "
                  "As-of-right includes administrative site plan approval (no public hearing), matching how Stamford was treated.",
        "sources": ["public/sources/greenwich-div9.pdf", "public/sources/greenwich-div21.pdf", "public/sources/greenwich-div15.pdf",
                    "data/land_area/greenwich.json", "data/nza_replication/nza_snapshots.json (greenwich)", "data/towns/greenwich.json"],
        "acreage_note": land["method"],
        "residential_districts": res,
        "nonresidential_districts": nonres,
        "residential_acres_ours": round(base, 1),
        "residential_acres_nza": nza_res,
        "unclassified_residential_districts": {c: {"acres": acres[c], "why": w} for c, w in UNCLASSIFIED_RES.items()},
        "unclassified_residential_acres": round(unc_res_ac, 1),
        "unclassified_other_districts": {c: {"acres": acres[c], "why": w} for c, w in UNCLASSIFIED_OTHER.items()},
        "unclassified_other_acres": round(unc_oth_ac, 1),
        "nonresidential_acres": round(sum(acres[c] for c in nonres), 1),
        "total_acres_in_layer": round(sum(acres.values()), 1),
        "nza_land_categories": nza_all["land_categories"],
    }

    # ---- per-district statuses
    per = {}
    for c in res:
        key, note = DISTRICTS[c]
        r = RULES[key]
        per[c] = {"acres": acres[c], "rule": r["label"], "note": note,
                  "statuses": {f: {"status": r["s"][f][0], "cite": r["s"][f][1]} for f in FAMS}}
        if c in LOT:
            per[c]["min_lot_sqft"] = {"value": LOT[c][0], "section": LOT_SEC, "quote": LOT[c][1]}
        elif c in LOT_OVERLAY_BASE(c):
            per[c]["min_lot_sqft"] = {"value": LOT[base_of(c)][0], "section": LOT_SEC + " (base district)", "quote": LOT[base_of(c)][1]}
        elif key in ("biz", "indre"):
            per[c]["min_lot_sqft"] = {"value": None, "section": "Sec. 6-205(b)", "note": BIZ_LOT_NOTE}
    for c in nonres:
        k = DISTRICTS[c][1]
        per[c] = {"acres": acres[c], "rule": RULES["nonres"]["label"], "cite": NONRES_CITE[k]}
    out["per_district"] = per

    # ---- housing shares
    out["housing"] = {}
    for f in FAMS:
        a = {s: 0.0 for s in STATUSES}
        for c in res:
            a[status_of(c, f)[0]] += acres[c]
        # bounds: unclassified residential districts all one way
        lo_prohib = a["prohibited"] / (base + unc_res_ac)               # all unclassified are not prohibited
        hi_prohib = (a["prohibited"] + unc_res_ac) / (base + unc_res_ac)  # all unclassified prohibited
        out["housing"][f] = {
            "ours_acres": {s: round(v, 1) for s, v in a.items()},
            "ours_pct": {s: pct(v, base) for s, v in a.items()},
            "nza_acres": nza_housing[f],
            "nza_pct": nza_pct[f],
            "districts": {s: [c for c in res if status_of(c, f)[0] == s] for s in STATUSES},
            "prohibited_pct_bounds_if_unclassified_residential_included": {
                "lower": round(lo_prohib * 100, 1), "upper": round(hi_prohib * 100, 1)},
        }

    # ---- minimum lot size for 1-family land (as of right or hearing)
    one = [c for c in res if status_of(c, "1-family")[0] in ("as_of_right", "hearing")]
    sized = [c for c in one if "min_lot_sqft" in per[c] and per[c]["min_lot_sqft"]["value"] is not None]
    nolot = [c for c in one if c not in sized]
    nza_ml = dict(zip(nza_all["min_lot_acres_order"], nza_all["min_lot_acres"]))
    nza_ml_tot = sum(v for k, v in nza_ml.items() if k != "Varies")

    def binned(include_none_for):
        ac = {c: acres[c] for c in sized}
        for c in include_none_for:
            ac[c] = acres[c]
        lot = {c: per[c]["min_lot_sqft"]["value"] or 0 for c in ac}
        tot = sum(ac.values())
        res_b = {}
        for name, lo, hi in LOT_BINS:
            ds = [c for c in ac if lo <= lot[c] < hi]
            res_b[name] = {"districts": ds, "acres": round(sum(ac[c] for c in ds), 1),
                           "ours_pct": pct(sum(ac[c] for c in ds), tot),
                           "nza_pct": pct(nza_ml[name], nza_ml_tot), "nza_acres": nza_ml[name]}
        return res_b, tot
    main_bins, main_tot = binned(nolot)
    alt_bins, alt_tot = binned([])
    ge80 = main_bins["80,000 sq ft or more"]["ours_pct"]
    # bound for unclassified residential (all large vs all small)
    one_ac = main_tot
    out["min_lot_size"] = {
        "basis": "1-family land = districts where 1-family is as of right or hearing (same as NZA's 1-family acres)",
        "bins": main_bins, "land_in_bins_acres": round(main_tot, 1),
        "districts_binned_as_None": nolot, "note_none": BIZ_LOT_NOTE,
        "sensitivity_excluding_business_zones": {"bins": alt_bins, "land_in_bins_acres": round(alt_tot, 1)},
        "share_80000_plus_bounds_if_unclassified_residential_included": {
            "lower_all_small": pct(main_bins["80,000 sq ft or more"]["acres"], one_ac + unc_res_ac),
            "upper_all_large": pct(main_bins["80,000 sq ft or more"]["acres"] + unc_res_ac, one_ac + unc_res_ac)},
        "nza_stored_proxy_input_pct": next(m["value"] for m in town["nza_metrics"] if "80,000" in m["label"]),
    }

    # ---- parking
    park_districts = res  # every residential-base district falls under Sec. 6-154, 6-155 or Sec. 6-110(e)
    out["parking_mandate_pct"] = {
        "ours": 100.0, "nza": next(m["value"] for m in town["nza_metrics"] if "parking" in m["label"].lower()),
        "numeric_minimum_note": "Sec. 6-154 (single-family) sets no number; numeric minimums exist only for two-/multi-family and business-zone housing (Sec. 6-155), and for ADUs (one space, Sec. 6-99(a)(3)F). If NZA counts only numeric minimums, its 92% would fit a code that leaves some 1-family land with no number; we cannot tell from the text.",
        "basis": "Every residential-base district is under Sec. 6-154 (single-family: 'sufficient' spaces), Sec. 6-155 (two-/multi-family table) or "
                 "Sec. 6-110(e) (business zones use Sec. 6-155); so a mandate exists everywhere, but for single-family land it is not a numeric minimum.",
        "cites": park_q,
    }

    # ---- ADU
    adu_ok = [c for c in res if base_of(c) in ("RA-4", "RA-2", "RA-1", "R-20", "R-12", "R-7", "R-6")]
    adu_ac = sum(acres[c] for c in adu_ok)
    rmf_ac = sum(acres[c] for c in res if base_of(c) == "R-MF")
    other_ac = base - adu_ac - rmf_ac
    nza_adu = dict(zip(nza_all["adu_acres_order"], nza_all["adu_acres"]))
    out["adu"] = {
        "ours": "Allowed by zoning permit (administrative approval from the Planning and Zoning Office) with owner-occupancy, in RA-4, RA-2, RA-1, R-20, R-12, R-7 and R-6; "
                "oversize ADUs or ADUs on nonconforming lots need a special permit.",
        "ours_acres": {"allowed_with_occupancy_restrictions": round(adu_ac, 1),
                       "not_listed_in_Sec_6-99_R-MF": round(rmf_ac, 1),
                       "not_applicable_business_zones_and_WB": round(other_ac, 1)},
        "ours_pct_of_residential_base": {"allowed_with_occupancy_restrictions": pct(adu_ac, base),
                                         "not_listed_or_not_applicable": pct(base - adu_ac, base)},
        "ours_pct_of_1family_land_with_ADU_rule": pct(adu_ac, sum(acres[c] for c in one)),
        "nza_acres": nza_adu, "nza_pct": {k: pct(v, sum(nza_adu.values())) for k, v in nza_adu.items()},
        "districts_with_adu_rule": adu_ok,
        "district_notes": {"R-6": "ADU only where the existing structure is a single-family dwelling (Sec. 6-99(a)(3)M); R-6 two-family is separately allowed.",
                           "R-MF": "R-MF is absent from the zone list in Sec. 6-99(a)(3)C, so no ADU rule applies there (not scored)."},
        "cites": adu_q,
        "adu_max_sqft_external": "800 sq ft in R-12, R-7, R-6; 1,000 in RA-1, R-20; 1,200 in RA-2, RA-4 (Sec. 6-99(a)(3)D(i), as quoted in V2 notes)",
    }

    # ---- the two proxies
    def proxy(use_excl, big, park):
        comp = (0.30 * use_excl + 0.25 * big + 0.15 * park) / 0.70
        return round(comp, 1)
    ours_ue = sum(out["housing"][f]["ours_pct"]["prohibited"] for f in FAMS[1:]) / 3
    ours_big = ge80
    ours_park = out["parking_mandate_pct"]["ours"]
    nza_ue_stored = sum(m["value"] for m in town["nza_metrics"] if "prohibited" in m["label"]) / 3
    stored = {m["label"]: m["value"] for m in town["nza_metrics"]}
    nza_ue_snap = sum(nza_pct[f]["prohibited"] for f in FAMS[1:]) / 3
    nza_big_snap = out["min_lot_size"]["bins"]["80,000 sq ft or more"]["nza_pct"]
    # bounds on our proxy for the unclassified residential districts
    lo_ue = sum(out["housing"][f]["prohibited_pct_bounds_if_unclassified_residential_included"]["lower"] for f in FAMS[1:]) / 3
    hi_ue = sum(out["housing"][f]["prohibited_pct_bounds_if_unclassified_residential_included"]["upper"] for f in FAMS[1:]) / 3
    b80 = out["min_lot_size"]["share_80000_plus_bounds_if_unclassified_residential_included"]
    out["proxy"] = {
        "formula": "composite = (0.30*use_exclusion + 0.25*share of 1-family land needing >=80,000 sq ft + 0.15*share of residential land with a parking mandate)/0.70; "
                   "use_exclusion = mean(2-family, 3-family, 4+-family prohibited %)",
        "ours": {"use_exclusion": round(ours_ue, 1), "lots_80000_plus": ours_big, "parking_mandate": ours_park,
                 "composite": proxy(ours_ue, ours_big, ours_park)},
        "nza_stored_in_town_file": {"use_exclusion": round(nza_ue_stored, 1), "lots_80000_plus": stored["1-family lots requiring ≥80,000 sq ft"],
                                    "parking_mandate": stored["Residential land with a parking mandate"], "composite": town["composite_score"],
                                    "recomputed_from_stored_inputs": proxy(nza_ue_stored, stored["1-family lots requiring ≥80,000 sq ft"],
                                                                           stored["Residential land with a parking mandate"])},
        "nza_recomputed_from_snapshot_acres": {"use_exclusion": round(nza_ue_snap, 1), "lots_80000_plus": nza_big_snap,
                                               "parking_mandate": stored["Residential land with a parking mandate"],
                                               "composite": proxy(nza_ue_snap, nza_big_snap, stored["Residential land with a parking mandate"])},
        "difference_ours_minus_nza_stored": round(proxy(ours_ue, ours_big, ours_park) - town["composite_score"], 1),
        "ours_bounds_with_unclassified_residential": {
            "lower": proxy(lo_ue, b80["lower_all_small"], ours_park), "upper": proxy(hi_ue, b80["upper_all_large"], ours_park),
            "note": "Lower: the unclassified RA-C/R-C/R-PR/R-PHD districts are all not-prohibited and all small-lot; upper: all prohibited and all >=80,000 sq ft."},
    }

    # ---- compare table (flat, for reading)
    rows = []
    for f in FAMS:
        for s in ("as_of_right", "hearing", "prohibited"):
            rows.append({"figure": f"{f} {s} (% of residential acres)", "ours": out["housing"][f]["ours_pct"][s], "nza": nza_pct[f][s]})
    for name, _, _ in LOT_BINS:
        rows.append({"figure": f"1-family min lot: {name} (%)", "ours": main_bins[name]["ours_pct"], "nza": main_bins[name]["nza_pct"]})
    rows.append({"figure": "Residential land with parking mandate (%)", "ours": 100.0, "nza": out["parking_mandate_pct"]["nza"]})
    rows.append({"figure": "Residential acres", "ours": round(base, 1), "nza": nza_res})
    rows.append({"figure": "Proxy composite", "ours": out["proxy"]["ours"]["composite"], "nza": town["composite_score"]})
    out["comparison_rows"] = rows

    out["unresolved"] = [
        "RA-C4, RA-C2, RA-C1, RA-CC4, RA-CC4-HO, R-C7, R-C12, R-C20, R-C7-HO, RC-20-HO, RC-12-HO (conservation zone families): no use or bulk text in "
        f"the mirrored Div. 9/15/21. {round(sum(acres[c] for c in UNCLASSIFIED_RES if c.startswith(('RA-C', 'R-C', 'RC-'))), 1)} acres left unclassified.",
        f"R-PR, R-PHD-SU, R-PHD-E ({round(sum(acres[c] for c in ('R-PR', 'R-PHD-SU', 'R-PHD-E')), 1)} acres): planned-residential / housing-design zones are in Div. 6, which is not mirrored.",
        f"R-6-HRO ({acres['R-6-HRO']} acres), HRO ({acres['HRO']}), LB-R-C7-HO ({acres['LB-R-C7-HO']}), BEX-50-R ({acres['BEX-50-R']}), P ({acres['P']}): overlay or district text not available.",
        "R-6 two-family: Sec. 6-98(a)(3) says administrative site plan approval; Sec. 6-101(d) says special permit for two or more dwelling units on a lot in residential zones. "
        "Read as administrative (specific over general). If the special permit reading is right, R-6 2-family moves from as-of-right to hearing "
        f"({acres['R-6']} acres, {pct(acres['R-6'], base)}% of the base).",
        "Business zones: Use Group 3 'dwelling units' are not typed as 1-, 2-, 3-family. We read up to 4 units as site-plan-only (Sec. 6-110(F)(1)) and 5+ units as special permit "
        "(Sec. 6-110(F)(2)); NZA may code business-zone housing differently, and may exclude some of these zones from residential land altogether.",
        "WB 2-family: Use Group 7c lists only 'Multi Family Dwellings'; whether that includes two-family is not defined in the mirrored text. Left unclassified.",
        "LBR-1: Sec. 6-103(G) lists Use Group 3 for all LBR zones but Sec. 6-110(c)(1) names only LBR-2.",
        "Div. 9 is the Aug. 2023 edition; Sec. 6-110 amendments effective 5/6/26 and other later amendments (see build_data.py links) are not in the mirrored PDFs. NZA's coding date for Greenwich is not stated in our files.",
        "NZA's stored proxy inputs in data/towns/greenwich.json (95.3/97.7/98.3 prohibited, 59.8 for >=80,000 sq ft) do not reproduce from the snapshot acres saved in "
        "nza_snapshots.json (96.0/97.9/98.5 and 65.0); the composite 82.7 matches the stored inputs only.",
        "Overlay codes (-HO) are separate polygons in the acreage layer, so base-district acres may be understated (acreage method note).",
    ]

    os.makedirs(os.path.join(ROOT, "data", "nza_replication"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "nza_replication", "greenwich.json"), "w") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("residential_acres_ours", "residential_acres_nza", "unclassified_residential_acres",
                                          "unclassified_other_acres", "proxy", "comparison_rows")}, indent=1, ensure_ascii=False))


def LOT_OVERLAY_BASE(c):
    """Overlay codes (-HO) inherit the base district's lot size."""
    b = base_of(c)
    return [c] if (c != b and b in LOT) else []


if __name__ == "__main__":
    main()
