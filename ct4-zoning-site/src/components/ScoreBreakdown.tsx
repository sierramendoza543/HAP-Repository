"use client";

import { useState } from "react";
import type { HapScoreFactor } from "@/lib/types";

function sevColor(frac: number) {
  if (frac >= 0.66) return "var(--prohibit)";
  if (frac >= 0.33) return "var(--maybe)";
  return "var(--allow)";
}

export default function ScoreBreakdown({ factors }: { factors: HapScoreFactor[] }) {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  return (
    <div className="flex flex-col gap-2">
      {factors.map((f, i) => {
        const unscored = f.points === null;
        const frac = unscored ? 0 : f.max_points ? f.points! / f.max_points : 0;
        const color = unscored ? "var(--ink-faint)" : sevColor(frac);
        const open = openIdx === i;
        return (
          <div
            key={f.label}
            className={`border rounded-lg overflow-hidden bg-(--surface) ${unscored ? "border-dashed border-(--rule-strong) opacity-70" : "border-(--rule)"}`}
          >
            <button
              onClick={() => setOpenIdx(open ? null : i)}
              className="w-full flex items-center gap-3 px-3.5 py-2.5 text-left hover:bg-(--surface-2) transition-colors"
            >
              <span className="w-[136px] shrink-0">
                <span className="block text-sm font-semibold leading-tight">{f.label}</span>
                <span className="block text-[10px] uppercase tracking-wide text-(--ink-faint)">{f.category}</span>
              </span>
              <span className="flex-1 h-5 rounded bg-(--surface-2) relative overflow-hidden">
                {unscored ? (
                  <span className="absolute inset-0 flex items-center px-2 text-[10px] text-(--ink-faint) italic">
                    excluded — not independently confirmed for this town
                  </span>
                ) : (
                  <span
                    className="absolute inset-y-0 left-0 rounded transition-[width]"
                    style={{ width: `${Math.max(2, frac * 100)}%`, background: color }}
                  />
                )}
              </span>
              <span className="w-20 text-right text-sm tabular font-bold shrink-0" style={{ color }}>
                {unscored ? "n/a" : `+${f.points!.toFixed(1)}`}
              </span>
              <span className="w-12 text-right text-[11px] text-(--ink-faint) tabular shrink-0">/{f.max_points}</span>
              <span className={`text-(--ink-faint) shrink-0 transition-transform text-xs ${open ? "rotate-90" : ""}`}>
                &#9654;
              </span>
            </button>
            {open && (
              <div className="px-3.5 pb-3.5 pt-0.5 border-t border-(--rule) bg-(--surface-2)/40">
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mb-1.5 mt-2.5">
                  <span className="text-xs">
                    <span className="text-(--ink-faint)">Rubric tier:</span>{" "}
                    <span className="font-semibold capitalize">{f.tier.replace(/_/g, " ")}</span>
                  </span>
                  <span className="text-xs">
                    <span className="text-(--ink-faint)">Input:</span>{" "}
                    <span className="font-semibold">{f.input_value}</span>
                  </span>
                </div>
                <p className="text-xs text-(--ink-dim) leading-relaxed">{f.note}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
