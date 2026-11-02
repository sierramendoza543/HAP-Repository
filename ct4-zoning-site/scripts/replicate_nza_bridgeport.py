"""Recompute the National Zoning Atlas Jurisdiction Snapshot figures for Bridgeport from our own
sources: Table 2-2 of the mirrored "Zone Bridgeport" form-based code (which building types each
zone allows), the "Number of Principal Units" row of each building type's page, and our district
acreage (data/land_area/bridgeport.json).

Run with: python3 -I scripts/replicate_nza_bridgeport.py
Writes data/nza_replication/bridgeport.json.

Nothing here is guessed: Table 2-2 is parsed from the PDF at run time, and every unit-count rule
below carries a verbatim quote that the script re-finds in the PDF (it stops if one is missing).
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "public", "sources", "bridgeport-zoning.pdf")
SECTION_NAME_RE = re.compile(r"\s+")

# ---- NZA Jurisdiction Snapshot (jurisdiction 311) and stored proxy inputs -------------------------
NZA_SNAP = json.load(open(os.path.join(ROOT, "data", "nza_replication", "nza_snapshots.json")))["bridgeport"]
NZA_TOWN = json.load(open(os.path.join(ROOT, "data", "towns", "bridgeport.json")))
LAND = json.load(open(os.path.join(ROOT, "data", "land_area", "bridgeport.json")))["districts"]
ACRES = {d: v["acres"] for d, v in LAND.items()}

LOT_BINS = [("None", 0, 1), ("Less than 10,000 sq ft", 1, 10000), ("10,000 to 19,999 sq ft", 10000, 20000),
            ("20,000 to 39,999 sq ft", 20000, 40000), ("40,000 to 79,999 sq ft", 40000, 80000),
            ("80,000 sq ft or more", 80000, 10 ** 9)]

# ---- Unit-count rules: building type -> zone -> (min units, max units or None, special-permit max) -
# "No limits" -> 1+ ; "N max." -> 1..N ; "3 min." / "3 minimum" -> 3+ ; "1 in House" -> exactly 1.
# Each entry: (quote that must appear in the page text after whitespace collapse, section heading
# that must be on the same page, section/column note).
UNIT_RULES = {
    "Storefront Building": {
        "section": "3.20 Storefront Building Type", "cite": "Sec. 3.20.9 Storefront, Number of Principal Units",
        "quote": "Number of Principal Units No limits No limits No limits 8 max.",
        "zones": {"DX1": (1, None, None), "MX1": (1, None, None), "MX2": (1, None, None), "MXN": (1, 8, None)}},
    "Commercial Center": {
        "section": "3.30 Commercial Center Building Type", "cite": "Sec. 3.30.9 Commercial Center, Number of Principal Units",
        "quote": "Number of Principal Units No limits",
        "zones": {"MX2": (1, None, None)}},
    "Commercial House": {
        "section": "3.40 Commercial House Building Type", "cite": "Sec. 3.40.9 Commercial House, Number of Principal Units",
        "quote": "Number of Principal Units No limits No limits 6 max. 6 max. No limits",
        "zones": {"MX1": (1, None, None), "MX2": (1, None, None), "MXN": (1, 6, None), "RX1": (1, 6, None),
                  "RX2": (1, None, None)}},
    "General Building": {
        "section": "3.50 General Building Type", "cite": "Sec. 3.50.9 General Building, Number of Principal Units",
        "quote": "Number of Principal Units 3 min. 3 min. – – – 3 min.",
        "zones": {"DX2": (3, None, None), "RX2": (3, None, None), "NX3": (3, None, None), "NX4": (3, None, None)}},
    "Small General Building": {
        "section": "3.60 Small General Building Type", "cite": "Sec. 3.60.9 Small General Building, Number of Principal Units",
        "quote": "Number of Principal Units 3 min., 6 max., 3 min. up to 8 units with special permit",
        "zones": {"NX2": (3, 6, 8), "RX1": (3, None, None)}},
    "Row Building": {
        "section": "3.70 Row Building Type", "cite": "Sec. 3.70.9 Row, Number of Principal Units",
        "quote": "Number of Principal Units 3 minimum 3 minimum 3 minimum",
        "zones": {z: (3, None, None) for z in ("NX1", "NX2", "NX3", "NX4", "RX1", "RX2")}},
    "Double House A": {
        "section": "3.80 Double House A Building Type", "cite": "Sec. 3.80.9 Double House A, Number of Principal Units; minimum 2 from Sec. 3.80.1 ('essentially two House A types ... housing multiple units')",
        "quote": "up to 4, 6 with special permit in House; up to 6, 8 with special permit in House;",
        "zones": {"NX1": (2, 4, 6), "NX2": (2, 6, 8)}},
    "House A": {
        "section": "3.90 House A Building Type", "cite": "Sec. 3.90.9 House A, Number of Principal Units",
        "quote": "Number of Principal Units 1 in House up to 3 in House plus 1",
        "zones": {"N1": (1, 1, None), "NX1": (1, 3, None), "NX2": (1, 4, None)}},
    "House B": {
        "section": "3.100 House B Building Type", "cite": "Sec. 3.100.9 House B, Number of Principal Units",
        "quote": "Number of Principal Units 1 in House, 2 with special permit",
        "zones": {"N2": (1, 1, 2)}},
    "House C": {
        "section": "3.110 House C Building Type", "cite": "Sec. 3.110.9 House C, Number of Principal Units",
        "quote": "Number of Principal Units 1 in House",
        "zones": {"N3": (1, 1, None)}},
    "House D": {
        "section": "3.120 House D Building Type", "cite": "Sec. 3.120.9 House D, Number of Principal Units",
        "quote": "Number of Principal Units 1 in House",
        "zones": {"N4": (1, 1, None)}},
}
MIXED_USE_TYPES = ("Storefront Building", "Commercial Center", "Commercial House")

# Other quotes that must be present (page-checked): parking, lot size, accessory apartments.
OTHER_QUOTES = {
    "parking": ("8.20 Motor Vehicle Parking", "Sec. 8.20.1 Minimum Ratios",
                "This zoning code does not establish minimum off-street parking requirements"),
    "lot_house_b": ("3.100 House B Building Type", "Sec. 3.100.4 House B, Lot Size", "Lot Size No min."),
    "lot_house_c": ("3.110 House C Building Type", "Sec. 3.110.4 House C, Lot Size", "Lot Size 9000 sq. ft. min."),
    "lot_house_d": ("3.120 House D Building Type", "Sec. 3.120.4 House D, Lot Size", "Lot Size 7500 sq. ft. min."),
    "adu_n1": ("3.90 House A Building Type", "Sec. 3.90.9 House A, ACCESSORY USES table (N1 / NX1 / NX2 columns)",
               "Accessory Apartments 4 – –"),
    "adu_n2": ("3.100 House B Building Type", "Sec. 3.100.9 House B, Number of Accessory Apartments",
               "Number of Accessory Apartments 1 in Backyard Cottage with special permit"),
    "adu_n3": ("3.110 House C Building Type", "Sec. 3.110.9 House C, Number of Accessory Apartments",
               "Number of Accessory Apartments up to 2; 1 in House and/or 1 in Backyard Cottage"),
    "adu_n4": ("3.120 House D Building Type", "Sec. 3.120.9 House D, Number of Accessory Apartments",
               "Number of Accessory Apartments 1 in House or Backyard Cottage"),
    "key": ("3.20 Storefront Building Type", "Sec. 3.20.9 use-table key",
            "KEY: 4 = Allowed Use 8 = Allowed in Upper Stories Only"),
}

_pages = None


def pages():
    global _pages
    if _pages is None:
        text = subprocess.run(["pdftotext", "-q", "-layout", PDF, "-"], capture_output=True, text=True,
                              check=True).stdout
        text = text.replace("‐", "-").replace("‑", "-")
        _pages = text.split("\f")
    return _pages


_raw = None


def raw_pages():
    """Reading-order text (no -layout), used for prose such as Sec. 8.20.1 that shares a line with a second column."""
    global _raw
    if _raw is None:
        text = subprocess.run(["pdftotext", "-q", PDF, "-"], capture_output=True, text=True, check=True).stdout
        _raw = text.replace("‐", "-").replace("‑", "-").split("\f")
    return _raw


def collapse(s):
    return SECTION_NAME_RE.sub(" ", s).strip()


def printed_page(pg_text):
    found = re.findall(r"(?:CITY OF BRIDGEPORT CT\s+(\d+-\d+)|(\d+-\d+)\s+CITY OF BRIDGEPORT CT)", pg_text)
    for a, b in reversed(found):
        return a or b
    return None


def locate(heading, quote):
    """First PDF page whose text has both the section heading and the quote (whitespace collapsed)."""
    q, h = collapse(quote), collapse(heading)
    for source in (pages(), raw_pages()):
        for i, pg in enumerate(source, start=1):
            c = collapse(pg)
            if h in c and q in c:
                return {"pdf_page": i, "printed_page": printed_page(pages()[i - 1])}
    raise SystemExit(f"quote not found in PDF under '{heading}': {quote}")


def table_2_2():
    """Parse both halves of Table 2-2 into {zone: {building type: allowed?}}; check mark extracts as '4'."""
    out, pdf_pages = {}, set()
    for i, pg in enumerate(pages(), start=1):
        lines = pg.splitlines()
        for n, ln in enumerate(lines):
            if not re.match(r"\s*Table 2-2", ln):
                continue
            block = lines[n:n + 40]
            # header zones sit on the line that contains the zone codes
            zone_line = next(b for b in block if re.search(r"\b(DX1\s+DX2|NX4\s+NX3)\b", b)
                             or ("Site and Building Types" in b and re.search(r"\bNX4\b", b)))
            zones = [z for z in zone_line.replace("Site and Building Types", "").replace("Reference", "").split()]
            for b in block:
                m = re.match(r"\s*(Storefront Building|Commercial Center|Commercial House|General Building|"
                             r"Small General Building|Row Building|Double House A|House [A-D]|Workshop|Civic Building|"
                             r"Patio Outdoor Site|Outdoor Patio Site|Open Outdoor Site)\s{2,}(.*)$", b)
                if not m:
                    continue
                name, rest = m.group(1).strip(), m.group(2).replace("0 DP", "D")
                toks = rest.split()
                toks = toks[:-1]  # drop the Reference column
                if len(toks) != len(zones):
                    raise SystemExit(f"Table 2-2 row '{name}': {len(toks)} symbols for {len(zones)} zones")
                for z, t in zip(zones, toks):
                    out.setdefault(z, {})[name] = t
                pdf_pages.add(i)
    return out, sorted(pdf_pages)


def rank(s):
    return {"prohibited": 0, "hearing": 1, "as_of_right": 2}[s]


def family_status(zone, k, t22, mixed_use_3plus_only=False):
    """Best status of a k-unit principal building (k=4 means 4 or more) in the zone, from the building
    types Table 2-2 allows there and each type's unit-count rule. Returns (status, [reasons])."""
    best, why = "prohibited", []
    for bt, rule in UNIT_RULES.items():
        if zone not in rule["zones"] or t22.get(zone, {}).get(bt) != "4":
            continue
        lo, hi, sp = rule["zones"][zone]
        if mixed_use_3plus_only and bt in MIXED_USE_TYPES:
            lo = max(lo, 3)

        def fits(top):
            return lo <= k and (top is None or (top >= 4 if k == 4 else top >= k))
        if fits(hi):
            st = "as_of_right"
        elif sp is not None and fits(sp):
            st = "hearing"
        else:
            continue
        why.append(f"{bt} ({st})")
        if rank(st) > rank(best):
            best = st
    return best, why


