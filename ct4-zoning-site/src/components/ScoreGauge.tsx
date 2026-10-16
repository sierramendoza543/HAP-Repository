function bandColor(score: number) {
  if (score >= 66) return "var(--prohibit)";
  if (score >= 33) return "var(--maybe)";
  return "var(--allow)";
}

function bandLabel(score: number) {
  if (score >= 66) return "Highly Restrictive";
  if (score >= 33) return "Moderately Restrictive";
  return "Comparatively Permissive";
}

// Polar point on a circle of radius r centered at (cx, cy), angle in degrees
// where 0deg = straight up, increasing clockwise.
function polar(cx: number, cy: number, r: number, angleDeg: number) {
  const a = ((angleDeg - 90) * Math.PI) / 180;
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}

// Describes an SVG arc path from startDeg to endDeg (measured from the gauge's own
// -130..130 sweep, i.e. 0 = startDeg of the whole gauge) on radius r.
function arcPath(cx: number, cy: number, r: number, startDeg: number, endDeg: number) {
  const s = polar(cx, cy, r, startDeg);
  const e = polar(cx, cy, r, endDeg);
  const large = endDeg - startDeg > 180 ? 1 : 0;
  return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
}

export default function ScoreGauge({
  score,
  nzaScore,
}: {
  score: number;
  nzaScore: number;
}) {
  const size = 240;
  const cx = size / 2;
  const cy = size / 2 + 10;
  const r = 92;
  const SWEEP_START = -130;
  const SWEEP_END = 130;
  const SWEEP = SWEEP_END - SWEEP_START;
  const scoreAngle = SWEEP_START + (Math.max(0, Math.min(100, score)) / 100) * SWEEP;
  const color = bandColor(score);

  return (
    <div className="flex flex-col items-center">
      <svg viewBox={`0 0 ${size} ${size - 40}`} width={240} height={200} role="img" aria-label={`HAP restrictiveness score ${score.toFixed(1)} out of 100`}>
        <defs>
          <linearGradient id="gaugeTrack" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--allow)" />
            <stop offset="50%" stopColor="var(--maybe)" />
            <stop offset="100%" stopColor="var(--prohibit)" />
          </linearGradient>
        </defs>
        {/* background track */}
        <path d={arcPath(cx, cy, r, SWEEP_START, SWEEP_END)} fill="none" stroke="var(--surface-2)" strokeWidth={14} strokeLinecap="round" />
        {/* colored gradient track, faint */}
        <path d={arcPath(cx, cy, r, SWEEP_START, SWEEP_END)} fill="none" stroke="url(#gaugeTrack)" strokeWidth={14} strokeLinecap="round" opacity={0.18} />
        {/* filled progress to current score */}
        <path d={arcPath(cx, cy, r, SWEEP_START, scoreAngle)} fill="none" stroke={color} strokeWidth={14} strokeLinecap="round" />
        {/* needle tick for NZA score, for comparison */}
        {(() => {
          const nzaAngle = SWEEP_START + (Math.max(0, Math.min(100, nzaScore)) / 100) * SWEEP;
          const inner = polar(cx, cy, r - 11, nzaAngle);
          const outer = polar(cx, cy, r + 11, nzaAngle);
          return (
            <line
              x1={inner.x}
              y1={inner.y}
              x2={outer.x}
              y2={outer.y}
              stroke="var(--ink-faint)"
              strokeWidth={2.5}
              strokeDasharray="1 2.5"
              strokeLinecap="round"
            />
          );
        })()}
        <text x={cx} y={cy - 18} textAnchor="middle" fontSize={44} fontWeight={800} fill="var(--ink)" className="tabular">
          {score.toFixed(1)}
        </text>
        <text x={cx} y={cy + 4} textAnchor="middle" fontSize={11} fontWeight={600} fill={color} letterSpacing={0.3}>
          {bandLabel(score).toUpperCase()}
        </text>
      </svg>
      <p className="text-xs font-semibold uppercase tracking-wide text-(--ink-dim) -mt-2">HAP Restrictiveness Score</p>
      <p className="text-[11px] text-(--ink-faint) mt-1">
        NZA 2026 Score: <span className="tabular font-medium">{nzaScore.toFixed(1)}</span>
        <span className="inline-block w-2 h-0.5 bg-(--ink-faint) align-middle mx-1" /> tick on gauge
      </p>
    </div>
  );
}
