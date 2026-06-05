import React from 'react';
import type { Margin } from '../engine/layout';

export interface ChartSvgProps {
  width: number;
  height: number;
  margin: Margin;
  children: React.ReactNode;
  onMouseMove?: React.MouseEventHandler<SVGSVGElement>;
  onMouseLeave?: React.MouseEventHandler<SVGSVGElement>;
}

export const ChartSvg: React.FC<ChartSvgProps> = ({
  width,
  height,
  margin,
  children,
  onMouseMove,
  onMouseLeave,
}) => (
  <svg
    width={width}
    height={height}
    onMouseMove={onMouseMove}
    onMouseLeave={onMouseLeave}
  >
    <g transform={`translate(${margin.left},${margin.top})`}>
      {children}
    </g>
  </svg>
);
