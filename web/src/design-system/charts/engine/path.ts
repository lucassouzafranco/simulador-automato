export function linePath(
  points: Array<{ x: number; y: number }>
): string {
  return `M ${points.map((p) => `${p.x},${p.y}`).join(' L ')}`;
}

export function stepPath(
  points: Array<{ x: number; y: number }>
): string {
  return points.reduce((path, p, i) => {
    if (i === 0) return `M ${p.x},${p.y}`;
    return `${path} H ${p.x} V ${p.y}`;
  }, '');
}

export function areaPolygon(
  points: Array<{ x: number; y: number }>,
  baseline: number
): string {
  const line = points.map((p) => `${p.x},${p.y}`).join(' ');
  const lastX = points[points.length - 1]?.x ?? 0;
  const firstX = points[0]?.x ?? 0;
  return `${firstX},${baseline} ${line} ${lastX},${baseline}`;
}
