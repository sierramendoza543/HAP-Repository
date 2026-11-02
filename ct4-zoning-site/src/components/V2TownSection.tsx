import type { NzaCompare, Town, V2Citation, V2District, V2Factor } from "@/lib/types";
import V2CitationButton from "@/components/V2CitationButton";

type V2Town = NonNullable<Town["v2"]>;

export function scoreColor(score: number | null) {
  if (score === null) return "var(--ink-faint)";
  if (score >= 66) return "var(--prohibit)";
  if (score >= 33) return "var(--maybe)";
  return "var(--allow)";
}

function pct(n: number) {
  return `${n.toFixed(1)}%`;
}

// What the National Zoning Atlas reports for the same idea, next to what we recomputed from the code.
function nzaNote(town: Town, compare: NzaCompare | undefined, label: string): string {
  const metric = (needle: string) => town.nza_metrics.find((m) => m.label.includes(needle))?.value;
  const p2 = metric("2-family");
  const p3 = metric("3-family");
  const p4 = metric("4+-family");
  const lot80 = metric("≥80,000");
  const parking = metric("parking mandate");
  switch (label) {
    case "Multifamily Access": {
      const nza = `NZA (town-wide, all residential land): 2-family prohibited ${p2}%, 3-family ${p3}%, 4+-family ${p4}%.`;
      if (!compare) return nza;
      const o = compare.prohibited;
      return `${nza} Recomputed from the code: ${pct(o["2-family"].ours)} / ${pct(o["3-family"].ours)} / ${pct(o["4+-family"].ours)}.`;
    }
    case "Approval Discretion": {
      if (!compare) return "NZA has no approval-process measure; it records only whether a use is allowed as of right, after a public hearing, or prohibited.";
      const h = compare.hearing;
      return `NZA records land where housing "may be allowed after a public hearing": 2-family ${pct(h["2-family"].nza)}, 3-family ${pct(h["3-family"].nza)}, 4+-family ${pct(h["4+-family"].nza)} (recomputed from the code: ${pct(h["2-family"].ours)} / ${pct(h["3-family"].ours)} / ${pct(h["4+-family"].ours)}).`;
    }
    case "Minimum Lot Size":
      return compare
        ? `NZA: ${lot80}% of 1-family land needs a minimum lot of 80,000 sq ft or more. Recomputed from the code: ${pct(compare.lot80.ours)}.`
        : `NZA: ${lot80}% of 1-family land needs a minimum lot of 80,000 sq ft or more.`;
    case "ADU Approval Pathway":
      return compare
        ? `NZA: ${compare.adu.nza}. Our reading of the code: ${compare.adu.ours}.`
        : "NZA records accessory dwelling units as allowed, allowed with occupancy limits, hearing, or prohibited, as a share of 1-family land.";
    case "Parking Mandate":
      return compare
        ? `NZA: ${parking}% of residential land has a parking minimum. Recomputed from the code: ${pct(compare.parking.ours)}. Parking is shown for context and is not part of the cross-town score.`
        : `NZA: ${parking}% of residential land has a parking minimum. Parking is shown for context and is not part of the cross-town score.`;
    default:
      return "NZA does not measure demolition delay. It is shown for context and is not part of the cross-town score.";
  }
}

