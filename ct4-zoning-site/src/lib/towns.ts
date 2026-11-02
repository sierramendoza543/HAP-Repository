import fs from "node:fs";
import path from "node:path";
import type { NzaCompare, Town } from "./types";

const TOWNS_DIR = path.join(process.cwd(), "data", "towns");

export function getAllTowns(): Town[] {
  const files = fs.readdirSync(TOWNS_DIR).filter((f) => f.endsWith(".json"));
  const towns = files.map((f) => {
    const raw = fs.readFileSync(path.join(TOWNS_DIR, f), "utf-8");
    return JSON.parse(raw) as Town;
  });
  return towns.sort((a, b) => b.hap_score.composite - a.hap_score.composite);
}

export function getTown(slug: string): Town | null {
  if (!getAllSlugs().includes(slug)) return null;
  const file = path.join(TOWNS_DIR, `${slug}.json`);
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf-8")) as Town;
}

export function getAllSlugs(): string[] {
  return fs
    .readdirSync(TOWNS_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""));
}

export function compositeBreakdown(town: Town) {
  const byLabel = (needle: string) =>
    town.nza_metrics.find((m) => m.label.includes(needle))!;
  const pct2 = byLabel("2-family").value;
  const pct3 = byLabel("3-family").value;
  const pct4 = byLabel("4+-family").value;
  const lot80 = byLabel("≥80,000").value;
  const parking = byLabel("parking mandate").value;
  const useExclusion = (pct2 + pct3 + pct4) / 3;
  return [
    { key: "use_exclusion", label: "Use Exclusion", weight: 0.3, raw: useExclusion, contribution: (0.3 * useExclusion) / 0.7 },
    { key: "density", label: "Large-Lot Zoning", weight: 0.25, raw: lot80, contribution: (0.25 * lot80) / 0.7 },
    { key: "parking", label: "Parking Mandates", weight: 0.15, raw: parking, contribution: (0.15 * parking) / 0.7 },
  ];
}

let nzaCompareCache: Record<string, NzaCompare> | null = null;

export function getNzaCompare(): Record<string, NzaCompare> {
  if (!nzaCompareCache) {
    const file = path.join(process.cwd(), "data", "nza_compare.json");
    nzaCompareCache = JSON.parse(fs.readFileSync(file, "utf-8")) as Record<string, NzaCompare>;
  }
  return nzaCompareCache;
}

export interface DashboardRow {
  slug: string;
  name: string;
  population: number;
  districtsAnalyzed: number;
  headline: number | null;
  basis: "v2" | "nza";
  v2: number | null;
  v2Districts: number;
  v2Acres: number;
  hap: number;
  nzaProxy: number;
  nzaLive: number | null;
  gap: number | null;
  nza: {
    pct2: number;
    pct3: number;
    pct4: number;
    lot80: number;
    parking: number;
  };
  ours: { pct2: number; pct3: number; pct4: number; lot80: number; parking: number; proxy: number } | null;
  components: { label: string; pct: number }[] | null;
}

const CORE = ["Multifamily Access", "Approval Discretion", "Minimum Lot Size", "ADU Approval Pathway"];

export function getDashboardRows(): DashboardRow[] {
  const compare = getNzaCompare();
  const rows = getAllTowns().map((t): DashboardRow => {
    const byLabel = (needle: string) => t.nza_metrics.find((m) => m.label.includes(needle))?.value ?? 0;
    const v2 = t.v2?.land_weighted_score ?? null;
    const c = compare[t.slug];
    let components: DashboardRow["components"] = null;
    if (t.v2) {
      const included = t.v2.districts.filter((d) => d.included);
      const acres = included.reduce((s, d) => s + d.acres, 0);
      components = CORE.map((label) => {
        let pts = 0;
        let max = 0;
        for (const d of included) {
          const f = d.factors.find((x) => x.label === label);
          if (!f || f.points === null) continue;
          pts += f.points * d.acres;
          max += f.max_points * d.acres;
        }
        return { label, pct: max && acres ? Math.round((pts / max) * 1000) / 10 : 0 };
      });
    }
    return {
      slug: t.slug,
      name: t.name,
      population: t.population,
      districtsAnalyzed: t.districts_analyzed,
      headline: v2,
      basis: v2 !== null ? "v2" : "nza",
      v2,
      v2Districts: t.v2?.districts_included ?? 0,
      v2Acres: t.v2?.acres_included ?? 0,
      hap: t.hap_score.composite,
      nzaProxy: t.composite_score,
      nzaLive: c ? c.proxy.nza_live : null,
      gap: v2 !== null ? Math.round((v2 - t.composite_score) * 10) / 10 : null,
      nza: {
        pct2: byLabel("2-family"),
        pct3: byLabel("3-family"),
        pct4: byLabel("4+-family"),
        lot80: byLabel("≥80,000"),
        parking: byLabel("parking mandate"),
      },
      ours: c
        ? {
            pct2: c.prohibited["2-family"].ours,
            pct3: c.prohibited["3-family"].ours,
            pct4: c.prohibited["4+-family"].ours,
            lot80: c.lot80.ours,
            parking: c.parking.ours,
            proxy: c.proxy.ours,
          }
        : null,
      components,
    };
  });
  // District-scored towns first (by our score), then the rest by the NZA proxy.
  return rows.sort((a, b) => {
    if (a.headline !== null && b.headline !== null) return b.headline - a.headline;
    if (a.headline !== null) return -1;
    if (b.headline !== null) return 1;
    return b.nzaProxy - a.nzaProxy;
  });
}
