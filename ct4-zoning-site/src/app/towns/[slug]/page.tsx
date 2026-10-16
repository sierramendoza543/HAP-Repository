import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllSlugs, getTown, compositeBreakdown } from "@/lib/towns";
import { CitationBadge } from "@/components/CitationFact";
import UpdateChecker from "@/components/UpdateChecker";
import type { DistrictBlock } from "@/lib/types";

export function generateStaticParams() {
  return getAllSlugs().map((slug) => ({ slug }));
}

function DistrictCard({ block, role }: { block: DistrictBlock; role: "restrictive" | "permissive" }) {
  return (
    <div className="border border-(--rule) rounded-xl p-5 bg-(--surface)">
      <p className="text-xs uppercase tracking-wide font-semibold text-(--ink-dim) mb-1">
        {role === "restrictive" ? "Most restrictive district" : "Most permissive district"}
      </p>
      <h3 className="font-bold text-lg mb-3">{block.district}</h3>
      <dl className="flex flex-col gap-3">
        {block.facts.map((f, i) => (
          <div key={i} className="flex items-start justify-between gap-3 text-sm">
            <div className="min-w-0">
              <dt className="text-(--ink-dim)">{f.label}</dt>
              <dd className="font-medium">{f.value}</dd>
            </div>
            <CitationBadge source={f.source} cite={f.cite} />
          </div>
        ))}
      </dl>
    </div>
  );
}

export default async function TownPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const town = getTown(slug);
  if (!town) notFound();

  const breakdown = compositeBreakdown(town);

  return (
    <div className="px-4 max-w-4xl mx-auto w-full pb-16">
      <div className="pt-6">
        <Link href="/" className="text-sm text-(--ink-dim) hover:text-(--accent)">
          &larr; All 17 towns
        </Link>
      </div>

      <header className="pt-4 pb-6 border-b border-(--rule) flex flex-wrap items-start justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold mb-1">{town.name}, CT</h1>
          <p className="text-sm text-(--ink-dim)">
            Population {town.population.toLocaleString()}
            {town.land_area_acres ? ` · ${town.land_area_acres.toLocaleString()} acres` : ""} &middot;{" "}
            {town.districts_analyzed} districts analyzed by NZA
          </p>
        </div>
        <div className="text-right">
          <p className="font-serif text-4xl font-bold tabular">{town.composite_score.toFixed(1)}</p>
          <p className="text-xs uppercase tracking-wide text-(--ink-dim)">Composite score</p>
        </div>
      </header>

      <section className="py-6">
        <UpdateChecker slug={town.slug} />
        <p className="text-xs text-(--ink-dim) mt-2">Last research pass: {town.last_checked}</p>
      </section>

      <section className="py-6 border-t border-(--rule)">
        <h2 className="text-xl font-bold mb-4">Score Breakdown</h2>
        <div className="flex flex-col gap-3">
          {breakdown.map((b) => (
            <div key={b.key} className="flex items-center gap-4">
              <span className="w-40 text-sm text-(--ink-dim) shrink-0">{b.label}</span>
              <span className="flex-1 h-5 rounded bg-(--surface-2) relative overflow-hidden">
                <span
                  className="absolute inset-y-0 left-0 rounded bg-(--accent) opacity-80"
                  style={{ width: `${Math.min(100, b.raw)}%` }}
                />
              </span>
              <span className="w-16 text-right text-sm tabular">{b.raw.toFixed(1)}%</span>
              <span className="w-24 text-right text-xs text-(--ink-dim)">weight {Math.round(b.weight * 100)}%</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-(--ink-dim) mt-3">
          Composite = weighted average of the three indices above, renormalized by the weight
          actually used (0.70). See the methodology on the overview page for the full formula.
        </p>
      </section>

      <section className="py-6 border-t border-(--rule)">
        <h2 className="text-xl font-bold mb-4">Underlying Metrics</h2>
        <div className="grid sm:grid-cols-2 gap-3">
          {town.nza_metrics.map((m, i) => (
            <div key={i} className="flex items-center justify-between gap-3 border border-(--rule) rounded-lg px-3 py-2.5 text-sm">
              <div>
                <p className="text-(--ink-dim)">{m.label}</p>
                <p className="font-semibold tabular">
                  {m.value}
                  {m.unit.startsWith("%") ? "%" : ""}
                </p>
              </div>
              <CitationBadge source={m.source} cite={m.source.title} compact />
            </div>
          ))}
        </div>
      </section>

      <section className="py-6 border-t border-(--rule)">
        <h2 className="text-xl font-bold mb-4">District Evidence</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <DistrictCard block={town.restrictive} role="restrictive" />
          <DistrictCard block={town.permissive} role="permissive" />
        </div>
      </section>

      <section className="py-6 border-t border-(--rule)">
        <h2 className="text-lg font-bold mb-2">Caveat</h2>
        <p className="text-sm text-(--ink-dim) leading-relaxed bg-(--surface-2) rounded-lg p-4">
          {town.caveat}
        </p>
      </section>

      <section className="py-6 border-t border-(--rule) text-xs text-(--ink-dim)">
        Primary source:{" "}
        <a href={town.primary_source.url} target="_blank" rel="noopener noreferrer" className="underline hover:text-(--accent)">
          {town.primary_source.title}
        </a>
        {" · "}
        <a
          href={`https://edit.zoningatlas.org/statsrollup/jurisdiction/${town.jurisdiction_id}/`}
          target="_blank"
          rel="noopener noreferrer"
          className="underline hover:text-(--accent)"
        >
          NZA Jurisdiction Snapshot
        </a>
      </section>
    </div>
  );
}
