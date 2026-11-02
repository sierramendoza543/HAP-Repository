"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { gapRamp, scoreRamp } from "@/lib/colors";

type Position = [number, number];
interface GeoFeature {
  properties: Record<string, string | boolean | null>;
  geometry: { type: "Polygon" | "MultiPolygon"; coordinates: number[][][] | number[][][][] };
}
export interface GeoCollection {
  features: GeoFeature[];
}

export interface MapTown {
  slug: string;
  name: string;
  headline: number | null;
  basis: "v2" | "nza";
  nzaProxy: number;
  gap: number | null;
  pct2: number;
  pct3: number;
  pct4: number;
  lot80: number;
  parking: number;
  hasDistricts: boolean;
}

export interface MapDistrictScore {
  score: number | null;
  acres: number;
  included: boolean;
}

type MetricKey = "headline" | "nza" | "gap" | "pct2" | "pct3" | "pct4" | "lot80" | "parking";

const METRICS: { key: MetricKey; label: string; note: string; diverging?: boolean }[] = [
  { key: "headline", label: "Our score", note: "District-by-district score, land-weighted. Hatched towns are not yet scored by district." },
  { key: "nza", label: "NZA proxy", note: "Our weighted blend of three National Zoning Atlas figures" },
  { key: "gap", label: "Our score − NZA", note: "Positive: we score the town more restrictive than the NZA proxy", diverging: true },
  { key: "pct2", label: "2-family prohibited", note: "NZA: % of residential land" },
  { key: "pct3", label: "3-family prohibited", note: "NZA: % of residential land" },
  { key: "pct4", label: "4+-family prohibited", note: "NZA: % of residential land" },
  { key: "lot80", label: "Large-lot zoning", note: "NZA: % of 1-family land needing 80,000 sq ft or more" },
  { key: "parking", label: "Parking mandate", note: "NZA: % of residential land with a parking minimum" },
];

function valueOf(t: MapTown, key: MetricKey): number | null {
  switch (key) {
    case "headline": return t.headline;
    case "nza": return t.nzaProxy;
    case "gap": return t.gap;
    case "pct2": return t.pct2;
    case "pct3": return t.pct3;
    case "pct4": return t.pct4;
    case "lot80": return t.lot80;
    default: return t.parking;
  }
}

