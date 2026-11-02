import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import { getAllTowns, getDashboardRows, getNzaCompare } from "@/lib/towns";
import CtMap, { type GeoCollection, type MapDistrictScore, type MapTown } from "@/components/CtMap";
import DashboardTable from "@/components/DashboardTable";
import {
  AgreementChart,
  ComponentHeatmap,
  LandByScore,
  NzaCheck,
  NzaHeatmap,
  ScoreBars,
} from "@/components/DashboardCharts";

export default function Home() {
  const towns = getAllTowns();
  const rows = getDashboardRows();
  const compare = getNzaCompare();
  const v2Towns = towns
    .filter((t) => t.v2)
    .sort((a, b) => (b.v2!.land_weighted_score ?? 0) - (a.v2!.land_weighted_score ?? 0));

  const townGeo = JSON.parse(
    fs.readFileSync(path.join(process.cwd(), "public", "data", "ct4-towns.geojson"), "utf-8"),
  ) as GeoCollection;

  const mapTowns: MapTown[] = rows.map((r) => ({
    slug: r.slug,
    name: r.name,
    headline: r.headline,
    basis: r.basis,
    nzaProxy: r.nzaProxy,
    gap: r.gap,
    pct2: r.nza.pct2,
    pct3: r.nza.pct3,
    pct4: r.nza.pct4,
    lot80: r.nza.lot80,
    parking: r.nza.parking,
    hasDistricts: fs.existsSync(path.join(process.cwd(), "public", "data", "districts", `${r.slug}.geojson`)),
  }));
  const districtScores: Record<string, Record<string, MapDistrictScore>> = {};
  for (const t of v2Towns) {
    districtScores[t.slug] = Object.fromEntries(
      t.v2!.districts.map((d) => [d.district, { score: d.score, acres: d.acres, included: d.included }]),
    );
  }

  const names = Object.fromEntries(towns.map((t) => [t.slug, t.name]));
  const totalVariables = towns.reduce((s, t) => s + t.variables.length, 0);
  const districtsScored = v2Towns.reduce((s, t) => s + t.v2!.districts_included, 0);
  const acresScored = v2Towns.reduce((s, t) => s + t.v2!.acres_included, 0);
  const scoredRows = rows.filter((r) => r.headline !== null);
  const most = scoredRows[0];
  const least = scoredRows[scoredRows.length - 1];
  const nzaCheckNames = Object.fromEntries(Object.keys(compare).map((s) => [s, names[s]]));

  return (
    <div className="px-4 max-w-6xl mx-auto w-full pb-16">
      <header className="pt-8 pb-5 border-b border-(--rule)">
        <p className="text-xs uppercase tracking-widest text-(--accent) font-semibold mb-2">
          CT-4 Congressional District &middot; Zoning Code Reader
        </p>
        <h1 className="text-2xl md:text-3xl font-bold leading-tight mb-2 text-balance">
          How restrictive is the zoning in each CT-4 town?
        </h1>
        <p className="text-(--ink-dim) max-w-3xl leading-relaxed text-sm">
          We read each town&rsquo;s own zoning code, score it district by district, weight the districts by land
          area, and set every result beside the National Zoning Atlas (NZA). Every input links to a quoted passage
          you can open in the source PDF. Scores run from 0 (least restrictive) to 100 (most restrictive).
        </p>
      </header>

      <section className="py-5 border-b border-(--rule) grid grid-cols-2 md:grid-cols-6 gap-3" aria-label="Summary figures">
        <Kpi label="Towns" value={String(towns.length)} />
        <Kpi label="Scored by district" value={String(v2Towns.length)} sub={`${districtsScored} districts`} />
        <Kpi label="Land scored by district" value={`${Math.round(acresScored).toLocaleString()} ac`} />
        <Kpi label="Variables tracked" value={String(totalVariables)} />
        <Kpi label="Most restrictive (scored)" value={most?.name ?? "n/a"} sub={most?.headline?.toFixed(1)} />
        <Kpi label="Least restrictive (scored)" value={least?.name ?? "n/a"} sub={least?.headline?.toFixed(1)} />
      </section>
      <p className="text-xs text-(--ink-faint) pt-2">
        These figures are computed from the data below, not independent facts. {towns.length - v2Towns.length} towns
        show only the NZA proxy until their district maps and codes are read in full.
      </p>

      <section className="py-5 border-b border-(--rule)">
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div className="rounded-lg border border-(--rule) bg-(--surface) p-4">
            <h2 className="text-sm font-semibold mb-1">Our score</h2>
            <p className="text-xs text-(--ink-dim) leading-relaxed">
              For district-level towns, the land-weighted average of each district&rsquo;s score on four components we can
              document in every town: how much multifamily housing is allowed, how it is approved, minimum lot size, and the
              accessory-unit pathway. Towns not yet scored by district show only the NZA proxy.
            </p>
          </div>
          <div className="rounded-lg border border-(--rule) bg-(--surface) p-4">
            <h2 className="text-sm font-semibold mb-1">NZA proxy</h2>
            <p className="text-xs text-(--ink-dim) leading-relaxed">
              NZA publishes no overall score. The proxy is our blend of three of its snapshot figures: how much land prohibits
              2-, 3- and 4+-family housing, how much needs very large lots, and how much has a parking minimum. It is shown
              next to every score so the two can be checked against each other.
            </p>
          </div>
        </div>
      </section>

      <section className="py-6 border-b border-(--rule)" aria-labelledby="map-h">
        <h2 id="map-h" className="text-base font-semibold mb-1">Map</h2>
        <p className="text-xs text-(--ink-dim) mb-3 max-w-3xl">
          Switch the measure, select a town, then open its districts (eight towns have district scores) to see
          every zoning district colored by its score.
        </p>
        <CtMap townGeo={townGeo} towns={mapTowns} districtScores={districtScores} />
      </section>

      <section className="py-6 border-b border-(--rule)">
        <h2 className="text-base font-semibold mb-1">All towns</h2>
        <p className="text-xs text-(--ink-dim) mb-4">
          Sortable and filterable. Our score appears beside the NZA proxy and each NZA figure; click a town for its
          districts, evidence and the full comparison.
        </p>
        <DashboardTable rows={rows} />
      </section>

      <section className="py-6 border-b border-(--rule) grid lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-base font-semibold mb-1">Our score vs the NZA proxy</h2>
          <p className="text-xs text-(--ink-dim) mb-3">
            Each dot is a district-scored town. Dots on the dashed line agree exactly; dots above it are towns we score as more
            restrictive than the proxy.
          </p>
          <AgreementChart rows={scoredRows} />
        </div>
        <div>
          <h2 className="text-base font-semibold mb-1">Every town, ranked</h2>
          <p className="text-xs text-(--ink-dim) mb-3">Our score (colored bar) against the NZA proxy (gray bar); towns without district scores show the proxy only.</p>
          <ScoreBars rows={rows} />
        </div>
      </section>

      <section className="py-6 border-b border-(--rule)">
        <h2 className="text-base font-semibold mb-1">Where the restrictive land is</h2>
        <p className="text-xs text-(--ink-dim) mb-4 max-w-3xl">
          Each bar is one town&rsquo;s scored land, split into its zoning districts. A town that is mostly large-lot
          single-family land is mostly red; one with dense downtown districts shows a green stretch.
        </p>
        <LandByScore towns={v2Towns} />
      </section>

      <section className="py-6 border-b border-(--rule) grid lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-base font-semibold mb-1">Our four components, by town</h2>
          <p className="text-xs text-(--ink-dim) mb-3">Which rules drive each town&rsquo;s score.</p>
          <ComponentHeatmap rows={rows} />
        </div>
        <div>
          <h2 className="text-base font-semibold mb-1">NZA snapshot figures, all towns</h2>
          <p className="text-xs text-(--ink-dim) mb-3">The inputs behind the NZA proxy.</p>
          <NzaHeatmap rows={rows} />
        </div>
      </section>

      <section className="py-6 border-b border-(--rule)">
        <h2 className="text-base font-semibold mb-1">Does our reading of the codes match NZA&rsquo;s?</h2>
        <p className="text-xs text-(--ink-dim) mb-4 max-w-3xl">
          For the four towns with district maps we recomputed NZA&rsquo;s own figures from the zoning codes and ran its formula
          on our numbers. Gray bars are NZA&rsquo;s figures; blue bars are ours.
        </p>
        <NzaCheck compare={compare} names={nzaCheckNames} />
      </section>

      <footer className="py-8 text-xs text-(--ink-dim) flex flex-col gap-2">
        <p>
          <Link href="/method" className="underline hover:text-(--accent)">How the scores are built, what they mean, and what is still open</Link>
        </p>
        <p className="text-(--ink-faint)">
          Data current as of {towns[0]?.last_checked}. Town outlines: US Census Bureau cartographic boundaries (public domain).
          District polygons: CT Zoning Atlas (DesegregateCT / CT Data Collaborative, 2022) for Stamford, Greenwich and Norwalk,
          and the City of Bridgeport GIS Hub for Bridgeport; terms of reuse are being confirmed.
        </p>
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
