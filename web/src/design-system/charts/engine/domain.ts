export function computeDomain(values: number[]): [number, number] {
  return [Math.min(...values), Math.max(...values)];
}

export function computeDomainFromZero(values: number[]): [number, number] {
  return [Math.min(0, ...values), Math.max(...values)];
}