function ringPath(ring: number[][], proj: (p: Position) => Position) {
  return ring
    .map((p, i) => {
      const [x, y] = proj([p[0], p[1]]);
      return `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join("") + "Z";
}

function featurePath(f: GeoFeature, proj: (p: Position) => Position) {
  const g = f.geometry;
  const polys = (g.type === "Polygon" ? [g.coordinates] : g.coordinates) as number[][][][];
  return polys.map((poly) => poly.map((r) => ringPath(r, proj)).join("")).join("");
}

function bounds(features: GeoFeature[]) {
  let minX = 180, maxX = -180, minY = 90, maxY = -90;
  const visit = (c: unknown): void => {
    const a = c as unknown[];
    if (typeof a[0] === "number") {
      const [x, y] = a as number[];
      if (x < minX) minX = x;
      if (x > maxX) maxX = x;
      if (y < minY) minY = y;
      if (y > maxY) maxY = y;
    } else {
      a.forEach(visit);
    }
  };
  features.forEach((f) => visit(f.geometry.coordinates));
  return { minX, maxX, minY, maxY };
}

function makeProjection(b: ReturnType<typeof bounds>, width: number, pad = 8) {
  const lat0 = (b.minY + b.maxY) / 2;
  const kx = Math.cos((lat0 * Math.PI) / 180);
  const spanX = (b.maxX - b.minX) * kx;
  const spanY = b.maxY - b.minY;
  const scale = (width - pad * 2) / spanX;
  const height = spanY * scale + pad * 2;
  const proj = (p: Position): Position => [pad + (p[0] - b.minX) * kx * scale, pad + (b.maxY - p[1]) * scale];
  return { proj, height };
}

const WIDTH = 760;

export default function CtMap({
  townGeo,
  towns,
  districtScores,
}: {
  townGeo: GeoCollection;
  towns: MapTown[];
  districtScores: Record<string, Record<string, MapDistrictScore>>;
}) {
  const [metric, setMetric] = useState<MetricKey>("headline");
  const [selected, setSelected] = useState<string | null>(null);
  const [hovered, setHovered] = useState<string | null>(null);
  const [zoom, setZoom] = useState<string | null>(null);
  const [districtGeo, setDistrictGeo] = useState<Record<string, GeoCollection>>({});
  const [hoverDistrict, setHoverDistrict] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const bySlug = useMemo(() => Object.fromEntries(towns.map((t) => [t.slug, t])), [towns]);
  const regionView = useMemo(() => {
    const b = bounds(townGeo.features);
    return { ...makeProjection(b, WIDTH), b };
  }, [townGeo]);

  useEffect(() => {
    if (!zoom || districtGeo[zoom]) return;
    let cancelled = false;
    fetch(`/data/districts/${zoom}.geojson`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<GeoCollection>;
      })
      .then((g) => {
        if (!cancelled) setDistrictGeo((prev) => ({ ...prev, [zoom]: g }));
      })
      .catch((e: Error) => {
        if (!cancelled) setLoadError(`Could not load district map: ${e.message}`);
      });
    return () => {
      cancelled = true;
    };
  }, [zoom, districtGeo]);

  const metricDef = METRICS.find((m) => m.key === metric)!;
  const active = hovered ?? selected;
  const activeTown = active ? bySlug[active] : null;
  const zoomedGeo = zoom ? districtGeo[zoom] : undefined;

  const districtView = useMemo(() => {
    if (!zoomedGeo) return null;
    const b = bounds(zoomedGeo.features);
    return makeProjection(b, WIDTH);
  }, [zoomedGeo]);

  const colorFor = (t: MapTown) => {
    const v = valueOf(t, metric);
    if (v === null) return "url(#unscored)";
    return metricDef.diverging ? gapRamp(v) : scoreRamp(v);
  };

  const zoomTown = zoom ? bySlug[zoom] : null;
  const scores = zoom ? districtScores[zoom] ?? {} : {};
  const hoverInfo = hoverDistrict && zoom ? scores[hoverDistrict] : undefined;

  return (
    <div className="grid lg:grid-cols-[1fr_300px] gap-4">
      <div>
        <div className="flex flex-wrap gap-1.5 mb-3" role="tablist" aria-label="Map metric">
          {METRICS.map((m) => (
            <button
              key={m.key}
              role="tab"
              aria-selected={metric === m.key}
              onClick={() => setMetric(m.key)}
              disabled={Boolean(zoom)}
              className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                metric === m.key && !zoom
                  ? "bg-(--accent) text-(--accent-ink) border-(--accent)"
                  : "border-(--rule-strong) text-(--ink-dim) hover:text-(--ink) disabled:opacity-40 disabled:hover:text-(--ink-dim)"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
        <p className="text-xs text-(--ink-dim) mb-2">
          {zoom && zoomTown
            ? `${zoomTown.name}: each district colored by its V2 score (0 = least restrictive, 100 = most). Gray districts are not scored.`
            : metricDef.note}
        </p>

        <div className="relative border border-(--rule) rounded-lg bg-(--surface-2)/40 overflow-hidden">
          {zoom && (
            <button
              onClick={() => {
                setZoom(null);
                setHoverDistrict(null);
              }}
              className="absolute top-2 left-2 z-10 text-xs px-2.5 py-1 rounded-md bg-(--surface) border border-(--rule-strong) hover:border-(--accent)"
            >
              &larr; All towns
            </button>
          )}
          {!zoom && (
            <svg
              viewBox={`0 0 ${WIDTH} ${regionView.height}`}
              className="w-full h-auto max-h-[680px] block"
              role="group"
              aria-label="Map of the towns in Connecticut's 4th district, colored by the selected measure"
            >
              <defs>
                <pattern id="unscored" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                  <rect width="6" height="6" fill="rgb(214,218,225)" />
                  <line x1="0" y1="0" x2="0" y2="6" stroke="rgb(170,176,188)" strokeWidth="2" />
                </pattern>
              </defs>
              {townGeo.features.map((f) => {
                const slug = String(f.properties.slug);
                const t = bySlug[slug];
                if (!t) return null;
                const isSel = selected === slug;
                return (
                  <path
                    key={slug}
                    d={featurePath(f, regionView.proj)}
                    fillRule="evenodd"
                    fill={colorFor(t)}
                    stroke={isSel ? "var(--ink)" : "var(--surface)"}
                    strokeWidth={isSel ? 2.2 : 1}
                    strokeLinejoin="round"
                    tabIndex={0}
                    role="button"
                    aria-label={`${t.name}: ${metricDef.label} ${valueOf(t, metric)?.toFixed(1) ?? "not yet scored by district"}. Press Enter to select.`}
                    className="cursor-pointer outline-none focus-visible:stroke-(--ink)"
                    onMouseEnter={() => setHovered(slug)}
                    onMouseLeave={() => setHovered(null)}
                    onFocus={() => setHovered(slug)}
                    onBlur={() => setHovered(null)}
                    onClick={() => setSelected(slug)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setSelected(slug);
                      }
                    }}
                  />
                );
              })}
              {townGeo.features.map((f) => {
                const slug = String(f.properties.slug);
                const t = bySlug[slug];
                if (!t) return null;
                const b = bounds([f]);
                const [cx, cy] = regionView.proj([(b.minX + b.maxX) / 2, (b.minY + b.maxY) / 2]);
                return (
                  <text
                    key={`l-${slug}`}
                    x={cx}
                    y={cy}
                    textAnchor="middle"
                    fontSize={10}
                    fontWeight={600}
                    fill="#fff"
                    stroke="rgba(0,0,0,0.45)"
                    strokeWidth={2.5}
                    paintOrder="stroke"
                    pointerEvents="none"
                  >
                    {t.name}
                  </text>
                );
              })}
            </svg>
          )}
          {zoom && !zoomedGeo && !loadError && (
            <div className="h-72 flex items-center justify-center text-sm text-(--ink-dim)">Loading district map&hellip;</div>
          )}
          {zoom && loadError && (
            <div className="h-72 flex items-center justify-center text-sm text-(--prohibit)">{loadError}</div>
          )}
          {zoom && zoomedGeo && districtView && (
            <svg
              viewBox={`0 0 ${WIDTH} ${districtView.height}`}
              className="w-full h-auto max-h-[680px] block"
              role="group"
              aria-label={`Zoning districts of ${zoomTown?.name}, colored by V2 score`}
            >
              {zoomedGeo.features.map((f, i) => {
                const code = f.properties.code as string | null;
                const s = code ? scores[code] : undefined;
                const fill = s && s.score !== null && s.included ? scoreRamp(s.score) : "var(--rule-strong)";
                return (
                  <path
                    key={`${code ?? "x"}-${i}`}
                    d={featurePath(f, districtView.proj)}
                    fillRule="evenodd"
                    fill={fill}
                    fillOpacity={s && s.included ? 0.92 : 0.55}
                    stroke={code && code === hoverDistrict ? "var(--ink)" : "var(--surface)"}
                    strokeWidth={code && code === hoverDistrict ? 2 : 0.6}
                    onMouseEnter={() => setHoverDistrict(code)}
                    onMouseLeave={() => setHoverDistrict(null)}
                  />
                );
              })}
            </svg>
          )}
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-(--ink-dim)">
          <div className="flex items-center gap-2" aria-hidden>
            <span>{metricDef.diverging && !zoom ? "−25" : "0"}</span>
            <span
              className="h-2.5 w-40 rounded"
              style={{
                background:
                  metricDef.diverging && !zoom
                    ? "linear-gradient(90deg, rgb(37,99,235), rgb(236,238,242), rgb(234,88,12))"
                    : "linear-gradient(90deg, rgb(12,118,67), rgb(160,100,6), rgb(185,28,28))",
              }}
            />
            <span>{metricDef.diverging && !zoom ? "+25" : "100"}</span>
          </div>
          <span>
            {metricDef.diverging && !zoom ? "Blue: below NZA proxy · Orange: above" : "Green: least restrictive · Red: most restrictive"}
          </span>
        </div>
      </div>

      <aside className="border border-(--rule) rounded-lg bg-(--surface) p-4 h-fit" aria-live="polite">
        {zoom && zoomTown ? (
          <div>
            <h3 className="text-base font-semibold">{zoomTown.name}</h3>
            {hoverDistrict && hoverInfo ? (
              <div className="mt-2 text-sm">
                <p className="font-semibold">{hoverDistrict}</p>
                <p className="tabular">
                  V2 score: <b>{hoverInfo.included && hoverInfo.score !== null ? hoverInfo.score.toFixed(1) : "not scored"}</b>
                </p>
                <p className="tabular text-(--ink-dim)">{hoverInfo.acres.toLocaleString()} acres</p>
              </div>
            ) : (
              <p className="mt-2 text-xs text-(--ink-dim)">
                Hover a district to see its score. Open the town page for each district&rsquo;s components, evidence and NZA comparison.
              </p>
            )}
            <p className="mt-3 text-xs tabular text-(--ink-dim)">
              Town score {zoomTown.headline?.toFixed(1)} &middot; NZA proxy {zoomTown.nzaProxy.toFixed(1)}
            </p>
            <ul className="mt-3 max-h-64 overflow-y-auto text-xs flex flex-col gap-0.5 pr-1" aria-label="Districts by score">
              {Object.entries(scores)
                .filter(([, v]) => v.included && v.score !== null)
                .sort((a, b) => (b[1].score ?? 0) - (a[1].score ?? 0))
                .map(([code, v]) => (
                  <li
                    key={code}
                    onMouseEnter={() => setHoverDistrict(code)}
                    onMouseLeave={() => setHoverDistrict(null)}
                    className={`flex items-center gap-2 rounded px-1.5 py-0.5 ${hoverDistrict === code ? "bg-(--surface-2)" : ""}`}
                  >
                    <span className="inline-block w-3 h-3 rounded-sm shrink-0" style={{ background: scoreRamp(v.score!) }} />
                    <span className="flex-1 font-medium">{code}</span>
                    <span className="tabular text-(--ink-dim)">{v.score!.toFixed(1)}</span>
                  </li>
                ))}
            </ul>
            <Link href={`/towns/${zoomTown.slug}`} className="mt-3 inline-block text-sm text-(--accent) underline">
              Open {zoomTown.name}
            </Link>
          </div>
        ) : activeTown ? (
          <TownPanel
            t={activeTown}
            onZoom={() => {
              setLoadError(null);
              setZoom(activeTown.slug);
            }}
          />
        ) : (
          <p className="text-sm text-(--ink-dim)">
            Hover or select a town to compare our score with the National Zoning Atlas proxy and its underlying figures.
          </p>
        )}
      </aside>
    </div>
  );
}

function TownPanel({ t, onZoom }: { t: MapTown; onZoom: () => void }) {
  return (
    <div>
      <h3 className="text-base font-semibold">{t.name}</h3>
      <dl className="mt-2 text-sm grid grid-cols-[1fr_auto] gap-x-3 gap-y-1 tabular">
        <dt className="text-(--ink-dim)">Our score (district-level)</dt>
        <dd className="font-bold text-right">{t.headline !== null ? t.headline.toFixed(1) : "not yet"}</dd>
        <dt className="text-(--ink-dim)">NZA proxy</dt>
        <dd className="text-right font-semibold">{t.nzaProxy.toFixed(1)}</dd>
        <dt className="text-(--ink-dim)">Difference</dt>
        <dd className="text-right">
          {t.gap !== null ? `${t.gap >= 0 ? "+" : ""}${t.gap.toFixed(1)}` : "\u2013"}
        </dd>
      </dl>
      <p className="mt-3 text-[11px] uppercase tracking-wide text-(--ink-faint)">NZA snapshot figures</p>
      <dl className="mt-1 text-xs grid grid-cols-[1fr_auto] gap-x-3 gap-y-0.5 tabular text-(--ink-dim)">
        <dt>2-family prohibited</dt>
        <dd className="text-right">{t.pct2.toFixed(1)}%</dd>
        <dt>3-family prohibited</dt>
        <dd className="text-right">{t.pct3.toFixed(1)}%</dd>
        <dt>4+-family prohibited</dt>
        <dd className="text-right">{t.pct4.toFixed(1)}%</dd>
        <dt>1-family on 80,000+ sq ft</dt>
        <dd className="text-right">{t.lot80.toFixed(1)}%</dd>
        <dt>Parking mandate</dt>
        <dd className="text-right">{t.parking.toFixed(1)}%</dd>
      </dl>
      <div className="mt-3 flex flex-wrap gap-3 text-sm">
        <Link href={`/towns/${t.slug}`} className="text-(--accent) underline">
          Open {t.name}
        </Link>
        {t.hasDistricts && (
          <button onClick={onZoom} className="text-(--accent) underline">
            Show districts
          </button>
        )}
      </div>
    </div>
  );
}
