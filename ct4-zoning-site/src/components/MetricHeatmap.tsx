import Link from "next/link";
import type { Town } from "@/lib/types";

const METRICS = [
  "2-family housing prohibited",
  "3-family housing prohibited",
  "4+-family housing prohibited",
  "1-family lots requiring ≥80,000 sq ft",
  "Residential land with a parking mandate",
];

const SHORT = ["2F exclusion", "3F exclusion", "4F+ exclusion", "Large-lot %", "Parking mandate"];

function cellColor(v: number) {
  // 0 -> --allow (green), 100 -> --prohibit (red), via a muted amber midpoint
  const t = Math.max(0, Math.min(100, v)) / 100;
  const stops: [number, [number, number, number]][] = [
    [0, [47, 111, 78]],
    [0.5, [184, 134, 58]],
    [1, [138, 47, 39]],
  ];
  let lo = stops[0], hi = stops[stops.length - 1];
  for (let i = 0; i < stops.length - 1; i++) {
    if (t >= stops[i][0] && t <= stops[i + 1][0]) {
      lo = stops[i];
      hi = stops[i + 1];
      break;
    }
  }
  const span = hi[0] - lo[0] || 1;
  const localT = (t - lo[0]) / span;
  const rgb = lo[1].map((c, i) => Math.round(c + (hi[1][i] - c) * localT));
  return `rgb(${rgb.join(",")})`;
}

export default function MetricHeatmap({ towns }: { towns: Town[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm min-w-[640px]">
        <thead>
          <tr>
            <th className="text-left font-semibold text-xs uppercase tracking-wide text-(--ink-dim) pb-2 pr-2 sticky left-0 bg-(--bg)">
              Town
            </th>
            {SHORT.map((s) => (
              <th key={s} className="text-center font-semibold text-xs uppercase tracking-wide text-(--ink-dim) pb-2 px-1">
                {s}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {towns.map((t) => (
            <tr key={t.slug} className="border-t border-(--rule)">
              <td className="py-1.5 pr-2 font-medium whitespace-nowrap sticky left-0 bg-(--bg)">
                <Link href={`/towns/${t.slug}`} className="hover:text-(--accent)">
                  {t.name}
                </Link>
              </td>
              {METRICS.map((label) => {
                const m = t.nza_metrics.find((mm) => mm.label === label);
                const v = m?.value ?? 0;
                return (
                  <td key={label} className="px-1 py-1.5">
                    <div
                      className="h-7 rounded flex items-center justify-center text-[11px] font-semibold tabular"
                      style={{ background: cellColor(v), color: "#fff" }}
                      title={`${t.name} — ${label}: ${v}%`}
                    >
                      {v}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
