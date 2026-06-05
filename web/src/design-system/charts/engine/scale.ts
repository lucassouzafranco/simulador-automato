export function scaleLinear(
  domain: [number, number],
  range: [number, number]
): (value: number) => number {
  const [dMin, dMax] = domain;
  const [rMin, rMax] = range;
  if (dMax === dMin) return () => (rMin + rMax) / 2;
  return (value: number) => rMin + ((value - dMin) / (dMax - dMin)) * (rMax - rMin);
}
