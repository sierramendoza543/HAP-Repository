"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { DashboardRow } from "@/lib/towns";

type SortKey =
  | "headline"
  | "nzaProxy"
  | "gap"
  | "population"
  | "pct2"
  | "pct3"
  | "pct4"
  | "lot80"
  | "parking";

function sortValue(r: DashboardRow, key: SortKey): number | null {
  switch (key) {
    case "headline": return r.headline;
    case "nzaProxy": return r.nzaProxy;
    case "gap": return r.gap;
    case "population": return r.population;
    case "pct2": return r.nza.pct2;
    case "pct3": return r.nza.pct3;
    case "pct4": return r.nza.pct4;
    case "lot80": return r.nza.lot80;
    default: return r.nza.parking;
  }
}

function shade(v: number) {
  if (v >= 66) return "var(--prohibit)";
  if (v >= 33) return "var(--maybe)";
  return "var(--allow)";
}

const COLUMNS: { key: SortKey; label: string; hint?: string }[] = [
  { key: "headline", label: "Our score", hint: "District-by-district score, land-weighted; not yet built for every town" },
  { key: "nzaProxy", label: "NZA proxy", hint: "Our weighted blend of three National Zoning Atlas figures" },
  { key: "gap", label: "Difference", hint: "Our score minus the NZA proxy" },
  { key: "pct2", label: "2-family prohibited", hint: "NZA, % of residential land (ours in brackets where recomputed)" },
  { key: "pct3", label: "3-family prohibited" },
  { key: "pct4", label: "4+-family prohibited" },
  { key: "lot80", label: "Large lots", hint: "NZA, % of 1-family land needing 80,000 sq ft or more" },
  { key: "parking", label: "Parking mandate", hint: "NZA, % of residential land with a parking minimum" },
  { key: "population", label: "Population" },
];

function Cell({ nza, ours }: { nza: number; ours: number | undefined }) {
  return (
    <td className="px-3 py-2 tabular whitespace-nowrap">
      <span className="font-semibold" style={{ color: shade(nza) }}>
        {nza.toFixed(1)}
      </span>
      {ours !== undefined && <span className="text-(--ink-faint) text-xs ml-1">({ours.toFixed(1)})</span>}
    </td>
  );
}

export default function DashboardTable({ rows }: { rows: DashboardRow[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("headline");
  const [dir, setDir] = useState<"asc" | "desc">("desc");
  const [query, setQuery] = useState("");
  const [onlyDistrict, setOnlyDistrict] = useState(false);

  const list = useMemo(() => {
    const q = query.trim().toLowerCase();
    let out = rows.filter((r) => (!q || r.name.toLowerCase().includes(q)) && (!onlyDistrict || r.basis === "v2"));
    out = [...out].sort((a, b) => {
      const av = sortValue(a, sortKey);
      const bv = sortValue(b, sortKey);
      if (av === null && bv === null) return 0;
      if (av === null) return 1;
      if (bv === null) return -1;
      return (dir === "asc" ? 1 : -1) * (av - bv);
    });
    return out;
  }, [rows, query, sortKey, dir, onlyDistrict]);

  function toggle(key: SortKey) {
    if (key === sortKey) setDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setDir("desc");
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-3">
          <input
            type="search"
            aria-label="Filter towns"
            placeholder="Filter towns…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-48 text-sm border border-(--rule) rounded-md px-3 py-1.5 bg-(--surface) focus:outline-none focus:border-(--accent)"
          />
          <label className="flex items-center gap-1.5 text-xs text-(--ink-dim)">
            <input type="checkbox" checked={onlyDistrict} onChange={(e) => setOnlyDistrict(e.target.checked)} />
            District-level towns only
          </label>
        </div>
        <p className="text-xs text-(--ink-faint)">
          {list.length} of {rows.length} towns &middot; click a column to sort
        </p>
      </div>
      <div className="overflow-x-auto border border-(--rule) rounded-lg bg-(--surface)">
        <table className="w-full text-sm min-w-[980px]">
          <thead>
            <tr className="bg-(--surface-2) text-left">
              <th className="sticky left-0 bg-(--surface-2) px-3 py-2 text-xs uppercase tracking-wide text-(--ink-dim) z-10">Town</th>
              {COLUMNS.map((c) => (
                <th
                  key={c.key}
                  title={c.hint}
                  aria-sort={sortKey === c.key ? (dir === "desc" ? "descending" : "ascending") : "none"}
                  className="px-3 py-2 text-xs uppercase tracking-wide text-(--ink-dim) whitespace-nowrap"
                >
                  <button onClick={() => toggle(c.key)} className="uppercase tracking-wide font-semibold hover:text-(--accent)">
                    {c.label}
                    {sortKey === c.key ? (dir === "desc" ? " ↓" : " ↑") : ""}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {list.map((r) => (
              <tr key={r.slug} className="border-t border-(--rule) hover:bg-(--surface-2)">
                <td className="sticky left-0 bg-(--surface) px-3 py-2 font-medium whitespace-nowrap">
                  <Link href={`/towns/${r.slug}`} className="hover:text-(--accent) underline-offset-2 hover:underline">
                    {r.name}
                  </Link>
                  <span
                    className={`ml-2 text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded ${
                      r.basis === "v2" ? "bg-(--accent)/15 text-(--accent)" : "bg-(--surface-2) text-(--ink-faint)"
                    }`}
                    title={r.basis === "v2" ? "Scored district by district" : "District scoring not built yet; only the NZA proxy is shown"}
                  >
                    {r.basis === "v2" ? "districts" : "NZA only"}
                  </span>
                </td>
                <td className="px-3 py-2 tabular font-bold" style={{ color: r.headline !== null ? shade(r.headline) : "var(--ink-faint)" }}>
                  {r.headline !== null ? r.headline.toFixed(1) : "\u2013"}
                </td>
                <td className="px-3 py-2 tabular">
                  {r.nzaProxy.toFixed(1)}
                  {r.ours && <span className="text-(--ink-faint) text-xs ml-1">({r.ours.proxy.toFixed(1)})</span>}
                </td>
                <td className="px-3 py-2 tabular text-(--ink-dim)">
                  {r.gap !== null ? `${r.gap >= 0 ? "+" : ""}${r.gap.toFixed(1)}` : "\u2013"}
                </td>
                <Cell nza={r.nza.pct2} ours={r.ours?.pct2} />
                <Cell nza={r.nza.pct3} ours={r.ours?.pct3} />
                <Cell nza={r.nza.pct4} ours={r.ours?.pct4} />
                <Cell nza={r.nza.lot80} ours={r.ours?.lot80} />
                <Cell nza={r.nza.parking} ours={r.ours?.parking} />
                <td className="px-3 py-2 tabular text-(--ink-dim)">{r.population.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-(--ink-faint) mt-2">
        A dash means district scoring is not built for that town yet. Bracketed figures are our own recomputation of the same NZA measure from the town&rsquo;s zoning code
        (district-level towns only). The NZA proxy in brackets uses the same formula on our recomputed figures.
      </p>
    </div>
  );
}
