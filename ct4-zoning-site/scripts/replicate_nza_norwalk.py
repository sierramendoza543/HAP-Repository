"""Recompute the National Zoning Atlas Jurisdiction Snapshot figures for Norwalk from our own
sources: the dwelling rows of Table 4.3.9.A (public/sources/norwalk-usetable.pdf), the lot
standards of Table 4.3.1 and parking Table 4.3.12.B-1 (public/sources/norwalk-art4.pdf), and our
district acreage (data/land_area/norwalk.json).

Run with: python3 -I scripts/replicate_nza_norwalk.py
Writes data/nza_replication/norwalk.json.

Two acreage cases are reported:
  confirmed    - only the five districts whose old-zone crosswalk the user confirmed
                 (CD-1L, CD-1M, CD-1S, CD-2, CD-3).
  sensitivity  - confirmed districts plus extra old-zone to CD mappings read from the city
                 nomenclature flyer (Updated_Zoning Reg Flyer_Zoning Map103123.pdf). These extra
                 mappings are NOT user-confirmed (several rest on reading a layer abbreviation as
                 the flyer's district name) and are a labeled sensitivity case only.
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USETABLE = os.path.join(ROOT, "public", "sources", "norwalk-usetable.pdf")
ART4 = os.path.join(ROOT, "public", "sources", "norwalk-art4.pdf")

# Table 4.3.9.A, first page: PDF page 3 of norwalk-usetable.pdf = printed page 250.
USE_PDF_PAGE, USE_PRINTED = 3, 250
COLUMNS = ["CD-1L", "CD-1M", "CD-1S", "CD-2", "CD-3", "CD-3W", "CD-3C", "CD-4", "CD-4W",
           "SD-H", "SD-IC", "SD-LI", "SD-HI", "SD-MC", "CV"]  # header order, checked by x position
SYMBOLS = {"P", "PL", "SPU", "NP", "NR"}
LEGEND = {"P": "Permitted by Right", "PL": "Permitted by Right with Limitations",
          "SPU": "Special Permit Use", "NP": "Not Permitted", "NR": "Not Regulated"}
# (key, label words in the row label, used for locating the row)
ROWS = {
    "single_family_detached": ["Single-Family", "Detached"],
    "two_family_detached": ["Two-Family", "Detached"],
    "townhouse": ["Townhouse"],
    "small_multifamily": ["Small", "Multifamily"],
    "large_multifamily": ["Large", "Multifamily"],
    "flex_residential": ["Flex"],
    "live_work_residential": ["Live/Work"],
    "mid_rise_residential": ["Mid-Rise"],
    "mixed_use_residential": ["Mixed"],
}


def status(sym):
    """P and PL are as of right (PL carries limitations/site plan); SPU is a hearing; NP prohibited."""
    if sym in ("P", "PL"):
        return "as_of_right"
    if sym == "SPU":
        return "hearing"
    if sym == "NP":
        return "prohibited"
    return "unclassified"  # NR or anything unreadable


RANK = {"as_of_right": 3, "hearing": 2, "prohibited": 1, "unclassified": 0}


def best(statuses):
    return max(statuses, key=lambda s: RANK[s])


def parse_use_rows():
    html = subprocess.run(["pdftotext", "-q", "-f", str(USE_PDF_PAGE), "-l", str(USE_PDF_PAGE), "-bbox",
                           USETABLE, "-"], capture_output=True, text=True, check=True).stdout
    words = [(float(x), float(y), t) for x, y, t in
             re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">([^<]*)<', html)]
    # column centres from the header words (CD-1L ... CV); CD-3W/CD-4W/SD-MC sit in a raised row
    hdr = {}
    for x, y, t in words:
        if t in COLUMNS and y < 160:
            hdr[t] = x
    if set(hdr) != set(COLUMNS):
        raise SystemExit(f"header columns not all found: {sorted(set(COLUMNS) - set(hdr))}")
    labels = [(x, y, t) for x, y, t in words if x < 150 and 170 < y]
    # find the table's legend line so label words below it are ignored
    stop = min((y for x, y, t in words if t == "LEGEND"), default=1e9)
    labels = [w for w in labels if w[1] < stop]
    syms = [(x, y, t) for x, y, t in words if x > 150 and y > 170 and y < stop and t in SYMBOLS]
    # label lines -> rows. A row = the lines between successive row starts; locate each wanted row
    # by its first label word at x ~ 51, then take label lines until the next x~51 word that is a
    # row start. Row starts are words at x<53 whose previous label line is >=15pt away or that are
    # the known first words.
    starts = sorted({round(y, 1) for x, y, t in labels if x < 53})
    line_y = starts
    result = {}
    for key, ws in ROWS.items():
        cand = [y for x, y, t in labels if t == ws[0] and x < 53]
        if not cand:
            raise SystemExit(f"row label not found: {ws}")
        y0 = cand[0]
        # all words of this row label: same-y words, plus the next lines up to 2 more lines
        row_words = [(x, y, t) for x, y, t in labels if abs(y - y0) < 1.0]
        text0 = " ".join(t for x, y, t in sorted(row_words))
        if not all(w in text0 for w in ws[1:2]) and len(ws) > 1:
            pass
        result[key] = y0
    # symbol assignment: each symbol goes to the nearest row label first-line within the row pitch,
    # using the continuation line(s) as part of the same row (rows are ~23 pt apart, a label is up to
    # ~35 pt tall, so we assign by the nearest row start at or above y - 14, never above y + 6).
    all_starts = sorted({y for x, y, t in labels if x < 53 and t[0].isupper() and t not in ("RESIDENTIAL",)})
    # continuation words ("Building", "Dwelling", "Type") also start at x ~ 51; drop any start within
    # 16 pt below a previous start (they are label continuations)
    row_starts = []
    for y in all_starts:
        if not row_starts or y - row_starts[-1] > 16:
            row_starts.append(y)
    out = {}
    for key, y0 in result.items():
        i = min(range(len(row_starts)), key=lambda k: abs(row_starts[k] - y0))
        lo = row_starts[i] - 6
        hi = row_starts[i + 1] - 6 if i + 1 < len(row_starts) else lo + 40
        mine = [(x, t) for x, y, t in syms if lo <= y < hi]
        cols = {}
        for x, t in mine:
            c = min(COLUMNS, key=lambda c: abs(hdr[c] - x))
            if abs(hdr[c] - x) > 14:
                raise SystemExit(f"{key}: symbol {t} at x={x} not aligned with a column")
            if c in cols:
                raise SystemExit(f"{key}: two symbols in column {c}")
            cols[c] = t
        if len(cols) != len(COLUMNS):
            raise SystemExit(f"{key}: expected {len(COLUMNS)} symbols, found {len(cols)} ({sorted(cols)})")
        out[key] = cols
    return out


def main():
    land = json.load(open(os.path.join(ROOT, "data", "land_area", "norwalk.json")))
    raw = {k: v["acres"] for k, v in land["districts"].items()}
    confirmed = {d: v["acres"] for d, v in land["districts_current_code"].items()}

    # Sensitivity crosswalk: flyer table "Proposed Zone Name / Existing Zone Name" (pdf p.1-2).
    SENS = {  # layer code -> (CD, flyer wording, confidence note)
        "B1": ("CD-3C", "Business No. 1", "layer code B1 read as Business No. 1"),
        "B2": ("CD-3C", "Business No. 2", "layer code B2 read as Business No. 2"),
        "EVD": ("CD-3", "East Avenue Village District", "abbreviation read from name"),
        "GHVD": ("CD-3", "Golden Hill Village District", "abbreviation read from name"),
        "RVD": ("CD-3W", "Rowayton Avenue Village District", "abbreviation read from name; flyer name is Rowayton Avenue"),
        "SSDD": ("CD-4", "Sono Station Design District", "abbreviation read from name"),
        "RD": ("CD-4", "Reed-Putnam Design District", "layer code RD read as Reed-Putnam Design"),
        "CBD": ("CD-4", "Central Business District", "exact name"),
        "SNBD": ("CD-4", "South Norwalk Business District", "abbreviation read from name"),
        "EO": ("CD-4", "Executive Office", "abbreviation read from name"),
        "WSDD": ("CD-4", "Washington Street Design District", "abbreviation read from name"),
        "CBD W": ("CD-4W", "Central Business District-Water", "layer code CBD W read as CBD-Water"),
    }
    sens_acres = dict(confirmed)
    sens_sources = {}
    for code, (cd, wording, note) in SENS.items():
        sens_acres[cd] = round(sens_acres.get(cd, 0.0) + raw[code], 1)
        sens_sources.setdefault(cd, []).append({"layer_code": code, "acres": raw[code], "flyer_name": wording, "note": note})
    mapped_codes = set(land["crosswalk_applied"]) | set(SENS)
    unmapped = {k: v for k, v in raw.items() if k not in mapped_codes}

    rows = parse_use_rows()
    sym = lambda key, d: rows[key][d]
    # Mapping rule (Table 4.3.8.B): Small Multifamily Building = 3 to 6 dwelling units (PDF p.191, printed 238);
    # Large Multifamily Building = 7 or more units (PDF p.192, printed 239). Townhouse = 1 unit per building
    # (attached single-family units), so it is NOT counted as 3-family or 4+-family.
    #   3-family  = Small Multifamily Building status
    #   4+-family = most permissive of Small Multifamily (4-6 units) and Large Multifamily (7+) status
    fam = {"1-family": lambda d: status(sym("single_family_detached", d)),
           "2-family": lambda d: status(sym("two_family_detached", d)),
           "3-family": lambda d: status(sym("small_multifamily", d)),
           "4+-family": lambda d: best([status(sym("small_multifamily", d)), status(sym("large_multifamily", d))])}
    other_multi = ["flex_residential", "live_work_residential", "mid_rise_residential", "mixed_use_residential"]
    alt4 = lambda d: best([fam["4+-family"](d)] + [status(sym(k, d)) for k in other_multi])
    allowed_any = lambda d: any(status(sym(k, d)) in ("as_of_right", "hearing") for k in ROWS)

    # page cites
    cite_use = f"Table 4.3.9.A, printed p.{USE_PRINTED} (PDF p.{USE_PDF_PAGE} of public/sources/norwalk-usetable.pdf)"
    LOT_PAGE = {"CD-1L": (4, 51, "43,560 sq. ft.", 43560), "CD-1M": (15, 62, "12,500 sq. ft.", 12500),
                "CD-1S": (23, 70, "6,250 sq. ft.", 6250), "CD-2": (31, 78, "5,000 sq. ft.", 5000),
                "CD-3": (41, 88, "NR", 0), "CD-3W": (64, 111, "NR", 0), "CD-3C": (78, 125, "NR", 0),
                "CD-4": (89, 136, "NR", 0), "CD-4W": (104, 151, "NR", 0)}
    # verify the quoted lot-area values against the PDF text
    for d, (pg, printed, quoted, _) in LOT_PAGE.items():
        txt = subprocess.run(["pdftotext", "-q", "-f", str(pg), "-l", str(pg), "-layout", ART4, "-"],
                             capture_output=True, text=True, check=True).stdout
        m = re.search(r"Lot/Building Site Area\s+(.+)", txt)
        assert d in txt and m and m.group(1).strip().startswith(quoted.split()[0]), (d, m and m.group(1))
    LOT_BINS = [("None", 0, 1), ("Less than 10,000 sq ft", 1, 10000), ("10,000 to 19,999 sq ft", 10000, 20000),
                ("20,000 to 39,999 sq ft", 20000, 40000), ("40,000 to 79,999 sq ft", 40000, 80000),
                ("80,000 sq ft or more", 80000, 10 ** 9)]

    nza_snap = json.load(open(os.path.join(ROOT, "data", "nza_replication", "nza_snapshots.json")))["norwalk"]
    nza_res = nza_snap["land_use_acres"]["Primarily Residential"] + nza_snap["land_use_acres"]["Mixed With Residential"]
    nza_housing = nza_snap["housing_acres"]
    nza_pct = {f: {s: round(nza_housing[f][s] / nza_res * 100, 1) for s in ("as_of_right", "hearing", "prohibited")}
               for f in fam}
    nza_bins_ac = dict(zip(nza_snap["min_lot_acres_order"], nza_snap["min_lot_acres"]))
    nza_1f = sum(nza_bins_ac.values())
    nza_big = nza_bins_ac["80,000 sq. ft. or more".replace("sq. ft.", "sq ft")] / nza_1f * 100
    nza_towns = json.load(open(os.path.join(ROOT, "data", "towns", "norwalk.json")))
    nza_in = {m["label"]: m["value"] for m in nza_towns["nza_metrics"]}
    nza_ue = (nza_in["2-family housing prohibited"] + nza_in["3-family housing prohibited"] +
              nza_in["4+-family housing prohibited"]) / 3
    nza_big_stored = nza_in["1-family lots requiring ≥80,000 sq ft"]
    nza_park = nza_in["Residential land with a parking mandate"]
    composite = lambda ue, big, park: (0.30 * ue + 0.25 * big + 0.15 * park) / 0.70
    nza_comp = composite(nza_ue, nza_big_stored, nza_park)

    def run_case(acres, label, basis):
        res = [d for d in COLUMNS if d in acres and allowed_any(d)]
        base = sum(acres[d] for d in res)
        out = {"label": label, "basis": basis, "residential_districts": res,
               "residential_acres_ours": round(base, 1), "residential_acres_nza": nza_res,
               "housing": {}}
        for f, fn in fam.items():
            tot = {"as_of_right": 0.0, "hearing": 0.0, "prohibited": 0.0, "unclassified": 0.0}
            for d in res:
                tot[fn(d)] += acres[d]
            out["housing"][f] = {
                "ours_acres": {k: round(v, 1) for k, v in tot.items()},
                "ours_pct": {k: round(v / base * 100, 1) for k, v in tot.items() if k != "unclassified" or v},
                "nza_acres": nza_housing[f], "nza_pct": nza_pct[f],
                "districts_as_of_right": [d for d in res if fn(d) == "as_of_right"],
                "districts_hearing": [d for d in res if fn(d) == "hearing"],
                "districts_prohibited": [d for d in res if fn(d) == "prohibited"]}
        # 4+-family sensitivity to counting the residential portion of flex/live-work/mid-rise/mixed-use types
        out["four_plus_if_all_multi_unit_building_types_counted_pct_prohibited"] = round(
            sum(acres[d] for d in res if alt4(d) == "prohibited") / base * 100, 1)
        one = [d for d in res if fam["1-family"](d) == "as_of_right"]
        one_ac = sum(acres[d] for d in one)
        bins = {}
        for name, lo, hi in LOT_BINS:
            ds = [d for d in one if lo <= LOT_PAGE[d][3] < hi]
            bins[name] = {"districts": ds, "acres": round(sum(acres[d] for d in ds), 1),
                          "ours_pct": round(sum(acres[d] for d in ds) / one_ac * 100, 1),
                          "nza_acres": nza_bins_ac.get(name),
                          "nza_pct": round(nza_bins_ac.get(name, 0) / nza_1f * 100, 1)}
        out["min_lot_size"] = {"one_family_land_acres": round(one_ac, 1), "bins": bins,
                               "lot_area_by_district": {d: {"quoted": LOT_PAGE[d][2], "sq_ft_used": LOT_PAGE[d][3],
                                                            "cite": f"Table 4.3.1, PDF p.{LOT_PAGE[d][0]} (printed p.{LOT_PAGE[d][1]}) of norwalk-art4.pdf"}
                                                        for d in one},
                               "note": "NR (not regulated) is binned as 'None'. 'Varies' bin is empty for us."}
        big = bins["80,000 sq ft or more"]["ours_pct"]
        ue = sum(out["housing"][f]["ours_pct"]["prohibited"] for f in ("2-family", "3-family", "4+-family")) / 3
        out["parking_mandate_pct"] = {"ours": 100.0, "nza": nza_park,
            "basis": "Table 4.3.12.B-1 (PDF p.263 of norwalk-art4.pdf, printed p.310) sets a per-dwelling-unit minimum for every dwelling type "
                     "(2 per unit single/two-family, 1.3 in CD-3/3W/3C/4/4W; 1.3 multifamily; 1 townhouse). Transit-area reductions "
                     "(Table 4.3.12.B-4) were not applied."}
        out["proxy"] = {"use_exclusion": round(ue, 2), "share_1f_land_ge_80000": big, "share_residential_with_parking_mandate": 100.0,
                        "ours": round(composite(ue, big, 100.0), 1), "nza": round(nza_comp, 1),
                        "difference_ours_minus_nza": round(composite(ue, big, 100.0) - nza_comp, 1)}
        return out

    cases = {
        "confirmed": run_case(confirmed, "Confirmed-acreage districts only (CD-1L, CD-1M, CD-1S, CD-2, CD-3)",
                              "land_area/norwalk.json districts_current_code (user-confirmed crosswalk)"),
        "sensitivity": run_case(sens_acres, "SENSITIVITY: confirmed plus flyer-based mappings (NOT user-confirmed)",
                                "adds old-zone codes mapped from the city flyer; see sensitivity_mappings"),
    }

    # per-district statuses
    per = {}
    for d in COLUMNS:
        per[d] = {"symbols": {k: rows[k][d] for k in ROWS},
                  "status": {f: fn(d) for f, fn in fam.items()},
                  "acres_confirmed": confirmed.get(d), "acres_sensitivity": sens_acres.get(d),
                  "allows_any_dwelling": allowed_any(d)}

    out = {
        "method": "Residential land = districts whose column allows at least one dwelling type (P, PL or SPU in any dwelling row of Table 4.3.9.A). "
                  "Shares use our gross district acreage (ArcGIS layer, pre-rewrite map) with no protected/unzoned/water deductions. "
                  "Status: P and PL = as_of_right (PL is permitted by right with limitations, e.g. site plan), SPU = hearing, NP = prohibited. "
                  "Mapping rule for family types (Table 4.3.8.B defines Small Multifamily Building as 3 to 6 units and Large Multifamily Building as 7+ units): "
                  "3-family = Small Multifamily Building status; 4+-family = the more permissive of Small Multifamily (4-6 units) and Large Multifamily (7+); "
                  "Townhouse (1 unit per building) is not mapped to 3 or 4+-family. 1-family = Single-Family Detached Dwelling; 2-family = Two-Family Detached Dwelling.",
        "legend": LEGEND,
        "source": {"use_table": cite_use + "; columns checked by x-position against the header; header order: " + ", ".join(COLUMNS),
                   "building_types": "Table 4.3.8.B: Small Multifamily PDF p.191 (printed 238) 'Units per Building 3 min., 6 max.'; Large Multifamily PDF p.192 (printed 239) 'Units per Building 7 min.' of norwalk-art4.pdf",
                   "lot_standards": "Table 4.3.1-A to 4.3.1-I, norwalk-art4.pdf (pages in min_lot_size)",
                   "parking": "Table 4.3.12.B-1, norwalk-art4.pdf PDF p.263 (printed 310)",
                   "adu": "Table 4.3.9.D row 'Accessory Dwelling Unit', printed p.260 (PDF p.13) and Sec. 4.3.9.G.4.a, printed pp.264-265 (PDF pp.17-18) of norwalk-usetable.pdf",
                   "acreage": "data/land_area/norwalk.json"},
        "per_district": per,
        "cases": cases,
        "sensitivity_mappings": {"source": "Updated_Zoning Reg Flyer_Zoning Map103123.pdf, table 'Proposed Zone Name / Existing Zone Name' (Oct 31, 2023)",
                                 "added": sens_sources, "acres_by_cd": sens_acres,
                                 "caveat": "Not user-confirmed. Flyer names were matched to ArcGIS layer abbreviations by reading the abbreviation; the layer is the pre-rewrite map."},
        "adu": {"ours": "Accessory Dwelling Unit is PL (permitted by right with limitations) in CD-1L, CD-1M, CD-1S, CD-2, CD-3, CD-3W, CD-3C, CD-4, CD-4W (Table 4.3.9.D); "
                        "limitations include owner residing on the lot, 6-month minimum rental, one ADU per lot, Zoning Permit (Sec. 4.3.9.G.4.a). "
                        "NZA category equivalent: Allowed with occupancy restrictions on 100% of 1-family land.",
                "nza": {"Allowed with occupancy restrictions": nza_snap["adu_acres"][1], "Prohibited": nza_snap["adu_acres"][4]}},
        "nza": {"residential_acres": nza_res, "housing_acres": nza_housing, "min_lot_acres": nza_bins_ac,
                "one_family_land_acres": nza_1f,
                "proxy_inputs": {"use_exclusion": round(nza_ue, 2), "share_1f_land_ge_80000": nza_big_stored, "parking": nza_park},
                "composite": round(nza_comp, 1), "stored_composite_score": nza_towns["composite_score"]},
        "unresolved": [
            "Old-zone layer codes with no confirmed or flyer-based CD mapping (excluded from both cases): " +
            ", ".join(f"{k} {v} ac" for k, v in unmapped.items() if k != "WATER") + "; WATER (" + str(raw["WATER"]) + " ac) is water.",
            "NB is confirmed as CD-3 only; the flyer says some neighborhood business land is CD-3W (Rowayton), which the layer cannot separate.",
            "SD-IC permits single-family detached (P) but no layer code is mapped to any SD district, so SD acreage is zero in both cases.",
            "The ArcGIS layer predates the 2024 rewrite; district boundaries and acreage may be stale.",
            "Large Multifamily in CD-3 needs a Special Permit above 29 units (Sec. 4.3.9.G.4.bb); counted as as_of_right because the table symbol is PL.",
            "Table 4.3.9.A notes: footnote * and ** (Silvermine Tavern Village District Overlay) alter CD-1L single-family; overlay acreage not separable.",
        ],
    }
    os.makedirs(os.path.join(ROOT, "data", "nza_replication"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "nza_replication", "norwalk.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps({"per_district_symbols": {d: per[d]["symbols"] for d in COLUMNS[:9]},
                      "cases": {k: {"res_ac": v["residential_acres_ours"], "proxy": v["proxy"],
                                    "housing": {f: v["housing"][f]["ours_pct"] for f in v["housing"]},
                                    "bins": {b: v["min_lot_size"]["bins"][b]["ours_pct"] for b in v["min_lot_size"]["bins"]}}
                                for k, v in cases.items()},
                      "nza": out["nza"]["proxy_inputs"], "nza_comp": out["nza"]["composite"]}, indent=1))


if __name__ == "__main__":
    main()