export default function V2TownSection({ town, compare }: { town: Town; compare?: NzaCompare }) {
  const v2 = town.v2 as V2Town;
  const maxAcres = Math.max(...v2.districts.map((d) => d.acres));
  const score = v2.land_weighted_score;
  const gap = score !== null ? score - town.composite_score : 0;
  return (
    <section>
      <div className="flex flex-wrap items-end justify-between gap-4 mb-3">
        <div>
          <h2 className="text-base font-semibold">District-level score</h2>
          <p className="text-xs text-(--ink-dim) mt-1 max-w-2xl">
            Each district is scored on four components that every town in this study can document, then weighted by
            land area. Open a district to see each component&rsquo;s scale, the tier it received, the reason, and the
            quoted code text, plus what the National Zoning Atlas reports for the same idea.
          </p>
        </div>
        <div className="text-right">
          <p className="text-[11px] uppercase tracking-wide text-(--ink-faint)">Land-weighted V2 score</p>
          <p className="text-3xl font-extrabold tabular" style={{ color: scoreColor(score) }}>
            {score?.toFixed(1) ?? "n/a"}
          </p>
          <p className="text-xs text-(--ink-dim) tabular mt-1">
            NZA-derived proxy: <span className="font-semibold text-(--ink)">{town.composite_score.toFixed(1)}</span>
            {" "}&middot; V2 minus NZA proxy {gap >= 0 ? "+" : ""}
            {gap.toFixed(1)}
          </p>
        </div>
      </div>
      <p className="text-xs text-(--ink-dim) mb-3">
        <span className="font-semibold text-(--ink)">Formula:</span> {v2.formula}. {v2.districts_included} of{" "}
        {v2.districts.length} districts included &middot; {v2.acres_included.toLocaleString()} acres.
      </p>
      <div className="flex flex-col gap-2">
        {v2.districts.map((d) => (
          <DistrictRow key={d.district} d={d} maxAcres={maxAcres} town={town} compare={compare} />
        ))}
      </div>
      <p className="text-xs text-(--ink-faint) mt-4">{v2.method}</p>
    </section>
  );
}

function DistrictRow({ d, maxAcres, town, compare }: { d: V2District; maxAcres: number; town: Town; compare?: NzaCompare }) {
  const color = scoreColor(d.score);
  return (
    <details className="group border border-(--rule) rounded-lg overflow-hidden bg-(--surface)">
      <summary className="cursor-pointer list-none flex items-center gap-3 px-3 py-2.5 hover:bg-(--surface-2)">
        <span className="w-20 shrink-0 text-sm font-semibold">{d.district}</span>
        <span className="flex-1 h-4 rounded bg-(--surface-2) relative overflow-hidden" aria-hidden>
          <span
            className="absolute inset-y-0 left-0 rounded"
            style={{ width: `${(d.acres / maxAcres) * 100}%`, background: "var(--accent)", opacity: 0.35 }}
          />
        </span>
        <span className="w-28 text-right text-xs text-(--ink-dim) tabular shrink-0">
          {d.acres.toLocaleString()} ac{d.land_share !== null ? ` · ${d.land_share}%` : ""}
        </span>
        {!d.included && (
          <span className="shrink-0 text-[10px] uppercase tracking-wide px-1.5 py-0.5 rounded bg-(--surface-2) text-(--ink-dim)">
            excluded
          </span>
        )}
        <span
          className="w-16 text-right text-sm font-bold tabular shrink-0"
          style={{ color: d.included ? color : "var(--ink-faint)" }}
        >
          {d.score === null ? "n/a" : d.score.toFixed(1)}
        </span>
        <span className="text-(--ink-faint) text-xs group-open:rotate-90 transition-transform" aria-hidden>
          &#9654;
        </span>
      </summary>
      <div className="px-3 pb-3 pt-2 border-t border-(--rule) bg-(--surface-2)/40">
        <div className="text-xs text-(--ink-dim) mb-2">
          <span>{d.note}</span>
          <span className="block mt-1 text-(--ink-faint)">
            {d.components_scored} of 4 scored components
            {d.components_confirmed > d.components_scored
              ? ` (plus ${d.components_confirmed - d.components_scored} marked not applicable)`
              : ""}
            .
            {d.included
              ? d.contribution !== null
                ? ` Contributes ${d.contribution.toFixed(2)} points to the town score.`
                : ""
              : ` ${d.exclusion_reason ?? "Excluded from the town score."}`}
          </span>
        </div>
        <div className="flex flex-col gap-1.5">
          {d.factors.map((f) => (
            <FactorRow key={f.label} f={f} nza={nzaNote(town, compare, f.label)} />
          ))}
        </div>
      </div>
    </details>
  );
}