def adu_status(zone):
    """Accessory-apartment status from the 'Accessory Apartments' row / 'Number of Accessory Apartments'
    row of the House A-D pages. Zones whose House page shows a dash (NX1, NX2) or that have no House
    type are 'prohibited'; the backyard-cottage unit in NX1/NX2 is counted as a principal unit, not as
    an accessory apartment."""
    return {"N1": "as_of_right", "N3": "as_of_right", "N4": "as_of_right", "N2": "hearing"}.get(zone, "prohibited")


def lot_sqft(zone):
    return {"N3": 9000, "N4": 7500}.get(zone, 0)  # all other 1-family zones: no lot-area minimum row


def compute(t22, residential, mixed_use_3plus_only=False):
    base = sum(ACRES[d] for d in residential)
    res = {"residential_acres": round(base, 1), "family": {}}
    for label, k in (("1-family", 1), ("2-family", 2), ("3-family", 3), ("4+-family", 4)):
        acc = {"as_of_right": 0.0, "hearing": 0.0, "prohibited": 0.0}
        for d in residential:
            acc[family_status(d, k, t22, mixed_use_3plus_only)[0]] += ACRES[d]
        res["family"][label] = {s: round(a, 1) for s, a in acc.items()}
        res["family"][label]["pct"] = {s: round(a / base * 100, 1) for s, a in acc.items()}
    one = [d for d in residential if family_status(d, 1, t22, mixed_use_3plus_only)[0] != "prohibited"]
    one_ac = sum(ACRES[d] for d in one)
    bins = {}
    for name, lo, hi in LOT_BINS:
        ds = [d for d in one if lo <= lot_sqft(d) < hi]
        a = sum(ACRES[d] for d in ds)
        bins[name] = {"districts": ds, "acres": round(a, 1), "pct": round(a / one_ac * 100, 1) if one_ac else 0.0}
    res["one_family_land_acres"] = round(one_ac, 1)
    res["min_lot_bins"] = bins
    adu = {"as_of_right": 0.0, "hearing": 0.0, "prohibited": 0.0}
    for d in one:
        adu[adu_status(d)] += ACRES[d]
    res["adu_acres_on_one_family_land"] = {k: round(v, 1) for k, v in adu.items()}
    ue = sum(res["family"][f]["pct"]["prohibited"] for f in ("2-family", "3-family", "4+-family")) / 3
    ge80 = bins["80,000 sq ft or more"]["pct"]
    res["proxy"] = proxy(ue, ge80, 0.0)
    return res


