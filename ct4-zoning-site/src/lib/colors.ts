// green (permissive) -> amber -> red (restrictive)
export function scoreRamp(v: number) {
  const t = Math.max(0, Math.min(100, v)) / 100;
  const stops: [number, number[]][] = [
    [0, [12, 118, 67]],
    [0.5, [160, 100, 6]],
    [1, [185, 28, 28]],
  ];
  let lo = stops[0];
  let hi = stops[2];
  for (let i = 0; i < 2; i++) {
    if (t >= stops[i][0] && t <= stops[i + 1][0]) {
      lo = stops[i];
      hi = stops[i + 1];
      break;
    }
  }
  const k = (t - lo[0]) / (hi[0] - lo[0] || 1);
  return `rgb(${lo[1].map((c, i) => Math.round(c + (hi[1][i] - c) * k)).join(",")})`;
}

// blue (we score lower than NZA) -> light -> orange (we score higher)
export function gapRamp(v: number) {
  const t = Math.max(-1, Math.min(1, v / 25));
  const mid = [236, 238, 242];
  const end = t < 0 ? [37, 99, 235] : [234, 88, 12];
  const k = Math.abs(t);
  return `rgb(${mid.map((c, i) => Math.round(c + (end[i] - c) * k)).join(",")})`;
}
