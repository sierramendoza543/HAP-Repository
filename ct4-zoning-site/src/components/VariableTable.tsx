"use client";

import { useState } from "react";
import type { Variable, VariableCategory } from "@/lib/types";
import SourceViewer from "./SourceViewer";

const CATEGORY_ORDER: VariableCategory[] = [
  "Use Permissions",
  "Dimensional Standards",
  "ADU Policy",
  "Parking",
  "Approval Process",
];

export default function VariableTable({ variables }: { variables: Variable[] }) {
  const [active, setActive] = useState<Variable | null>(null);

  const grouped = CATEGORY_ORDER.map((cat) => ({
    category: cat,
    rows: variables.filter((v) => v.category === cat),
  })).filter((g) => g.rows.length > 0);

  return (
    <div className="flex flex-col gap-6">
      {grouped.map((g) => (
        <div key={g.category}>
          <h3 className="text-xs uppercase tracking-wide font-semibold text-(--ink-dim) mb-2">
            {g.category} <span className="text-(--ink-faint)">({g.rows.length})</span>
          </h3>
          <div className="overflow-x-auto border border-(--rule) rounded-lg">
            <table className="w-full text-sm min-w-[560px]">
              <thead>
                <tr className="bg-(--surface-2) text-left">
                  <th className="px-3 py-2 font-semibold text-xs uppercase tracking-wide text-(--ink-dim) w-[22%]">
                    District
                  </th>
                  <th className="px-3 py-2 font-semibold text-xs uppercase tracking-wide text-(--ink-dim) w-[26%]">
                    Variable
                  </th>
                  <th className="px-3 py-2 font-semibold text-xs uppercase tracking-wide text-(--ink-dim)">
                    Value
                  </th>
                  <th className="px-3 py-2 font-semibold text-xs uppercase tracking-wide text-(--ink-dim) w-10 text-right">
                    Src
                  </th>
                </tr>
              </thead>
              <tbody>
                {g.rows.map((v, i) => (
                  <tr key={i} className="border-t border-(--rule) hover:bg-(--surface-2)">
                    <td className="px-3 py-2 text-(--ink-dim) whitespace-nowrap">{v.district}</td>
                    <td className="px-3 py-2 font-medium">{v.label}</td>
                    <td className="px-3 py-2">{v.value}</td>
                    <td className="px-3 py-2 text-right">
                      <button
                        type="button"
                        onClick={() => setActive(v)}
                        title={v.quote ? "Verified quote available" : "Citation only"}
                        className={`inline-flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold ${
                          v.quote
                            ? "bg-(--allow-bg) text-(--allow)"
                            : "bg-(--surface-2) text-(--ink-faint) border border-(--rule)"
                        }`}
                      >
                        {v.quote ? "✓" : "?"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      {active && (
        <SourceViewer
          source={active.source}
          cite={active.cite}
          quote={active.quote}
          onClose={() => setActive(null)}
        />
      )}
    </div>
  );
}
