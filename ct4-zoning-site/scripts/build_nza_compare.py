"""Normalize the four per-town NZA replication files into one compact file for the website.

Reads data/nza_replication/{stamford,greenwich,norwalk,bridgeport}.json and data/towns/*.json,
writes data/nza_compare.json. Every figure is "ours" (recomputed from the town's zoning code and our
district acreage) next to "nza" (read from the National Zoning Atlas Jurisdiction Snapshot).

Run with: python3 -I scripts/build_nza_compare.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "data", "nza_replication")
FAMILIES = ("1-family", "2-family", "3-family", "4+-family")
LOT80 = "80,000 sq ft or more"


def load(name):
    with open(os.path.join(REP, f"{name}.json")) as f:
        return json.load(f)


def town_proxy_stored(slug):
    with open(os.path.join(ROOT, "data", "towns", f"{slug}.json")) as f:
        return json.load(f)["composite_score"]


def proxy(prohibited, lot80, parking):
    use_exclusion = (prohibited["2-family"] + prohibited["3-family"] + prohibited["4+-family"]) / 3
    return round((0.30 * use_exclusion + 0.25 * lot80 + 0.15 * parking) / 0.70, 1)


def pairs_from_pct(housing, key_ours, key_nza, status):
    return {fam: {"ours": housing[fam][key_ours][status], "nza": housing[fam][key_nza][status]} for fam in FAMILIES}


def stamford():
    d = load("stamford")
    h = d["housing"]
    return {
        "as_of_right": pairs_from_pct(h, "ours_pct", "nza_pct", "as_of_right"),
        "hearing": pairs_from_pct(h, "ours_pct", "nza_pct", "hearing"),
        "prohibited": pairs_from_pct(h, "ours_pct", "nza_pct", "prohibited"),
        "lot80": {"ours": d["min_lot_size"]["bins"][LOT80]["ours_pct"], "nza": d["min_lot_size"]["bins"][LOT80]["nza_pct"]},
        "parking": {"ours": d["parking_mandate_pct"]["ours"], "nza": d["parking_mandate_pct"]["nza"]},
        "adu": {"ours": d["adu"]["ours"], "nza": d["adu"]["nza"]},
        "base_acres": {"ours": d["residential_acres_ours"], "nza": d["residential_acres_nza"]},
        "notes": [
            "NZA shows 17.6% of residential land where 4+-family housing may be allowed after a hearing; Appendix A of the 2024 code shows none, and the difference is unexplained.",
            "NZA codes every 1-family acre as ADU-prohibited; the 2024 code allows ADUs by zoning permit with owner occupancy on lots of at least 10,000 sq ft.",
            "Our shares use gross district acres; NZA removes protected and unzoned land.",
        ],
    }


def greenwich():
    d = load("greenwich")
    h = d["housing"]
    lot = d["min_lot_size"]["bins"][LOT80]
    return {
        "as_of_right": pairs_from_pct(h, "ours_pct", "nza_pct", "as_of_right"),
        "hearing": pairs_from_pct(h, "ours_pct", "nza_pct", "hearing"),
        "prohibited": pairs_from_pct(h, "ours_pct", "nza_pct", "prohibited"),
        "lot80": {"ours": lot["ours_pct"], "nza": lot["nza_pct"]},
        "parking": {"ours": d["parking_mandate_pct"]["ours"], "nza": d["parking_mandate_pct"]["nza"]},
        "adu": {"ours": d["adu"]["ours"], "nza": "NZA codes 87.5% of 1-family land as allowed with occupancy restrictions and 12.4% prohibited"},
        "base_acres": {"ours": d["residential_acres_ours"], "nza": d["residential_acres_nza"]},
        "proxy_override": {"ours": d["proxy"]["ours"]["composite"],
                           "nza_stored": d["proxy"]["nza_stored_in_town_file"]["composite"],
                           "nza_live": d["proxy"]["nza_recomputed_from_snapshot_acres"]["composite"]},
        "notes": [
            "Stored NZA inputs were checked against NZA's live snapshot on 2026-11-02 and match it (parking 100%, large-lot 65.0%).",
            "Single-family parking (Sec. 6-154) requires 'sufficient' spaces with no number, so we count it as a mandate; NZA's 92% probably counts only numeric minimums.",
            "1,229 acres of conservation, R-PR and R-PHD zones are unclassified because their text is not mirrored.",
        ],
    }


def norwalk():
    d = load("norwalk")
    c = d["cases"]["confirmed"]
    s = d["cases"]["sensitivity"]
    h = c["housing"]
    return {
        "as_of_right": pairs_from_pct(h, "ours_pct", "nza_pct", "as_of_right"),
        "hearing": pairs_from_pct(h, "ours_pct", "nza_pct", "hearing"),
        "prohibited": pairs_from_pct(h, "ours_pct", "nza_pct", "prohibited"),
        "lot80": {"ours": c["min_lot_size"]["bins"][LOT80]["ours_pct"], "nza": c["min_lot_size"]["bins"][LOT80]["nza_pct"]},
        "parking": {"ours": c["parking_mandate_pct"]["ours"], "nza": c["parking_mandate_pct"]["nza"]},
        "adu": {"ours": "Permitted by zoning permit with limitations in every Community District (Table 4.3.9.D)",
                "nza": "NZA codes 10,018 of 10,019 acres of 1-family land as allowed with occupancy restrictions"},
        "base_acres": {"ours": c["residential_acres_ours"], "nza": c["residential_acres_nza"]},
        "proxy_override": {"ours": c["proxy"]["ours"], "nza_stored": c["proxy"]["nza"], "nza_live": d["nza"]["composite"],
                           "ours_with_unconfirmed_districts": s["proxy"]["ours"]},
        "notes": [
            "Only five districts have user-confirmed acreage; CD-3W, CD-3C, CD-4 and CD-4W (multifamily) are not in the base, so our multifamily share is below NZA's. Adding them from the unconfirmed flyer crosswalk gives a proxy of %s." % s["proxy"]["ours"],
            "NZA coded the pre-2024 code and our acreage layer is also pre-rewrite.",
        ],
    }


def bridgeport():
    d = load("bridgeport")
    fam_o, fam_n = d["ours"]["family"], d["nza"]["family"]
    return {
        "as_of_right": {f: {"ours": fam_o[f]["pct"]["as_of_right"], "nza": fam_n[f]["pct"]["as_of_right"]} for f in FAMILIES},
        "hearing": {f: {"ours": fam_o[f]["pct"]["hearing"], "nza": fam_n[f]["pct"]["hearing"]} for f in FAMILIES},
        "prohibited": {f: {"ours": fam_o[f]["pct"]["prohibited"], "nza": fam_n[f]["pct"]["prohibited"]} for f in FAMILIES},
        "lot80": {"ours": d["ours"]["min_lot_bins"][LOT80]["pct"], "nza": d["nza"]["min_lot_bins"][LOT80]["pct"]},
        "parking": {"ours": d["parking_mandate_pct"]["ours"], "nza": d["parking_mandate_pct"]["nza"]},
        "adu": {"ours": "By right in N1, N3, N4; special permit in N2 (accessory apartment rules, Sec. 3.90-3.120)",
                "nza": "NZA codes 1,132 acres allowed and 1,096 acres hearing, close to our N1+N3+N4 and N2"},
        "base_acres": {"ours": d["residential_acres_ours"], "nza": d["residential_acres_nza"]},
        "proxy_override": {"ours": d["comparison"]["composite_ours"], "nza_stored": d["comparison"]["composite_nza_stored"],
                           "nza_live": d["nza"]["proxy_recomputed"]["composite"],
                           "ours_with_unconfirmed_districts": d["comparison"]["composite_sensitivity_mixed_use_3plus_only"]},
        "notes": [
            "NZA has about 378 more 1-family-prohibited acres than we find; one possible cause is treating upper-story-only storefront units as not 1-family (that reading gives a proxy of %s)." % d["comparison"]["composite_sensitivity_mixed_use_3plus_only"],
            "NZA reads a pre-2022 code; Bridgeport adopted Zone Bridgeport in 2022.",
        ],
    }


def main():
    out = {}
    for slug, fn in (("stamford", stamford), ("greenwich", greenwich), ("norwalk", norwalk), ("bridgeport", bridgeport)):
        r = fn()
        ours_prohibited = {f: r["prohibited"][f]["ours"] for f in FAMILIES}
        override = r.pop("proxy_override", None)
        stored = town_proxy_stored(slug)
        ours = override["ours"] if override else proxy(ours_prohibited, r["lot80"]["ours"], r["parking"]["ours"])
        nza_live = override["nza_live"] if override else stored
        r["proxy"] = {"ours": ours, "nza_stored": stored, "nza_live": nza_live,
                      "difference": round(ours - stored, 1)}
        if override and "ours_with_unconfirmed_districts" in override:
            r["proxy"]["ours_with_unconfirmed_districts"] = override["ours_with_unconfirmed_districts"]
        r["method"] = ("Recomputed from the town's mirrored zoning code and our district acreage, using NZA's own definitions "
                       "(share of residential land by status; 1-family minimum-lot bins; parking mandate share) and the proxy "
                       "formula (0.30 x mean of 2-, 3-, 4+-family prohibited + 0.25 x large-lot share + 0.15 x parking share) / 0.70.")
        r["replication_file"] = f"data/nza_replication/{slug}.json"
        out[slug] = r
    with open(os.path.join(ROOT, "data", "nza_compare.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for slug, r in out.items():
        print(slug, r["proxy"])


if __name__ == "__main__":
    main()
