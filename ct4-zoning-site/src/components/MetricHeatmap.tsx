import Link from "next/link";
import type { Town } from "@/lib/types";

const METRICS = [
  "2-family housing prohibited",
  "3-family housing prohibited",
  "4+-family housing prohibited",
  "1-family lots requiring ≥80,000 sq ft",
  "Residential land with a parking mandate",
];

const SHORT = ["2F excl.", "3F excl.", "4F+ excl.", "Large-lot", "Parking mand."];

function cellColor(v: number) {
  const t = Math.max(0, Math.min(100, v)) / 100;
  const stops: [number, [number, number, number]][] = [
    [0, [15, 138, 79]],
    [0.5, [180, 114, 10]],
    [1, [185, 28, 28]],
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
    <div className="overflow-x-auto border border-(--rule) rounded-lg">
      <table className="w-full border-collapse text-sm min-w-[640px]">
        <thead>
          <tr className="bg-(--surface-2)">
            <th className="text-left font-semibold text-xs uppercase tracking-wide text-(--ink-dim) px-3 py-2 sticky left-0 bg-(--surface-2)">
              Town
            </th>
            {SHORT.map((s) => (
              <th key={s} className="text-center font-semibold text-xs uppercase tracking-wide text-(--ink-dim) px-2 py-2">
                {s}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {towns.map((t) => (
            <tr key={t.slug} className="border-t border-(--rule)">
              <td className="py-1.5 px-3 font-medium whitespace-nowrap sticky left-0 bg-(--surface)">
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
