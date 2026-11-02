import Link from "next/link";
import type { DashboardRow } from "@/lib/towns";
import type { NzaCompare, Town } from "@/lib/types";
import { scoreRamp } from "@/lib/colors";

// ---------------------------------------------------------------------------------------------
// Agreement chart: our score against the NZA proxy, one dot per town. The dashed diagonal is
// perfect agreement; dots above it are towns we score as more restrictive than the proxy does.
// ---------------------------------------------------------------------------------------------
export function AgreementChart({ rows }: { rows: DashboardRow[] }) {
  const pts = rows.filter((r): r is DashboardRow & { headline: number } => r.headline !== null);
  const W = 560;
  const H = 420;
  const m = { l: 44, r: 16, t: 14, b: 40 };
  const x = (v: number) => m.l + (v / 100) * (W - m.l - m.r);
  const y = (v: number) => H - m.b - (v / 100) * (H - m.t - m.b);
  const ticks = [0, 25, 50, 75, 100];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Our score against the NZA proxy for each town">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={m.t} y2={H - m.b} stroke="var(--rule)" />
          <line x1={m.l} x2={W - m.r} y1={y(t)} y2={y(t)} stroke="var(--rule)" />
          <text x={x(t)} y={H - m.b + 16} textAnchor="middle" fontSize={10} fill="var(--ink-faint)">{t}</text>
          <text x={m.l - 8} y={y(t) + 3} textAnchor="end" fontSize={10} fill="var(--ink-faint)">{t}</text>
        </g>
      ))}
      <line x1={x(0)} y1={y(0)} x2={x(100)} y2={y(100)} stroke="var(--ink-faint)" strokeDasharray="4 4" />
      <text x={x(78)} y={y(86)} fontSize={10} fill="var(--ink-faint)" transform={`rotate(-38 ${x(78)} ${y(86)})`}>perfect agreement</text>
      <text x={(W + m.l) / 2} y={H - 4} textAnchor="middle" fontSize={11} fill="var(--ink-dim)">NZA-derived proxy</text>
      <text x={12} y={H / 2} textAnchor="middle" fontSize={11} fill="var(--ink-dim)" transform={`rotate(-90 12 ${H / 2})`}>Our score</text>
      {pts.map((r) => (
        <g key={r.slug}>
          <title>{`${r.name}: our score ${r.headline.toFixed(1)}, NZA proxy ${r.nzaProxy.toFixed(1)}`}</title>
          <Link href={`/towns/${r.slug}`}>
            <circle
              cx={x(r.nzaProxy)}
              cy={y(r.headline)}
              r={7}
              fill={scoreRamp(r.headline)}
              stroke="var(--ink)"
              strokeWidth={1.6}
              opacity={0.92}
            />
            <text x={x(r.nzaProxy) + 9} y={y(r.headline) + 3} fontSize={9} fill="var(--ink-dim)">{r.name}</text>
          </Link>
        </g>
      ))}
    </svg>
  );
}