function FactorRow({ f, nza }: { f: V2Factor; nza: string }) {
  const scored = f.points !== null;
  return (
    <details className="group/f border border-(--rule) rounded-md bg-(--surface)">
      <summary className="cursor-pointer list-none flex items-center gap-3 px-3 py-2 hover:bg-(--surface-2)">
        <span className="w-40 shrink-0 text-xs font-semibold">{f.label}</span>
        <span className="flex-1 min-w-0 text-xs text-(--ink-dim) truncate">{f.value}</span>
        {!f.in_score && (
          <span className="text-[10px] uppercase tracking-wide text-(--ink-faint) shrink-0">context only</span>
        )}
        <span
          className="text-xs font-bold tabular shrink-0"
          style={{ color: f.in_score ? scoreColor(scored ? (f.points! / f.max_points) * 100 : null) : "var(--ink-faint)" }}
        >
          {scored ? `${f.points!.toFixed(1)} / ${f.max_points}` : f.value === "Not applicable" ? "n/a" : "not confirmed"}
        </span>
        <span className="text-(--ink-faint) text-[10px] group-open/f:rotate-90 transition-transform" aria-hidden>
          &#9654;
        </span>
      </summary>
      <div className="px-3 pb-3 pt-2 border-t border-(--rule) text-xs flex flex-col gap-3">
        <div>
          <p className="font-semibold mb-1">Why this score</p>
          <p className="text-(--ink-dim)">{f.reason}</p>
        </div>
        {f.scale && (
          <div>
            <p className="font-semibold mb-1">
              Scale for {f.label} (0 to {f.max_points})
            </p>
            <div className="flex flex-col gap-1">
              {f.scale.map((step) => (
                <div
                  key={step.tier}
                  className={`flex items-center gap-2 rounded px-2 py-1 ${step.active ? "bg-(--accent)/15 ring-1 ring-(--accent)" : ""}`}
                >
                  <span className="w-20 shrink-0 tabular font-semibold">
                    {step.points} / {f.max_points}
                  </span>
                  <span className="w-44 shrink-0 font-semibold">{step.label}</span>
                  <span className="flex-1 text-(--ink-dim)">{step.meaning}</span>
                  {step.active && <span className="text-(--accent) font-semibold shrink-0">this district</span>}
                </div>
              ))}
            </div>
          </div>
        )}
        {f.scale === null && <p className="text-(--ink-dim)">{f.scale_note}</p>}
        <div>
          <p className="font-semibold mb-1">Evidence</p>
          <EvidenceLine ev={f.evidence} />
        </div>
        <div className="rounded-md bg-(--surface-2) px-3 py-2">
          <p className="font-semibold mb-0.5">National Zoning Atlas comparison</p>
          <p className="text-(--ink-dim)">{nza}</p>
        </div>
      </div>
    </details>
  );
}

function EvidenceLine({ ev }: { ev: V2Citation | null }) {
  if (!ev) {
    return <p className="text-(--ink-faint) italic">No verbatim quote is linked to this input yet.</p>;
  }
  return (
    <div className="border-l-2 border-(--accent) pl-3">
      <p className="font-semibold">{ev.cite}</p>
      <p className="italic text-(--ink-dim)">&ldquo;{ev.quote}&rdquo;</p>
      <div className="mt-1 flex flex-wrap gap-x-2">
        <V2CitationButton
          source={{ kind: "pdf", id: ev.file, url: ev.url, title: ev.source_title, file: ev.file }}
          cite={ev.cite}
          quote={ev.quote}
        />
        <span aria-hidden>·</span>
        <a href={ev.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-(--accent)">
          {ev.source_title}
        </a>
      </div>
    </div>
  );
}