def proxy(use_excl, ge80, parking):
    comp = (0.30 * use_excl + 0.25 * ge80 + 0.15 * parking) / 0.70
    return {"use_exclusion": round(use_excl, 1), "share_1fam_ge_80000": round(ge80, 1),
            "share_parking_mandate": round(parking, 1), "composite": round(comp, 1)}


def main():
    t22, t22_pages = table_2_2()
    zones_in_table = sorted({z for z in t22})
    # --- classify every district in the acreage file ---
    per, residential, nonres, unclassified = {}, [], [], []
    for d in ACRES:
        if d in ("PDD", "(blank)"):
            reason = ("PDD is a legacy Planned Development District governed by each parcel's recorded general "
                      "development plan, which is not in the mirrored code (Sec. 2.60.1 A(1))" if d == "PDD" else
                      "parcels with no ZONE_2021 value in the city layer")
            unclassified.append({"district": d, "acres": ACRES[d], "reason": reason})
            per[d] = {"acres": ACRES[d], "class": "unclassified", "reason": reason}
            continue
        types = sorted(bt for bt, sym in t22.get(d, {}).items() if sym in ("4", "D", "0"))
        dwelling = [bt for bt in types if bt in UNIT_RULES and d in UNIT_RULES[bt]["zones"]]
        if dwelling:
            residential.append(d)
        else:
            nonres.append(d)
        per[d] = {"acres": ACRES[d], "class": "residential" if dwelling else "no dwelling type",
                  "table_2_2_building_types": types, "dwelling_building_types": dwelling}
    for d in residential:
        per[d]["status"] = {}
        for label, k in (("1-family", 1), ("2-family", 2), ("3-family", 3), ("4+-family", 4)):
            st, why = family_status(d, k, t22)
            per[d]["status"][label] = {"status": st, "via": why}
        per[d]["adu"] = adu_status(d)
        per[d]["min_lot_sqft"] = lot_sqft(d)
        per[d]["parking_minimum"] = "none (Sec. 8.20.1)"
    for d in nonres:
        per[d]["reason"] = ("Table 2-2 allows no building type with a Number of Principal Units; "
                            "Civic/Workshop/Open-site/General pages show '–' for units in this zone")

    # --- verify and cite quotes ---
    cites = {}
    for bt, rule in UNIT_RULES.items():
        cites[bt] = {"cite": rule["cite"], "quote": rule["quote"], **locate(rule["section"], rule["quote"]),
                     "zones": {z: {"min": v[0], "max": v[1], "special_permit_max": v[2]} for z, v in rule["zones"].items()}}
    other = {}
    for key, (head, cite, quote) in OTHER_QUOTES.items():
        other[key] = {"cite": cite, "quote": quote, **locate(head, quote)}
    # Table 2-2 and the Storefront/Commercial House '8' (upper stories only) entries
    cites["Table 2-2"] = {"pdf_pages": t22_pages, "note": "parsed live; check mark extracts as '4', dash as '–', '0 DP' = development plan"}

    base_ours = compute(t22, residential)
    sens = compute(t22, residential, mixed_use_3plus_only=True)

    # --- NZA side ---
    h = NZA_SNAP["housing_acres"]
    nza_res = sum(NZA_SNAP["land_use_acres"][k] for k in ("Mixed With Residential", "Primarily Residential"))
    nza = {"residential_acres": nza_res, "family": {}}
    for f in ("1-family", "2-family", "3-family", "4+-family"):
        tot = sum(h[f].values())
        nza["family"][f] = {**h[f], "pct": {k: round(v / nza_res * 100, 1) for k, v in h[f].items()}, "sum_acres": tot}
    lots = dict(zip(NZA_SNAP["min_lot_acres_order"], NZA_SNAP["min_lot_acres"]))
    lt = sum(v for k, v in lots.items() if k != "Varies")
    nza["min_lot_bins"] = {k: {"acres": lots[k], "pct": round(lots[k] / lt * 100, 1)} for k in lots if k != "Varies"}
    adu = dict(zip(NZA_SNAP["adu_acres_order"], NZA_SNAP["adu_acres"]))
    nza["adu_acres"] = adu
    nza_ue = sum(nza["family"][f]["pct"]["prohibited"] for f in ("2-family", "3-family", "4+-family")) / 3
    nza_ge80 = nza["min_lot_bins"]["80,000 sq ft or more"]["pct"]
    nza["proxy_recomputed"] = proxy(nza_ue, nza_ge80, 0.0)
    nza["proxy_stored"] = {"composite_score": NZA_TOWN["composite_score"],
                           "nza_metrics": {m["label"]: m["value"] for m in NZA_TOWN["nza_metrics"]}}

    comparison = {"composite_ours": base_ours["proxy"]["composite"], "composite_nza_stored": NZA_TOWN["composite_score"],
                  "composite_difference_ours_minus_nza": round(base_ours["proxy"]["composite"] - NZA_TOWN["composite_score"], 1),
                  "composite_sensitivity_mixed_use_3plus_only": sens["proxy"]["composite"]}

    out = {
        "method": "Residential land = districts where Table 2-2 allows at least one building type whose "
                  "'Number of Principal Units' row admits a dwelling. Family status per district: a building type "
                  "allowed in the zone (Table 2-2 check mark) admits a k-unit building when its unit rule permits k units: "
                  "'No limits' = 1 or more, 'N max.' = 1 to N, '3 min.'/'3 minimum' = 3 or more, '1 in House' = exactly 1, "
                  "'2 with special permit' = 2 only after a hearing (hearing status). A Double House A has at least 2 units "
                  "(Sec. 3.80.1: two House A types side by side). 4+-family means a building type that can hold 4 or more "
                  "units. Storefront/Commercial House dwelling entries marked '8' (upper stories only) are counted as allowed. "
                  "The backyard-cottage unit in NX1/NX2 is not counted toward the 4+ test (Row Building already allows 4+ there). "
                  "Shares use our gross parcel acreage (data/land_area/bridgeport.json), not NZA's net of protected land.",
        "source": "public/sources/bridgeport-zoning.pdf (Zone Bridgeport, Table 2-2 and Sec. 3.20-3.120, 4.70, 8.20.1); "
                  "data/land_area/bridgeport.json; NZA data in data/nza_replication/nza_snapshots.json and data/towns/bridgeport.json",
        "residential_districts": residential,
        "no_dwelling_districts": nonres,
        "unclassified_districts": unclassified,
        "unresolved": [
            {"item": "PDD (legacy Planned Development District)", "acres": ACRES["PDD"],
             "why": "Rules sit in each recorded general development plan, not in the mirrored code (Sec. 2.60.1)"},
            {"item": "(blank) parcels", "acres": ACRES["(blank)"], "why": "No zone code in the city layer"},
            {"item": "Row Building amendment 25-06", "acres": None,
             "why": "Noted in V2 as pending in 2025; the July 2022 text mirrored here is what is read"},
            {"item": "NZA reads a pre-2022 code", "acres": None,
             "why": "NZA's Bridgeport map is dated to the earlier code; its status per district cannot be inspected"},
            {"item": "P3 (public/institutional)", "acres": None,
             "why": "Appears in Table 2-2 (Civic Building, household living by special permit) but is not in the acreage file"}],
        "residential_acres_ours": base_ours["residential_acres"],
        "residential_acres_nza": nza_res,
        "per_district": per,
        "unit_rule_cites": cites,
        "other_cites": other,
        "ours": base_ours,
        "ours_sensitivity_mixed_use_only_counts_for_3plus": sens,
        "nza": nza,
        "parking_mandate_pct": {"ours": 0.0, "nza": 0, "basis": other["parking"]["cite"] + ": " + other["parking"]["quote"]},
        "adu": {"ours_acres_on_one_family_land": base_ours["adu_acres_on_one_family_land"],
                "nza_acres": {"allowed": adu["Allowed"], "hearing": adu["Hearing"], "prohibited": adu["Prohibited"]},
                "rule": "N1, N3, N4 allow accessory apartments by right; N2 only with special permit (backyard cottage); "
                        "NX1/NX2 House A page shows '–' for Accessory Apartments (the extra backyard-cottage unit is counted "
                        "as a principal unit); mixed-use House-less zones show '–'"},
        "comparison": comparison,
    }
    os.makedirs(os.path.join(ROOT, "data", "nza_replication"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "nza_replication", "bridgeport.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps({"residential_districts": residential, "residential_acres": base_ours["residential_acres"],
                      "ours": {k: base_ours[k] for k in ("family", "min_lot_bins", "adu_acres_on_one_family_land", "proxy")},
                      "sens": {k: sens[k] for k in ("family", "proxy")},
                      "nza": {"family": nza["family"], "bins": nza["min_lot_bins"], "proxy": nza["proxy_recomputed"]},
                      "comparison": comparison}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
