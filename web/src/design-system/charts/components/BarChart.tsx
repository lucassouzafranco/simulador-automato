import React, { useMemo, useRef, useState } from 'react';
import { getDimensions, scaleLinear } from '../engine';
import { ChartRoot, ChartSvg, ChartGrid, ChartAxis, ChartTooltip } from '../primitives';
import type { TooltipState } from '../primitives';
import type { DataPoint } from '../types';
import styles from '../charts.module.css';

export interface BarChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  className?: string;
  showTooltip?: boolean;
}

export const BarChart: React.FC<BarChartProps> = ({
  data,
  width = 400,
  height = 300,
  className,
  showTooltip = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const { margin, innerWidth, innerHeight } = useMemo(
    () => getDimensions(width, height),
    [width, height]
  );

  const values = data.map((d) => d.value);
  const maxValue = Math.max(...values);
  const barWidth = (innerWidth / data.length) * 0.8;

  const yScale = useMemo(
    () => scaleLinear([0, maxValue], [0, innerHeight]),
    [maxValue, innerHeight]
  );

  const handleBarHover = (index: number, e: React.MouseEvent<SVGRectElement>) => {
    if (!showTooltip || !containerRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const containerRect = containerRef.current.getBoundingClientRect();
    setTooltip({
      x: rect.left + rect.width / 2 - containerRect.left,
      y: rect.top - containerRect.top,
      content: `${data[index].name}: ${data[index].value}`,
    });
  };

  const handleMouseLeave = () => setTooltip(null);

  return (
    <ChartRoot ref={containerRef} width={width} height={height} className={className}>
      <ChartSvg
        width={width}
        height={height}
        margin={margin}
        onMouseLeave={handleMouseLeave}
      >
        <ChartGrid innerWidth={innerWidth} innerHeight={innerHeight} />
        {data.map((d, i) => {
          const x = i * (innerWidth / data.length) + (innerWidth / data.length - barWidth) / 2;
          const barHeight = yScale(d.value);
          return (
            <rect
              key={i}
              x={x}
              y={innerHeight - barHeight}
              width={barWidth}
              height={barHeight}
              className={styles.chartBar}
              onMouseMove={(e) => handleBarHover(i, e)}
              onMouseLeave={handleMouseLeave}
            />
          );
        })}
        <ChartAxis innerWidth={innerWidth} innerHeight={innerHeight} />
      </ChartSvg>
      <ChartTooltip tooltip={tooltip} />
    </ChartRoot>
  );
};
