import type { NzaCompare, NzaFamily } from "@/lib/types";

const FAMILIES: NzaFamily[] = ["1-family", "2-family", "3-family", "4+-family"];

function Row({ label, nza, ours, suffix = "%" }: { label: string; nza: number; ours: number; suffix?: string }) {
  const diff = Math.round((ours - nza) * 10) / 10;
  const big = Math.abs(diff) >= 5;
  return (
    <tr className="border-t border-(--rule)">
      <td className="px-3 py-1.5">{label}</td>
      <td className="px-3 py-1.5 tabular text-right">{nza.toFixed(1)}{suffix}</td>
      <td className="px-3 py-1.5 tabular text-right font-semibold">{ours.toFixed(1)}{suffix}</td>
      <td className={`px-3 py-1.5 tabular text-right ${big ? "text-(--maybe) font-semibold" : "text-(--ink-dim)"}`}>
        {diff >= 0 ? "+" : ""}
        {diff.toFixed(1)}
      </td>
    </tr>
  );
}

// Our recomputation of the National Zoning Atlas snapshot, figure by figure, next to NZA's own numbers.
export default function NzaComparePanel({ townName, compare }: { townName: string; compare: NzaCompare }) {
  const p = compare.proxy;
  return (
    <section>
      <h2 className="text-base font-semibold mb-1">How our reading compares with the National Zoning Atlas</h2>
      <p className="text-xs text-(--ink-dim) mb-3 max-w-3xl">
        We recomputed each figure on NZA&rsquo;s {townName} snapshot from the town&rsquo;s own zoning code and our district
        acreage, using NZA&rsquo;s definitions. Percentages are shares of residential land (gross acres; NZA removes
        protected and unzoned land). A difference of 5 points or more is highlighted.
      </p>
      <div className="overflow-x-auto border border-(--rule) rounded-lg bg-(--surface)">
        <table className="w-full text-sm min-w-[520px]">
          <thead>
            <tr className="bg-(--surface-2) text-left text-xs uppercase tracking-wide text-(--ink-dim)">
              <th className="px-3 py-2 font-semibold">Figure</th>
              <th className="px-3 py-2 font-semibold text-right">NZA</th>
              <th className="px-3 py-2 font-semibold text-right">Ours</th>
              <th className="px-3 py-2 font-semibold text-right">Ours &minus; NZA</th>
            </tr>
          </thead>
          <tbody>
            {FAMILIES.map((f) => (
              <Row key={`a-${f}`} label={`${f} allowed as of right`} nza={compare.as_of_right[f].nza} ours={compare.as_of_right[f].ours} />
            ))}
            {(["2-family", "3-family", "4+-family"] as NzaFamily[]).map((f) => (
              <Row key={`p-${f}`} label={`${f} prohibited`} nza={compare.prohibited[f].nza} ours={compare.prohibited[f].ours} />
            ))}
            <Row label="1-family land needing 80,000 sq ft or more" nza={compare.lot80.nza} ours={compare.lot80.ours} />
            <Row label="Residential land with a parking mandate" nza={compare.parking.nza} ours={compare.parking.ours} />
            <tr className="border-t-2 border-(--rule-strong) bg-(--surface-2)/50">
              <td className="px-3 py-2 font-semibold">NZA-derived proxy (same formula)</td>
              <td className="px-3 py-2 tabular text-right font-semibold">{p.nza_stored.toFixed(1)}</td>
              <td className="px-3 py-2 tabular text-right font-bold">{p.ours.toFixed(1)}</td>
              <td className="px-3 py-2 tabular text-right font-semibold">
                {p.difference >= 0 ? "+" : ""}
                {p.difference.toFixed(1)}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <ul className="mt-3 text-xs text-(--ink-dim) list-disc pl-5 flex flex-col gap-1">
        {p.nza_live !== p.nza_stored && (
          <li>
            Recomputed from NZA&rsquo;s live snapshot, NZA&rsquo;s proxy is {p.nza_live.toFixed(1)}; the stored figure above
            uses inputs saved earlier.
          </li>
        )}
        {p.ours_with_unconfirmed_districts !== undefined && (
          <li>
            Including districts whose acreage or reading is not yet confirmed, our proxy is{" "}
            {p.ours_with_unconfirmed_districts.toFixed(1)}.
          </li>
        )}
        {compare.notes.map((n) => (
          <li key={n}>{n}</li>
        ))}
      </ul>
      <p className="text-xs text-(--ink-faint) mt-2">
        Scripted and reproducible: <code className="tabular">{compare.replication_file}</code>.
      </p>
    </section>
  );
}
