import Link from "next/link";
import { getAllTowns, getNzaCompare } from "@/lib/towns";

export const metadata = {
  title: "Method and evidence | CT-4 Zoning Code Reader",
  description: "How the scores are built, how they compare with the National Zoning Atlas, and what is still open.",
};

export default function MethodPage() {
  const towns = getAllTowns();
  const compare = getNzaCompare();
  const v2Towns = towns
    .filter((t) => t.v2)
    .sort((a, b) => (b.v2!.land_weighted_score ?? 0) - (a.v2!.land_weighted_score ?? 0));

  return (
    <div className="px-4 max-w-3xl mx-auto w-full pb-16">
      <div className="pt-6">
        <Link href="/" className="text-sm text-(--ink-dim) hover:text-(--accent)">&larr; Dashboard</Link>
      </div>
      <header className="pt-4 pb-5 border-b border-(--rule)">
        <h1 className="text-2xl font-bold mb-2">Method and evidence</h1>
        <p className="text-sm text-(--ink-dim) leading-relaxed">
          What each number means, how it is built, how it compares with the National Zoning Atlas (NZA), and what is still open.
        </p>
      </header>

      <Section title="What the scores measure">
        <p>
          Every score runs from 0 (least restrictive) to 100 (most restrictive) and describes how hard a town&rsquo;s zoning code
          makes it to build housing beyond a single-family house on a large lot. There are two measures, and they are not the same
          thing.
        </p>
        <ul>
          <li>
            <b>Our score.</b> For the eight towns with district scores, each zoning district is scored on four components, and the
            town score is the average of its districts weighted by land area. Towns not yet scored by district show only the NZA
            proxy; the older town-level estimate on their pages rates a town by its single most permissive district, so it is not
            comparable and is not used in any ranking.
          </li>
          <li>
            <b>The NZA proxy.</b> NZA publishes no overall score. Our proxy is a weighted blend of three NZA snapshot figures:
            the share of residential land that prohibits 2-, 3- and 4+-family housing (30%), the share of 1-family land that
            needs 80,000 sq ft or more (25%), and the share with a parking minimum (15%), divided by 0.70.
          </li>
        </ul>
      </Section>

      <Section title="How a district is scored">
        <p>Four components, each against a fixed, published scale. Open any district on a town page to see the scale and the tier it received.</p>
        <table className="w-full text-sm border border-(--rule) rounded-lg overflow-hidden my-3">
          <thead className="bg-(--surface-2) text-left text-xs uppercase tracking-wide text-(--ink-dim)">
            <tr><th className="px-3 py-2">Component</th><th className="px-3 py-2">Max</th><th className="px-3 py-2">Most permissive</th><th className="px-3 py-2">Most restrictive</th></tr>
          </thead>
          <tbody>
            <tr className="border-t border-(--rule)"><td className="px-3 py-2">Multifamily access</td><td className="px-3 py-2">30</td><td className="px-3 py-2">By right, uncapped (6)</td><td className="px-3 py-2">No pathway (30)</td></tr>
            <tr className="border-t border-(--rule)"><td className="px-3 py-2">Approval discretion</td><td className="px-3 py-2">10</td><td className="px-3 py-2">Administrative (1)</td><td className="px-3 py-2">No pathway (10)</td></tr>
            <tr className="border-t border-(--rule)"><td className="px-3 py-2">Minimum lot size</td><td className="px-3 py-2">20</td><td className="px-3 py-2">2,500 sq ft or less (0)</td><td className="px-3 py-2">4 acres or more (20), log scale</td></tr>
            <tr className="border-t border-(--rule)"><td className="px-3 py-2">ADU pathway</td><td className="px-3 py-2">15</td><td className="px-3 py-2">By right (1)</td><td className="px-3 py-2">Prohibited (15)</td></tr>
          </tbody>
        </table>
        <p>
          The district score is the points earned divided by the points possible for the components that apply. Where a district
          already allows multi-unit buildings by right, an accessory-unit pathway adds no restriction, so that component is marked
          not applicable and left out of both sides of the fraction.
        </p>
        <p>
          <b>Why only four components.</b> Parking minimums and demolition delay are shown on every district as context but are not
          scored. Greenwich sets no numeric single-family parking minimum, and Stamford and Bridgeport have no quoted demolition-delay
          period in their codes, so scoring them would put the towns on different scales. An audit found that this one difference
          was enough to rank Stamford above Greenwich, which does not match reality; on the common four-component basis Greenwich ranks
          above Stamford, Norwalk and Bridgeport.
        </p>
      </Section>

      <Section title="Evidence">
        <p>
          Every scored district input is meant to carry a verbatim quote from the town&rsquo;s zoning code, with its section and a link that opens the
          mirrored PDF at the quote. The data build refuses to run if any quote is missing from its PDF&rsquo;s extracted text. Inputs
          that could not be read from the text are left unconfirmed, never filled in. Searches on the open web were used only to find
          the right official document.
        </p>
      </Section>

      <Section title="How our reading compares with NZA">
        <p>
          For each district-level town we recomputed NZA&rsquo;s own snapshot figures from the code and our district acreage, then ran
          the proxy formula on our numbers. This tests whether we read the codes the way NZA did, separately from the score design.
        </p>
        <table className="w-full text-sm border border-(--rule) rounded-lg overflow-hidden my-3">
          <thead className="bg-(--surface-2) text-left text-xs uppercase tracking-wide text-(--ink-dim)">
            <tr>
              <th className="px-3 py-2">Town</th>
              <th className="px-3 py-2 text-right">Our score</th>
              <th className="px-3 py-2 text-right">NZA proxy</th>
              <th className="px-3 py-2 text-right">Proxy on our readings</th>
              <th className="px-3 py-2 text-right">Difference</th>
            </tr>
          </thead>
          <tbody>
            {v2Towns.map((t) => {
              const c = compare[t.slug];
              return (
                <tr key={t.slug} className="border-t border-(--rule) tabular">
                  <td className="px-3 py-2"><Link href={`/towns/${t.slug}`} className="hover:text-(--accent)">{t.name}</Link></td>
                  <td className="px-3 py-2 text-right font-semibold">{t.v2!.land_weighted_score?.toFixed(1)}</td>
                  <td className="px-3 py-2 text-right">{t.composite_score.toFixed(1)}</td>
                  <td className="px-3 py-2 text-right">{c ? c.proxy.ours.toFixed(1) : "–"}</td>
                  <td className="px-3 py-2 text-right">{c ? `${c.proxy.difference >= 0 ? "+" : ""}${c.proxy.difference.toFixed(1)}` : "–"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <p>
          For the four towns we recomputed NZA&rsquo;s own figures for (Stamford, Greenwich, Norwalk and Bridgeport), our readings of the codes give a 
          proxy within 5.5 points of NZA&rsquo;s. Across all eight district towns our score sits above the proxy in five and below it in three
          (Easton, Greenwich and Fairfield). That is expected: our score rates each district&rsquo;s rules, including the approval process and
          the accessory-unit pathway, while the proxy counts the share of land with certain features.
        </p>
      </Section>

      <Section title="What is still open">
        <ul>
          <li>
            <b>Towns without district scores.</b> {towns.length - v2Towns.length} towns show the NZA proxy only. Wilton and Stratford need their
            zoning PDFs mirrored; Westport has no mirrored code and no open district map; Darien, New Canaan, Redding, Ridgefield, Shelton and Weston
            have code on file but no open district-acreage source yet (Shelton&rsquo;s code is also an image-only scan).
          </li>
          <li>
            <b>Districts left out of the score.</b> A district is scored only when all four components are confirmed from quoted text. Floating
            and overlay districts whose &ldquo;lot size&rdquo; is only the minimum area needed to create them (for example Monroe&rsquo;s MFR and Stamford&rsquo;s
            SRD districts), and districts whose accessory-unit rule would have to be inferred, are listed on each town page as excluded, with the reason.
          </li>
          <li>
            <b>Code editions.</b> Stamford&rsquo;s 2025 text amendments and Greenwich&rsquo;s 2026 amendments (including the state parking
            limits effective July 1, 2026) are not yet read; the mirrored text is Stamford July 2024 and Greenwich August 2023.
          </li>
          <li>
            <b>Norwalk.</b> Four multifamily districts (CD-3W, CD-3C, CD-4, CD-4W) lack confirmed acreage, and the district layer predates the 2024 rewrite.
          </li>
          <li>
            <b>NZA inputs.</b> Greenwich&rsquo;s stored NZA inputs differ from NZA&rsquo;s live page; its proxy recomputed from the live page is{" "}
            {compare.greenwich?.proxy.nza_live.toFixed(1)}.
          </li>
          <li>
            <b>Maps.</b> Outlines are public-domain Census boundaries. District polygons come from the CT Zoning Atlas (2022) and the City of
            Bridgeport GIS Hub; the reuse terms of both are being confirmed. Norwalk&rsquo;s polygons use the pre-rewrite map with a crosswalk.
          </li>
        </ul>
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="py-6 border-b border-(--rule) text-sm leading-relaxed text-(--ink-dim) [&_b]:text-(--ink) [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:flex [&_ul]:flex-col [&_ul]:gap-2 [&_p]:mb-3">
      <h2 className="text-base font-semibold text-(--ink) mb-2">{title}</h2>
      {children}
    </section>
  );
}
