export interface ArcData {
  path: string;
  name: string;
  value: number;
  startAngle: number;
  endAngle: number;
}

export function computeArcs(
  data: Array<{ name: string; value: number }>,
  centerX: number,
  centerY: number,
  radius: number
): ArcData[] {
  const total = data.reduce((sum, d) => sum + d.value, 0);
  let startAngle = 0;
  return data.map((d) => {
    const angle = (d.value / total) * 2 * Math.PI;
    const endAngle = startAngle + angle;
    const largeArcFlag = angle > Math.PI ? 1 : 0;
    const x1 = centerX + radius * Math.cos(startAngle);
    const y1 = centerY + radius * Math.sin(startAngle);
    const x2 = centerX + radius * Math.cos(endAngle);
    const y2 = centerY + radius * Math.sin(endAngle);
    const path = `M ${centerX},${centerY} L ${x1},${y1} A ${radius},${radius} 0 ${largeArcFlag} 1 ${x2},${y2} Z`;
    const result: ArcData = { path, name: d.name, value: d.value, startAngle, endAngle };
    startAngle = endAngle;
    return result;
  });
}
