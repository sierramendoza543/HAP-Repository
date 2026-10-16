import { getAllTowns } from "@/lib/towns";
import MetricHeatmap from "@/components/MetricHeatmap";
import OverviewTable from "@/components/OverviewTable";
import ScoreScatter from "@/components/ScoreScatter";

export default function Home() {
  const towns = getAllTowns();
  const totalVariables = towns.reduce((s, t) => s + t.variables.length, 0);
  const avgScore = towns.reduce((s, t) => s + t.composite_score, 0) / towns.length;
  const mostRestrictive = towns[0];
  const leastRestrictive = towns[towns.length - 1];

  return (
    <div className="px-4 max-w-6xl mx-auto w-full">
      <header className="pt-8 pb-5 border-b border-(--rule)">
        <p className="text-xs uppercase tracking-widest text-(--accent) font-semibold mb-2">
          CT-4 Congressional District &middot; Living Scorecard
        </p>
        <h1 className="text-2xl md:text-3xl font-bold leading-tight mb-2 text-balance">
          Zoning Restrictiveness Monitor
        </h1>
        <p className="text-(--ink-dim) max-w-2xl leading-relaxed text-sm">
          {totalVariables} tracked variables across {towns.length} towns, pulled from each
          town&rsquo;s own current zoning regulations and cross-checked against the National
          Zoning Atlas. Every figure traces back to its source.
        </p>
      </header>

      <section className="py-5 border-b border-(--rule) grid grid-cols-2 md:grid-cols-5 gap-4">
        <Kpi label="Towns tracked" value={String(towns.length)} />
        <Kpi label="Variables tracked" value={String(totalVariables)} />
        <Kpi label="Avg. composite score" value={avgScore.toFixed(1)} />
        <Kpi label="Most restrictive" value={mostRestrictive.name} sub={mostRestrictive.composite_score.toFixed(1)} />
        <Kpi label="Least restrictive" value={leastRestrictive.name} sub={leastRestrictive.composite_score.toFixed(1)} />
      </section>
      <p className="text-xs text-(--ink-dim) pt-2">
        These five figures are computed directly from the per-town data below &mdash; not
        independent facts, so no separate citation applies to them.
      </p>

      <section className="py-6 border-b border-(--rule)">
        <h2 className="text-base font-semibold mb-1">All Towns</h2>
        <p className="text-xs text-(--ink-dim) mb-4">
          Sortable, filterable. Click a row to open that town&rsquo;s full variable table and
          source citations.
        </p>
        <OverviewTable towns={towns} />
        <p className="text-xs text-(--ink-dim) mt-2">
          Population and the five metric columns: National Zoning Atlas Jurisdiction Snapshots
          (cited per-number on each town&rsquo;s page). Score: our own formula over those cited
          metrics &mdash; see a town&rsquo;s page for the exact weights.
        </p>
      </section>

      <section className="py-6 border-b border-(--rule) grid lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-base font-semibold mb-1">Population vs. Composite Score</h2>
          <p className="text-xs text-(--ink-dim) mb-3">
            Hover a point for the town; click to open it. Color follows the score band.
          </p>
          <ScoreScatter towns={towns} />
          <p className="text-xs text-(--ink-dim) mt-2">
            Population &amp; score source: see table above.
          </p>
        </div>
        <div>
          <h2 className="text-base font-semibold mb-1">Metric Heatmap</h2>
          <p className="text-xs text-(--ink-dim) mb-3">
            Every input to the composite score, town by town. Darker red = more exclusionary.
          </p>
          <MetricHeatmap towns={towns} />
          <p className="text-xs text-(--ink-dim) mt-2">
            Source: National Zoning Atlas Jurisdiction Snapshots &mdash; click a town name for the
            per-number citation.
          </p>
        </div>
      </section>

      <footer className="py-8 text-xs text-(--ink-dim)">
        Data current as of {towns[0]?.last_checked}. Open any town to check it for regulation
        changes since the last research pass.
      </footer>
    </div>
  );
}

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="border border-(--rule) rounded-lg px-3 py-2.5 bg-(--surface)">
      <p className="text-[11px] uppercase tracking-wide text-(--ink-faint) mb-1">{label}</p>
      <p className="text-lg font-bold tabular leading-tight">{value}</p>
      {sub && <p className="text-xs text-(--ink-dim) tabular">{sub}</p>}
    </div>
  );
}
