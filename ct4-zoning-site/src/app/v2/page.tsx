import Link from "next/link";
import { getAllTowns } from "@/lib/towns";
import type { V2Citation, V2District, V2Factor, Town } from "@/lib/types";
import V2CitationButton from "@/components/V2CitationButton";

type V2Town = NonNullable<Town["v2"]>;
type V2TownEntry = Town & { v2: V2Town };

export default function V2Page() {
  const towns = getAllTowns()
    .filter((t): t is V2TownEntry => Boolean(t.v2))
    .sort((a, b) => (b.v2.land_weighted_score ?? 0) - (a.v2.land_weighted_score ?? 0));

  return (
    <div className="px-4 max-w-6xl mx-auto w-full pb-16">
      <div className="pt-6">
        <Link href="/" className="text-sm text-(--ink-dim) hover:text-(--accent)">
          &larr; Overview
        </Link>
      </div>
      <header className="pt-4 pb-5 border-b border-(--rule)">
        <p className="text-xs uppercase tracking-widest text-(--accent) font-semibold mb-2">Version 2 &middot; Experimental</p>
        <h1 className="text-2xl font-bold mb-2">District-Level Restrictiveness</h1>
        <p className="text-(--ink-dim) text-sm max-w-3xl leading-relaxed">
          Each town is scored district by district using the same six-component rubric as the HAP
          score. The town figure weights each included district by its land area. Click any
          component to see its scale, the tier it received, the reason, and the quote that
          supports it.
        </p>
      </header>

      <div className="py-6 flex flex-col gap-8">
        {towns.map((t) => (
          <TownCard key={t.slug} town={t} />
        ))}
      </div>
    </div>
  );
}

function TownCard({ town }: { town: V2TownEntry }) {
  const v2 = town.v2;
  const maxAcres = Math.max(...v2.districts.map((d) => d.acres));
  const gap = v2.land_weighted_score !== null ? v2.land_weighted_score - town.composite_score : 0;
  return (
    <section className="border border-(--rule) rounded-xl bg-(--surface) p-5">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-4">
        <div>
          <h2 className="text-xl font-bold">{town.name}, CT</h2>
          <p className="text-xs text-(--ink-dim) mt-1">
            {v2.districts_included} included districts &middot; {v2.acres_included.toLocaleString()} acres
          </p>
        </div>
        <div className="text-right">
          <p className="text-[11px] uppercase tracking-wide text-(--ink-faint)">Land-weighted V2 score</p>
          <p className="text-3xl font-extrabold tabular">{v2.land_weighted_score?.toFixed(1) ?? "n/a"}</p>
          <p className="text-xs text-(--ink-dim) tabular mt-1">
            NZA proxy (town-wide estimate): <span className="font-semibold text-(--ink)">{town.composite_score.toFixed(1)}</span>
            {" "}&middot; Town HAP: {town.hap_score.composite.toFixed(1)}
          </p>
          <p className="text-[11px] text-(--ink-faint) tabular">
            V2 minus NZA proxy: {gap >= 0 ? "+" : ""}
            {gap.toFixed(1)}
          </p>
        </div>
      </div>

      <div className="text-xs text-(--ink-dim) mb-3">
        <span className="font-semibold text-(--ink)">How the town score is built:</span> {v2.formula}. Each included district
        contributes its score times its share of the included acreage.
      </div>

      <div className="flex flex-col gap-2">
        {v2.districts.map((d) => (
          <DistrictRow key={d.district} d={d} maxAcres={maxAcres} />
        ))}
      </div>
      <p className="text-xs text-(--ink-faint) mt-4">{v2.method}</p>
    </section>
  );
}

function scoreColor(score: number | null) {
  if (score === null) return "var(--ink-faint)";
  if (score >= 66) return "var(--prohibit)";
  if (score >= 33) return "var(--maybe)";
  return "var(--allow)";
}

function DistrictRow({ d, maxAcres }: { d: V2District; maxAcres: number }) {
  const color = scoreColor(d.score);
  return (
    <details className="group border border-(--rule) rounded-lg overflow-hidden">
      <summary className="cursor-pointer list-none flex items-center gap-3 px-3 py-2.5 hover:bg-(--surface-2)">
        <span className="w-20 shrink-0 text-sm font-semibold">{d.district}</span>
        <span className="flex-1 h-4 rounded bg-(--surface-2) relative overflow-hidden">
          <span className="absolute inset-y-0 left-0 rounded" style={{ width: `${(d.acres / maxAcres) * 100}%`, background: "var(--accent)", opacity: 0.35 }} />
        </span>
        <span className="w-28 text-right text-xs text-(--ink-dim) tabular shrink-0">
          {d.acres.toLocaleString()} ac{d.land_share !== null ? ` · ${d.land_share}%` : ""}
        </span>
        <span className="w-16 text-right text-sm font-bold tabular shrink-0" style={{ color }}>
          {d.score === null ? "n/a" : d.score.toFixed(1)}
        </span>
        <span className="text-(--ink-faint) text-xs group-open:rotate-90 transition-transform">&#9654;</span>
      </summary>
      <div className="px-3 pb-3 pt-2 border-t border-(--rule) bg-(--surface-2)/40">
        <div className="text-xs text-(--ink-dim) mb-2">
          <span>{d.note}</span>
          <span className="block mt-1 text-(--ink-faint)">
            Scored on {d.components_scored} of 6 components.
            {d.included
              ? d.contribution !== null
                ? ` Contributes ${d.contribution.toFixed(2)} points to the town score.`
                : ""
              : ` ${d.exclusion_reason ?? "Excluded from the town score."}`}
          </span>
        </div>
        <div className="flex flex-col gap-1.5">
          {d.factors.map((f) => (
            <FactorRow key={f.label} f={f} />
          ))}
        </div>
      </div>
    </details>
  );
}

function FactorRow({ f }: { f: V2Factor }) {
  const scored = f.points !== null;
  return (
    <details className="group/f border border-(--rule) rounded-md bg-(--surface)">
      <summary className="cursor-pointer list-none flex items-center gap-3 px-3 py-2 hover:bg-(--surface-2)">
        <span className="w-40 shrink-0 text-xs font-semibold">{f.label}</span>
        <span className="flex-1 min-w-0 text-xs text-(--ink-dim) truncate">{f.value}</span>
        <span className="text-xs font-bold tabular shrink-0" style={{ color: scoreColor(scored ? (f.points! / f.max_points) * 100 : null) }}>
          {scored ? `${f.points!.toFixed(1)} / ${f.max_points}` : "not confirmed"}
        </span>
        <span className="text-(--ink-faint) text-[10px] group-open/f:rotate-90 transition-transform">&#9654;</span>
      </summary>
      <div className="px-3 pb-3 pt-2 border-t border-(--rule) text-xs flex flex-col gap-3">
        <div>
          <p className="font-semibold mb-1">Why this score</p>
          <p className="text-(--ink-dim)">{f.reason}</p>
        </div>
        {f.scale && (
          <div>
            <p className="font-semibold mb-1">Scale for {f.label} (0 to {f.max_points})</p>
            <div className="flex flex-col gap-1">
              {f.scale.map((step) => (
                <div
                  key={step.tier}
                  className={`flex items-center gap-2 rounded px-2 py-1 ${step.active ? "bg-(--accent)/15 ring-1 ring-(--accent)" : ""}`}
                >
                  <span className="w-28 shrink-0 tabular font-semibold">{step.points} / {f.max_points}</span>
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