// ---------------------------------------------------------------------------------------------
// Side-by-side bars: our score vs NZA proxy for every town, sorted by our score.
// ---------------------------------------------------------------------------------------------
export function ScoreBars({ rows }: { rows: DashboardRow[] }) {
  return (
    <div className="flex flex-col gap-1.5">
      {rows.map((r) => (
        <div key={r.slug} className="grid grid-cols-[92px_1fr_44px] items-center gap-2 text-xs">
          <Link href={`/towns/${r.slug}`} className="truncate hover:text-(--accent)">{r.name}</Link>
          <div className="flex flex-col gap-0.5" aria-hidden>
            <div className="h-2.5 rounded bg-(--surface-2) overflow-hidden">
              {r.headline !== null && <div className="h-full rounded" style={{ width: `${r.headline}%`, background: scoreRamp(r.headline) }} />}
            </div>
            <div className="h-2.5 rounded bg-(--surface-2) overflow-hidden">
              <div className="h-full rounded bg-(--ink-faint)/70" style={{ width: `${r.nzaProxy}%` }} />
            </div>
          </div>
          <div className="tabular text-right leading-tight">
            <div className="font-semibold">{r.headline !== null ? r.headline.toFixed(1) : "\u2013"}</div>
            <div className="text-(--ink-faint)">{r.nzaProxy.toFixed(1)}</div>
          </div>
        </div>
      ))}
      <p className="text-[11px] text-(--ink-faint) mt-1">
        Top bar and top number: our score (a dash means not yet scored by district). Gray bar and bottom number: NZA-derived proxy.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------------------------
// Land by score: for each district-level town, one bar whose segments are districts, as wide
// as their share of the scored land and colored by their V2 score.
// ---------------------------------------------------------------------------------------------
export function LandByScore({ towns }: { towns: Town[] }) {
  return (
    <div className="flex flex-col gap-4">
      {towns.map((t) => {
        const ds = t.v2!.districts.filter((d) => d.included && d.score !== null).sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
        const total = ds.reduce((s, d) => s + d.acres, 0);
        return (
          <div key={t.slug}>
            <div className="flex items-baseline justify-between mb-1">
              <Link href={`/towns/${t.slug}`} className="text-sm font-semibold hover:text-(--accent)">{t.name}</Link>
              <span className="text-xs tabular text-(--ink-dim)">
                {t.v2!.land_weighted_score?.toFixed(1)} V2 &middot; NZA proxy {t.composite_score.toFixed(1)} &middot; {total.toLocaleString()} acres scored
              </span>
            </div>
            <div className="flex h-9 rounded overflow-hidden border border-(--rule)" role="img" aria-label={`${t.name} land by district score`}>
              {ds.map((d) => (
                <div
                  key={d.district}
                  title={`${d.district}: ${d.score!.toFixed(1)} · ${d.acres.toLocaleString()} acres (${((d.acres / total) * 100).toFixed(1)}%)`}
                  className="h-full flex items-center justify-center text-[10px] font-semibold text-white overflow-hidden whitespace-nowrap"
                  style={{ width: `${(d.acres / total) * 100}%`, background: scoreRamp(d.score!), borderRight: "1px solid rgba(255,255,255,0.5)" }}
                >
                  {(d.acres / total) * 100 > 6 ? d.district : ""}
                </div>
              ))}
            </div>
          </div>
        );
      })}
      <p className="text-[11px] text-(--ink-faint)">
        Segment width is the district&rsquo;s share of scored land; color is its V2 score (green least restrictive, red most). Hover for details.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------------------------
// Heatmap of our four components (share of the maximum points, land-weighted), district towns.
// ---------------------------------------------------------------------------------------------
const COMP_SHORT: Record<string, string> = {
  "Multifamily Access": "Multifamily access",
  "Approval Discretion": "Approval",
  "Minimum Lot Size": "Lot size",
  "ADU Approval Pathway": "ADU pathway",
};

export function ComponentHeatmap({ rows }: { rows: DashboardRow[] }) {
  const v2 = rows.filter((r) => r.components);
  const labels = v2[0]?.components?.map((c) => c.label) ?? [];
  return (
    <div className="overflow-x-auto border border-(--rule) rounded-lg bg-(--surface)">
      <table className="w-full text-sm min-w-[560px]">
        <thead>
          <tr className="bg-(--surface-2) text-xs uppercase tracking-wide text-(--ink-dim)">
            <th className="text-left px-3 py-2 font-semibold">Town</th>
            {labels.map((l) => (
              <th key={l} className="px-2 py-2 font-semibold text-center">{COMP_SHORT[l] ?? l}</th>
            ))}
            <th className="px-2 py-2 font-semibold text-center">Town V2</th>
            <th className="px-2 py-2 font-semibold text-center">NZA proxy</th>
          </tr>
        </thead>
        <tbody>
          {v2.map((r) => (
            <tr key={r.slug} className="border-t border-(--rule)">
              <td className="px-3 py-1.5 font-medium whitespace-nowrap">
                <Link href={`/towns/${r.slug}`} className="hover:text-(--accent)">{r.name}</Link>
              </td>
              {r.components!.map((c) => (
                <td key={c.label} className="px-1 py-1.5">
                  <div
                    className="h-7 rounded flex items-center justify-center text-[11px] font-semibold tabular text-white"
                    style={{ background: scoreRamp(c.pct) }}
                    title={`${r.name} — ${c.label}: ${c.pct}% of the maximum points, land-weighted`}
                  >
                    {c.pct.toFixed(0)}
                  </div>
                </td>
              ))}
              <td className="px-1 py-1.5">
                <div className="h-7 rounded flex items-center justify-center text-[11px] font-bold tabular text-white" style={{ background: scoreRamp(r.v2 ?? 0) }}>
                  {r.v2?.toFixed(1)}
                </div>
              </td>
              <td className="px-1 py-1.5">
                <div className="h-7 rounded flex items-center justify-center text-[11px] font-bold tabular text-white" style={{ background: scoreRamp(r.nzaProxy) }}>
                  {r.nzaProxy.toFixed(1)}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-[11px] text-(--ink-faint) px-3 py-2 border-t border-(--rule)">
        Each cell is the land-weighted share of that component&rsquo;s maximum points (0 = least restrictive, 100 = most).
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------------------------
// Heatmap of the NZA snapshot metrics for every town, with our recomputation where we have one.
// ---------------------------------------------------------------------------------------------
const NZA_COLS: { key: "pct2" | "pct3" | "pct4" | "lot80" | "parking"; label: string }[] = [
  { key: "pct2", label: "2-family prohibited" },
  { key: "pct3", label: "3-family prohibited" },
  { key: "pct4", label: "4+-family prohibited" },
  { key: "lot80", label: "Large lots" },
  { key: "parking", label: "Parking mandate" },
];

export function NzaHeatmap({ rows }: { rows: DashboardRow[] }) {
  return (
    <div className="overflow-x-auto border border-(--rule) rounded-lg bg-(--surface)">
      <table className="w-full text-sm min-w-[640px]">
        <thead>
          <tr className="bg-(--surface-2) text-xs uppercase tracking-wide text-(--ink-dim)">
            <th className="text-left px-3 py-2 font-semibold">Town</th>
            {NZA_COLS.map((c) => (
              <th key={c.key} className="px-2 py-2 font-semibold text-center">{c.label}</th>
            ))}
            <th className="px-2 py-2 font-semibold text-center">NZA proxy</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.slug} className="border-t border-(--rule)">
              <td className="px-3 py-1.5 font-medium whitespace-nowrap">
                <Link href={`/towns/${r.slug}`} className="hover:text-(--accent)">{r.name}</Link>
              </td>
              {NZA_COLS.map((c) => {
                const v = r.nza[c.key];
                const ours = r.ours?.[c.key];
                return (
                  <td key={c.key} className="px-1 py-1.5">
                    <div
                      className="h-7 rounded flex items-center justify-center gap-1 text-[11px] font-semibold tabular text-white"
                      style={{ background: scoreRamp(v) }}
                      title={`${r.name} — ${c.label}: NZA ${v}%${ours !== undefined ? `, our recomputation ${ours}%` : ""}`}
                    >
                      {v.toFixed(0)}
                      {ours !== undefined && <span className="font-normal opacity-80">({ours.toFixed(0)})</span>}
                    </div>
                  </td>
                );
              })}
              <td className="px-1 py-1.5">
                <div className="h-7 rounded flex items-center justify-center text-[11px] font-bold tabular text-white" style={{ background: scoreRamp(r.nzaProxy) }}>
                  {r.nzaProxy.toFixed(1)}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-[11px] text-(--ink-faint) px-3 py-2 border-t border-(--rule)">
        National Zoning Atlas Jurisdiction Snapshot, % of land. Bracketed numbers are our recomputation of the same measure from the town&rsquo;s zoning code.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------------------------
// NZA check: for each district-level town, what share of residential land prohibits 4+-family
// housing, NZA versus our recomputation, and the two proxies.
// ---------------------------------------------------------------------------------------------
export function NzaCheck({ compare, names }: { compare: Record<string, NzaCompare>; names: Record<string, string> }) {
  const slugs = Object.keys(compare);
  return (
    <div className="grid sm:grid-cols-2 gap-4">
      {slugs.map((s) => {
        const c = compare[s];
        const rowsData: [string, number, number][] = [
          ["4+-family prohibited", c.prohibited["4+-family"].nza, c.prohibited["4+-family"].ours],
          ["2-family prohibited", c.prohibited["2-family"].nza, c.prohibited["2-family"].ours],
          ["Large-lot share", c.lot80.nza, c.lot80.ours],
          ["Parking mandate", c.parking.nza, c.parking.ours],
          ["NZA-style proxy", c.proxy.nza_stored, c.proxy.ours],
        ];
        return (
          <div key={s} className="border border-(--rule) rounded-lg p-3 bg-(--surface)">
            <div className="flex items-baseline justify-between mb-2">
              <Link href={`/towns/${s}`} className="text-sm font-semibold hover:text-(--accent)">{names[s]}</Link>
              <span className="text-xs tabular text-(--ink-dim)">
                proxy difference {c.proxy.difference >= 0 ? "+" : ""}{c.proxy.difference.toFixed(1)}
              </span>
            </div>
            <div className="flex flex-col gap-1.5">
              {rowsData.map(([label, nza, ours]) => (
                <div key={label} className="grid grid-cols-[110px_1fr_74px] items-center gap-2 text-[11px]">
                  <span className="text-(--ink-dim)">{label}</span>
                  <div className="flex flex-col gap-0.5" aria-hidden>
                    <div className="h-2 rounded bg-(--surface-2)"><div className="h-full rounded bg-(--ink-faint)/70" style={{ width: `${Math.min(100, nza)}%` }} /></div>
                    <div className="h-2 rounded bg-(--surface-2)"><div className="h-full rounded bg-(--accent)" style={{ width: `${Math.min(100, ours)}%` }} /></div>
                  </div>
                  <span className="tabular text-right leading-tight">
                    <span className="block text-(--ink-faint)">NZA {nza.toFixed(1)}</span>
                    <span className="block font-semibold">ours {ours.toFixed(1)}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
