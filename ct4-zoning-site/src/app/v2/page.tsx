import Link from "next/link";
import { getAllTowns } from "@/lib/towns";
import type { V2District, Town } from "@/lib/types";
import V2CitationButton from "@/components/V2CitationButton";

export default function V2Page() {
  const towns = getAllTowns()
    .filter((t): t is Town & { v2: NonNullable<Town["v2"]> } => Boolean(t.v2))
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
          score. The town figure weights each district by its land area, so a district covering
          more residential land counts for more. Only residential districts are included; commercial
          and mixed-use districts are excluded.
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

function TownCard({ town }: { town: Town & { v2: NonNullable<Town["v2"]> } }) {
  const v2 = town.v2;
  const maxAcres = Math.max(...v2.districts.map((d) => d.acres));
  return (
    <section className="border border-(--rule) rounded-xl bg-(--surface) p-5">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-4">
        <div>
          <h2 className="text-xl font-bold">{town.name}, CT</h2>
          <p className="text-xs text-(--ink-dim) mt-1">
            {v2.districts_included} residential districts &middot; {v2.acres_included.toLocaleString()} acres
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
            V2 vs NZA proxy: {(v2.land_weighted_score !== null ? v2.land_weighted_score - town.composite_score : 0) >= 0 ? "+" : ""}
            {(v2.land_weighted_score !== null ? v2.land_weighted_score - town.composite_score : 0).toFixed(1)}
          </p>
        </div>
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

function DistrictRow({ d, maxAcres }: { d: V2District; maxAcres: number }) {
  const color = d.score === null ? "var(--ink-faint)" : d.score >= 66 ? "var(--prohibit)" : d.score >= 33 ? "var(--maybe)" : "var(--allow)";
  return (
    <details className="group border border-(--rule) rounded-lg overflow-hidden">
      <summary className="cursor-pointer list-none flex items-center gap-3 px-3 py-2.5 hover:bg-(--surface-2)">
        <span className="w-20 shrink-0 text-sm font-semibold">{d.district}</span>
        <span className="flex-1 h-4 rounded bg-(--surface-2) relative overflow-hidden">
          <span className="absolute inset-y-0 left-0 rounded" style={{ width: `${(d.acres / maxAcres) * 100}%`, background: "var(--accent)", opacity: 0.35 }} />
        </span>
        <span className="w-24 text-right text-xs text-(--ink-dim) tabular shrink-0">
          {d.acres.toLocaleString()} ac{d.land_share !== null ? ` · ${d.land_share}%` : ""}
        </span>
        <span className="w-16 text-right text-sm font-bold tabular shrink-0" style={{ color }}>
          {d.score === null ? "n/a" : d.score.toFixed(1)}
        </span>
        <span className="text-(--ink-faint) text-xs group-open:rotate-90 transition-transform">&#9654;</span>
      </summary>
      <div className="px-3 pb-3 pt-2 border-t border-(--rule) bg-(--surface-2)/40">
        <p className="text-xs text-(--ink-dim) mb-2">
          {d.note}
          <span className="block mt-1 text-(--ink-faint)">
            Scored on {d.components_scored} of 6 components.
            {d.included ? "" : " Excluded from the town score: fewer than 5 components are confirmed."}
          </span>
        </p>
        {d.citations.length > 0 && (
          <div className="mb-3 flex flex-col gap-2">
            {d.citations.map((c) => (
              <div key={`${c.field}-${c.cite}`} className="text-xs border-l-2 border-(--accent) pl-3">
                <p className="font-semibold">
                  {c.field.replace("_", " ")} &middot; {c.cite}
                </p>
                <p className="italic text-(--ink-dim)">&ldquo;{c.quote}&rdquo;</p>
                <div className="mt-0.5 flex flex-wrap gap-x-2">
                  <V2CitationButton
                    source={{ kind: "pdf", id: c.file, url: c.url, title: c.source_title, file: c.file }}
                    cite={c.cite}
                    quote={c.quote}
                  />
                  <span aria-hidden>·</span>
                  <a href={c.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-(--accent)">
                    {c.source_title}
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="grid sm:grid-cols-2 gap-x-6 gap-y-1">
          {d.factors.map((f) => (
            <div key={f.label} className="flex justify-between text-xs border-b border-(--rule) py-1">
              <span className="text-(--ink-dim)">{f.label}</span>
              <span className="tabular font-semibold">
                {f.points === null ? "not confirmed" : `${f.points.toFixed(1)} / ${f.max_points}`}
              </span>
            </div>
          ))}
        </div>
      </div>
    </details>
  );
}
