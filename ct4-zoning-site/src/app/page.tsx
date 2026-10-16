import Link from "next/link";
import { getAllTowns } from "@/lib/towns";
import MetricHeatmap from "@/components/MetricHeatmap";

export default function Home() {
  const towns = getAllTowns();
  const max = Math.max(...towns.map((t) => t.composite_score));
  const flagged = new Set(["Greenwich", "Bridgeport"]);

  return (
    <div className="px-4 max-w-4xl mx-auto w-full">
      <header className="pt-10 pb-6 border-b border-(--rule)">
        <p className="text-xs uppercase tracking-widest text-(--accent) font-bold mb-2">
          CT-4 Congressional District &middot; Living Scorecard
        </p>
        <h1 className="text-3xl md:text-4xl font-bold leading-tight mb-3 text-balance">
          Zoning Restrictiveness Across 17 CT-4 Towns
        </h1>
        <p className="text-(--ink-dim) max-w-2xl leading-relaxed">
          Built from each town&rsquo;s own current zoning regulations, cross-checked against the
          National Zoning Atlas. Every figure traces back to its source &mdash; click any citation
          to see the exact page.
        </p>
      </header>

      <section className="py-8">
        <h2 className="text-xl font-bold mb-1">Composite Score, Ranked</h2>
        <p className="text-sm text-(--ink-dim) mb-5">
          0 = no exclusionary rules found &middot; 100 = near-total exclusion of 2+-unit housing.
        </p>
        <div className="flex flex-col gap-1.5">
          {towns.map((t) => (
            <Link
              key={t.slug}
              href={`/towns/${t.slug}`}
              className="grid grid-cols-[110px_1fr_48px] gap-3 items-center group"
            >
              <span
                className={`text-sm truncate ${
                  flagged.has(t.name) ? "font-bold text-(--accent)" : "font-medium"
                }`}
              >
                {t.name}
                {flagged.has(t.name) ? " ★" : ""}
              </span>
              <span className="h-5 rounded bg-(--surface-2) relative overflow-hidden">
                <span
                  className="absolute inset-y-0 left-0 rounded bg-(--accent) opacity-80 group-hover:opacity-100 transition-opacity"
                  style={{ width: `${(t.composite_score / max) * 100}%` }}
                />
              </span>
              <span className="text-sm text-(--ink-dim) text-right tabular">
                {t.composite_score.toFixed(1)}
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="py-8 border-t border-(--rule)">
        <h2 className="text-xl font-bold mb-1">Metric Heatmap</h2>
        <p className="text-sm text-(--ink-dim) mb-5">
          Every underlying input to the composite score, town by town. Darker red = more
          exclusionary. Source: National Zoning Atlas Jurisdiction Snapshots.
        </p>
        <MetricHeatmap towns={towns} />
      </section>

      <footer className="py-10 text-xs text-(--ink-dim) border-t border-(--rule)">
        17 towns tracked &middot; data current as of {towns[0]?.last_checked}. Open any town to
        check it for regulation changes since the last pass.
      </footer>
    </div>
  );
}
