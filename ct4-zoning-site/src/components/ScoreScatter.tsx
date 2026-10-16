"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Town } from "@/lib/types";

const W = 760;
const H = 360;
const PAD = { top: 16, right: 24, bottom: 36, left: 48 };

function scaleLog(value: number, domain: [number, number], range: [number, number]) {
  const [d0, d1] = domain.map(Math.log10);
  const [r0, r1] = range;
  const t = (Math.log10(Math.max(value, 1)) - d0) / (d1 - d0);
  return r0 + t * (r1 - r0);
}

function scaleLinear(value: number, domain: [number, number], range: [number, number]) {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const t = (value - d0) / (d1 - d0);
  return r0 + t * (r1 - r0);
}

function scoreColor(score: number) {
  if (score >= 66) return "var(--prohibit)";
  if (score >= 33) return "var(--maybe)";
  return "var(--allow)";
}

export default function ScoreScatter({ towns }: { towns: Town[] }) {
  const [hover, setHover] = useState<string | null>(null);
  const router = useRouter();

  const popDomain: [number, number] = [5000, 160000];
  const xRange: [number, number] = [PAD.left, W - PAD.right];
  const yRange: [number, number] = [H - PAD.bottom, PAD.top];

  const ticks = [10000, 30000, 100000];

  return (
    <div className="border border-(--rule) rounded-lg bg-(--surface) p-4 overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ minWidth: 560 }} role="img" aria-label="Population vs. composite score scatter plot">
        {/* gridlines */}
        {[0, 25, 50, 75, 100].map((y) => (
          <g key={y}>
            <line
              x1={PAD.left}
              x2={W - PAD.right}
              y1={scaleLinear(y, [0, 100], yRange)}
              y2={scaleLinear(y, [0, 100], yRange)}
              stroke="var(--rule)"
              strokeWidth={1}
            />
            <text x={PAD.left - 8} y={scaleLinear(y, [0, 100], yRange) + 4} textAnchor="end" fontSize={11} fill="var(--ink-faint)">
              {y}
            </text>
          </g>
        ))}
        {ticks.map((t) => (
          <g key={t}>
            <line x1={scaleLog(t, popDomain, xRange)} x2={scaleLog(t, popDomain, xRange)} y1={PAD.top} y2={H - PAD.bottom} stroke="var(--rule)" strokeWidth={1} />
            <text x={scaleLog(t, popDomain, xRange)} y={H - PAD.bottom + 18} textAnchor="middle" fontSize={11} fill="var(--ink-faint)">
              {t.toLocaleString()}
            </text>
          </g>
        ))}
        <text x={W / 2} y={H - 4} textAnchor="middle" fontSize={11} fill="var(--ink-dim)">
          Population (log scale)
        </text>
        <text x={14} y={H / 2} textAnchor="middle" fontSize={11} fill="var(--ink-dim)" transform={`rotate(-90 14 ${H / 2})`}>
          Composite score
        </text>

        {towns.map((t) => {
          const cx = scaleLog(t.population, popDomain, xRange);
          const cy = scaleLinear(t.composite_score, [0, 100], yRange);
          const isHover = hover === t.slug;
          return (
            <g
              key={t.slug}
              onMouseEnter={() => setHover(t.slug)}
              onMouseLeave={() => setHover(null)}
              onClick={() => router.push(`/towns/${t.slug}`)}
              style={{ cursor: "pointer" }}
            >
              <circle cx={cx} cy={cy} r={isHover ? 7 : 5} fill={scoreColor(t.composite_score)} fillOpacity={0.85} stroke="var(--surface)" strokeWidth={1.5} />
              {isHover && (
                <g>
                  <rect x={cx + 8} y={cy - 22} width={t.name.length * 6.5 + 50} height={32} rx={4} fill="var(--ink)" opacity={0.95} />
                  <text x={cx + 14} y={cy - 8} fontSize={11} fill="var(--bg)" fontWeight={600}>
                    {t.name}
                  </text>
                  <text x={cx + 14} y={cy + 4} fontSize={10} fill="var(--bg)" opacity={0.8}>
                    score {t.composite_score.toFixed(1)} · pop {t.population.toLocaleString()}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
