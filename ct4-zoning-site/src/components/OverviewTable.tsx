"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { Town } from "@/lib/types";

interface Row {
  slug: string;
  name: string;
  score: number;
  nzaScore: number;
  population: number;
  pct2: number;
  pct3: number;
  pct4: number;
  lot80: number;
  parking: number;
  variables: number;
}

type SortKey = keyof Omit<Row, "slug" | "name">;

function toRow(t: Town): Row {
  const byLabel = (needle: string) => t.nza_metrics.find((m) => m.label.includes(needle))?.value ?? 0;
  return {
    slug: t.slug,
    name: t.name,
    score: t.hap_score.composite,
    nzaScore: t.composite_score,
    population: t.population,
    pct2: byLabel("2-family"),
    pct3: byLabel("3-family"),
    pct4: byLabel("4+-family"),
    lot80: byLabel("≥80,000"),
    parking: byLabel("parking mandate"),
    variables: t.variables.length,
  };
}

function cellShade(v: number) {
  const t = Math.max(0, Math.min(100, v)) / 100;
  if (t > 0.66) return "var(--prohibit)";
  if (t > 0.33) return "var(--maybe)";
  return "var(--allow)";
}

const COLUMNS: { key: SortKey; label: string; suffix?: string }[] = [
  { key: "score", label: "HAP Score" },
  { key: "nzaScore", label: "NZA 2026" },
  { key: "population", label: "Population" },
  { key: "pct2", label: "2F Excl.", suffix: "%" },
  { key: "pct3", label: "3F Excl.", suffix: "%" },
  { key: "pct4", label: "4F+ Excl.", suffix: "%" },
  { key: "lot80", label: "Large-Lot", suffix: "%" },
  { key: "parking", label: "Parking Mand.", suffix: "%" },
  { key: "variables", label: "Variables" },
];

export default function OverviewTable({ towns }: { towns: Town[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [query, setQuery] = useState("");
  const router = useRouter();

  const rows = useMemo(() => towns.map(toRow), [towns]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = q ? rows.filter((r) => r.name.toLowerCase().includes(q)) : rows;
    const sorted = [...list].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      return sortDir === "asc" ? av - bv : bv - av;
    });
    return sorted;
  }, [rows, query, sortKey, sortDir]);

  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between gap-3 mb-3">
        <input
          type="text"
          placeholder="Filter towns…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-56 text-sm border border-(--rule) rounded-md px-3 py-1.5 bg-(--surface) focus:outline-none focus:border-(--accent)"
        />
        <p className="text-xs text-(--ink-faint)">{filtered.length} of {rows.length} towns · click a column to sort</p>
      </div>
      <div className="overflow-x-auto border border-(--rule) rounded-lg">
        <table className="w-full text-sm min-w-[820px]">
          <thead>
            <tr className="bg-(--surface-2) text-left">
              <th className="sticky left-0 bg-(--surface-2) px-3 py-2 font-semibold text-xs uppercase tracking-wide text-(--ink-dim) z-10">
                Town
              </th>
              {COLUMNS.map((c) => (
                <th
                  key={c.key}
                  onClick={() => toggleSort(c.key)}
                  className="px-3 py-2 font-semibold text-xs uppercase tracking-wide text-(--ink-dim) cursor-pointer select-none hover:text-(--accent) whitespace-nowrap"
                >
                  {c.label}
                  {sortKey === c.key ? (sortDir === "desc" ? " ↓" : " ↑") : ""}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr
                key={r.slug}
                onClick={() => router.push(`/towns/${r.slug}`)}
                className="border-t border-(--rule) hover:bg-(--surface-2) cursor-pointer"
              >
                <td className="sticky left-0 bg-(--surface) px-3 py-2 font-medium whitespace-nowrap">{r.name}</td>
                <td className="px-3 py-2 tabular font-semibold text-(--accent)">{r.score.toFixed(1)}</td>
                <td className="px-3 py-2 tabular text-(--ink-dim)">{r.nzaScore.toFixed(1)}</td>
                <td className="px-3 py-2 tabular">{r.population.toLocaleString()}</td>
                {(["pct2", "pct3", "pct4", "lot80", "parking"] as const).map((k) => (
                  <td key={k} className="px-3 py-2 tabular">
                    <span style={{ color: cellShade(r[k]) }} className="font-semibold">
                      {r[k].toFixed(1)}
                    </span>
                  </td>
                ))}
                <td className="px-3 py-2 tabular text-(--ink-dim)">{r.variables}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
