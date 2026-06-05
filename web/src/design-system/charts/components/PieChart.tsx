import React, { useMemo, useRef, useState } from 'react';
import { computeArcs } from '../engine';
import { ChartRoot, ChartTooltip } from '../primitives';
import type { TooltipState } from '../primitives';
import type { ArcData } from '../engine';
import type { DataPoint } from '../types';
import styles from '../charts.module.css';

export interface PieChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  className?: string;
  showTooltip?: boolean;
}

export const PieChart: React.FC<PieChartProps> = ({
  data,
  width = 400,
  height = 300,
  className,
  showTooltip = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);
  const radius = Math.min(width, height) / 2 * 0.8;
  const centerX = width / 2;
  const centerY = height / 2;

  const total = useMemo(() => data.reduce((sum, d) => sum + d.value, 0), [data]);

  const arcs = useMemo(
    () => computeArcs(data, centerX, centerY, radius),
    [data, centerX, centerY, radius]
  );

  const handleSliceHover = (arc: ArcData, e: React.MouseEvent<SVGPathElement>) => {
    if (!showTooltip || !containerRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const containerRect = containerRef.current.getBoundingClientRect();
    setTooltip({
      x: rect.left + rect.width / 2 - containerRect.left,
      y: rect.top - containerRect.top,
      content: `${arc.name}: ${arc.value} (${((arc.value / total) * 100).toFixed(1)}%)`,
    });
  };

  const handleMouseLeave = () => setTooltip(null);

  return (
    <ChartRoot ref={containerRef} width={width} height={height} className={className}>
      <svg width={width} height={height} onMouseLeave={handleMouseLeave}>
        {arcs.map((arc, i) => (
          <path
            key={i}
            d={arc.path}
            fill={`var(--color-chart-${(i % 5) + 1})`}
            className={styles.chartPieSlice}
            onMouseMove={(e) => handleSliceHover(arc, e)}
            onMouseLeave={handleMouseLeave}
          />
        ))}
      </svg>
      <ChartTooltip tooltip={tooltip} />
    </ChartRoot>
  );
};
