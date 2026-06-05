// Components (public API)
export { AreaChart } from './components/AreaChart';
export type { AreaChartProps } from './components/AreaChart';
export { BarChart } from './components/BarChart';
export type { BarChartProps } from './components/BarChart';
export { LineChart } from './components/LineChart';
export type { LineChartProps } from './components/LineChart';
export { PieChart } from './components/PieChart';
export type { PieChartProps } from './components/PieChart';

// Types
export type { DataPoint } from './types';

// Engine (available for custom chart composition)
export {
  scaleLinear,
  computeDomain,
  computeDomainFromZero,
  getDimensions,
  linePath,
  stepPath,
  areaPolygon,
  computeArcs,
} from './engine';
export type { Margin, Dimensions, ArcData } from './engine';

// Primitives (available for custom chart composition)
export {
  ChartRoot,
  ChartSvg,
  ChartGrid,
  ChartAxis,
  ChartTooltip,
} from './primitives';
export type {
  ChartRootProps,
  ChartSvgProps,
  ChartGridProps,
  ChartAxisProps,
  TooltipState,
  ChartTooltipProps,
} from './primitives';
