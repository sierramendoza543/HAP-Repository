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
      <h3 className="font-bold text-lg mb-4">{block.district}</h3>
      <dl className="flex flex-col gap-4">
        {block.facts.map((f, i) => (
          <div key={i} className="border-t border-(--rule) pt-3 first:border-t-0 first:pt-0">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <dt className="text-xs uppercase tracking-wide text-(--ink-dim) font-semibold">
                  {f.label}
                </dt>
                <dd className="font-semibold text-sm mt-0.5">{f.value}</dd>
              </div>
              <CitationBadge source={f.source} cite={f.cite} quote={f.quote} />
            </div>
            {f.quote ? (
              <blockquote className="mt-2 text-xs italic text-(--ink-dim) border-l-2 border-(--rule) pl-2.5 leading-relaxed">
                &ldquo;{f.quote}&rdquo;
              </blockquote>
            ) : (
              <p className="mt-2 text-xs text-(--ink-dim)">
                No verbatim quote independently re-verified yet &mdash; citation only.
              </p>
            )}
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

      <header className="pt-4 pb-6 border-b border-(--rule)">
        <h1 className="text-3xl font-bold mb-1">{town.name}, CT</h1>
        <p className="text-sm text-(--ink-dim)">
          Population {town.population.toLocaleString()}
          {town.land_area_acres ? ` · ${town.land_area_acres.toLocaleString()} acres` : ""}
        </p>
      </header>

      <section className="py-6 border-b border-(--rule)">
        <UpdateChecker slug={town.slug} />
        <p className="text-xs text-(--ink-dim) mt-2">Last research pass: {town.last_checked}</p>
      </section>

      <section className="py-6 border-b border-(--rule)">
        <h2 className="text-xl font-bold mb-1">Evidence We Found</h2>
        <p className="text-sm text-(--ink-dim) mb-5">
          Pulled directly from {town.name}&rsquo;s own current zoning regulations. Every value
          below carries the exact section cited and, where independently re-verified against the
          source document, the verbatim quote &mdash; click a citation to see it highlighted in
          the original PDF.
        </p>
        <div className="grid md:grid-cols-2 gap-4">
          <DistrictCard block={town.restrictive} role="restrictive" />
          <DistrictCard block={town.permissive} role="permissive" />
        </div>
        <p className="text-xs text-(--ink-dim) mt-4 bg-(--surface-2) rounded-lg p-3">
          <span className="font-semibold">Caveat:</span> {town.caveat}
        </p>
      </section>

      <details className="py-6 group">
        <summary className="cursor-pointer select-none list-none flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold inline">Check the NZA&rsquo;s Own Score &amp; Data</h2>
            <p className="text-sm text-(--ink-dim) mt-1">
              Optional: a second, independent read on {town.name}, from the National Zoning
              Atlas&rsquo;s public town-wide dataset. Different methodology, town-wide rather than
              district-specific &mdash; see the overview page for how the two relate.
            </p>
          </div>
          <span className="text-2xl text-(--ink-dim) shrink-0 ml-4 group-open:rotate-45 transition-transform">
            +
          </span>
        </summary>

        <div className="mt-5 flex items-baseline justify-between border-b border-(--rule) pb-4 mb-5">
          <span className="text-sm text-(--ink-dim)">NZA-derived composite score</span>
          <span className="font-serif text-3xl font-bold tabular">{town.composite_score.toFixed(1)}</span>
        </div>

        <div className="flex flex-col gap-3 mb-6">
          {breakdown.map((b) => (
            <div key={b.key} className="flex items-center gap-4">
              <span className="w-36 text-sm text-(--ink-dim) shrink-0">{b.label}</span>
              <span className="flex-1 h-5 rounded bg-(--surface-2) relative overflow-hidden">
                <span
                  className="absolute inset-y-0 left-0 rounded bg-(--accent) opacity-80"
                  style={{ width: `${Math.min(100, b.raw)}%` }}
                />
              </span>
              <span className="w-16 text-right text-sm tabular">{b.raw.toFixed(1)}%</span>
              <span className="w-20 text-right text-xs text-(--ink-dim)">weight {Math.round(b.weight * 100)}%</span>
            </div>
          ))}
        </div>

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

        <p className="text-xs text-(--ink-dim) mt-4">
          Composite = weighted average of the three indices above, renormalized by the weight
          actually used (0.70). NZA percentages are town-wide averages across{" "}
          {town.districts_analyzed} districts, not specific to the single restrictive/permissive
          districts in the Evidence section above.
        </p>
      </details>

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
