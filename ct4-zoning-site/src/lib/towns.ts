import fs from "node:fs";
import path from "node:path";
import type { Town } from "./types";

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
