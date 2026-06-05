import React, { useMemo, useRef, useState } from 'react';
import { getDimensions, scaleLinear, linePath, stepPath } from '../engine';
import { ChartRoot, ChartSvg, ChartGrid, ChartAxis, ChartTooltip } from '../primitives';
import type { TooltipState } from '../primitives';
import type { DataPoint } from '../types';
import styles from '../charts.module.css';

export interface LineChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  className?: string;
  showTooltip?: boolean;
  variant?: 'linear' | 'step';
}

export const LineChart: React.FC<LineChartProps> = ({
  data,
  width = 400,
  height = 300,
  className,
  showTooltip = true,
  variant = 'linear',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const { margin, innerWidth, innerHeight } = useMemo(
    () => getDimensions(width, height),
    [width, height]
  );

  const values = data.map((d) => d.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);

  const xScale = useMemo(
    () => scaleLinear([0, data.length - 1], [0, innerWidth]),
    [data.length, innerWidth]
  );
  const yScale = useMemo(
    () => scaleLinear([minValue, maxValue], [innerHeight, 0]),
    [minValue, maxValue, innerHeight]
  );

  const points = data.map((d, i) => ({ x: xScale(i), y: yScale(d.value) }));
  const pathD = variant === 'linear' ? linePath(points) : stepPath(points);

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!showTooltip || !containerRef.current) return;
    const svgRect = e.currentTarget.getBoundingClientRect();
    const mouseX = e.clientX - svgRect.left - margin.left;
    if (mouseX < 0 || mouseX > innerWidth) {
      setTooltip(null);
      return;
    }
    const index = Math.round((mouseX / innerWidth) * (data.length - 1));
    if (index >= 0 && index < data.length) {
      setTooltip({
        x: xScale(index) + margin.left,
        y: yScale(data[index].value) + margin.top,
        content: `${data[index].name}: ${data[index].value}`,
      });
    }
  };

  const handleMouseLeave = () => setTooltip(null);

  return (
    <ChartRoot ref={containerRef} width={width} height={height} className={className}>
      <ChartSvg
        width={width}
        height={height}
        margin={margin}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <ChartGrid innerWidth={innerWidth} innerHeight={innerHeight} />
        <path d={pathD} className={styles.chartLine} />
        <ChartAxis innerWidth={innerWidth} innerHeight={innerHeight} />
      </ChartSvg>
      <ChartTooltip tooltip={tooltip} />
    </ChartRoot>
  );
};
