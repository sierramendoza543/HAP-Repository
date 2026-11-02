"""Recompute the National Zoning Atlas Jurisdiction Snapshot figures for Stamford from our own
sources: the dwelling rows of Appendix A, Table I in the mirrored zoning code, the minimum lot
sizes we quote in V2, and our district acreage (data/land_area/stamford.json).

Run with: python3 -I scripts/replicate_nza_stamford.py
Writes data/nza_replication/stamford.json.
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "public", "sources", "stamford-zoning.pdf")
APPENDIX_A_PDF_PAGE = 438  # "Dwelling, ..." rows of Appendix A, Table I (printed page A-4)

COLUMNS = ["RA-3", "RA-2", "RA-1", "R-20", "R-10", "R-7 1/2", "R-6", "RM-1", "R-5", "R-MF", "R-H",
           "C-N", "C-B", "C-L", "C-G", "CC", "C-I", "M-L", "M-G"]  # header order of Table I
MIN_LOT_SQFT = {"RA-3": 130680, "RA-2": 87120, "RA-1": 43560, "R-20": 20000, "R-10": 10000,
                "R-7 1/2": 7500, "R-6": 5000, "RM-1": 5000, "R-5": 5000, "R-MF": 5000, "R-H": 5000}
LOT_BINS = [("None", 0, 1), ("Less than 10,000 sq ft", 1, 10000), ("10,000 to 19,999 sq ft", 10000, 20000),
            ("20,000 to 39,999 sq ft", 20000, 40000), ("40,000 to 79,999 sq ft", 40000, 80000),
            ("80,000 sq ft or more", 80000, 10 ** 9)]

# NZA Jurisdiction Snapshot for Stamford (jurisdiction 304), read from the chart data on
# https://edit.zoningatlas.org/statsrollup/jurisdiction/304/ . Acres are NZA's own.
NZA = {
    "residential_acres": 16981 + 712,
    "as_of_right": {"1-family": 16944, "2-family": 1826, "3-family": 1507, "4+-family": 1507},
    "hearing": {"1-family": 505, "2-family": 564, "3-family": 629, "4+-family": 3108},
    "prohibited": {"1-family": 244, "2-family": 15303, "3-family": 15557, "4+-family": 13078},
    "min_lot_acres": {"None": 19, "Less than 10,000 sq ft": 2859, "10,000 to 19,999 sq ft": 2891,
                      "20,000 to 39,999 sq ft": 0, "40,000 to 79,999 sq ft": 7459,
                      "80,000 sq ft or more": 3717},
    "adu_prohibited_acres": 16944,
    "parking_mandate_pct": 100,
}


def dwelling_rows():
    text = subprocess.run(["pdftotext", "-q", "-f", str(APPENDIX_A_PDF_PAGE), "-l", str(APPENDIX_A_PDF_PAGE),
                           "-layout", PDF, "-"], capture_output=True, text=True, check=True).stdout
    text = text.replace("‐", "-").replace("‑", "-")
    rows = {}
    for key, label in (("1-family", "Dwelling, Single-Family"), ("2-family", "Dwelling, Two-Family"),
                       ("3+-family", "Dwelling, Multi-Family")):
        line = next(l for l in text.splitlines() if l.strip().startswith(label))
        tokens = line.strip()[len(label):].split()
        if len(tokens) != len(COLUMNS):
            raise SystemExit(f"{label}: expected {len(COLUMNS)} symbols, found {len(tokens)}: {tokens}")
        rows[key] = dict(zip(COLUMNS, tokens))
    return rows, {k: line.strip() for k, line in ()}


def main():
    land = json.load(open(os.path.join(ROOT, "data", "land_area", "stamford.json")))["districts"]
    acres = {d: land[d]["acres"] for d in COLUMNS}
    rows, _ = dwelling_rows()

    def status(sym):
        return "as_of_right" if sym == "√" else ("hearing" if sym in ("A", "B") else "prohibited")

    residential = [d for d in COLUMNS if any(rows[k][d] != "-" for k in rows)]
    base = sum(acres[d] for d in residential)

    out = {"method": "Districts that allow at least one dwelling type in Appendix A, Table I are treated as "
                     "residential land. Shares use our district acreage (gross, before NZA's protected-land and "
                     "unzoned-land deductions). Symbol key: a check mark is as-of-right (site plan may still apply), "
                     "A and B are Zoning Board of Appeals or Zoning Board approval, a dash is not permitted.",
           "source": "public/sources/stamford-zoning.pdf, Appendix A Table I (PDF page 438); data/land_area/stamford.json",
           "residential_districts": residential, "residential_acres_ours": round(base, 1),
           "residential_acres_nza": NZA["residential_acres"], "housing": {}}
    for key, nza_key in (("1-family", "1-family"), ("2-family", "2-family"),
                         ("3+-family", "3-family"), ("3+-family", "4+-family")):
        label = nza_key
        ours = {"as_of_right": 0.0, "hearing": 0.0, "prohibited": 0.0}
        for d in residential:
            ours[status(rows[key][d])] += acres[d]
        out["housing"][label] = {
            "ours_pct": {k: round(v / base * 100, 1) for k, v in ours.items()},
            "nza_pct": {k: round(NZA[k][nza_key] / NZA["residential_acres"] * 100, 1)
                        for k in ("as_of_right", "hearing", "prohibited")},
            "districts_as_of_right": [d for d in residential if status(rows[key][d]) == "as_of_right"],
            "districts_hearing": [d for d in residential if status(rows[key][d]) == "hearing"],
        }

    one_family = [d for d in residential if rows["1-family"][d] == "√"]
    sized = [d for d in one_family if d in MIN_LOT_SQFT]
    sized_acres = sum(acres[d] for d in sized)
    unknown = [d for d in one_family if d not in MIN_LOT_SQFT]
    bins = {}
    for name, lo, hi in LOT_BINS:
        ds = [d for d in sized if lo <= MIN_LOT_SQFT[d] < hi]
        bins[name] = {"districts": ds, "ours_pct": round(sum(acres[d] for d in ds) / sized_acres * 100, 1),
                      "nza_pct": round(NZA["min_lot_acres"][name] / sum(NZA["min_lot_acres"].values()) * 100, 1)}
    out["min_lot_size"] = {"bins": bins, "districts_without_a_quoted_minimum": unknown,
                           "acres_without_a_quoted_minimum": round(sum(acres[d] for d in unknown), 1),
                           "note": "Minimum lot sizes are the ones quoted in the V2 inputs; commercial districts that permit "
                                   "single-family are left out of the bins because we have no quoted minimum for them."}
    out["parking_mandate_pct"] = {"ours": 100.0, "nza": NZA["parking_mandate_pct"],
                                  "basis": "Table 12.7 (Residential Parking Requirements by Parking Category) applies to every residential use"}
    out["adu"] = {"ours": "Allowed by Zoning Permit with owner-occupancy on lots of at least 10,000 sq ft, in every district that permits single-family (ADU definition, Sec. 4)",
                  "nza": "100% of 1-family land coded Prohibited"}

    os.makedirs(os.path.join(ROOT, "data", "nza_replication"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "nza_replication", "stamford.json"), "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
