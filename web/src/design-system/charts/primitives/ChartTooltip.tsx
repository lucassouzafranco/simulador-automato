import React from 'react';
import styles from '../charts.module.css';

export interface TooltipState {
  x: number;
  y: number;
  content: string;
}

export interface ChartTooltipProps {
  tooltip: TooltipState | null;
}

export const ChartTooltip: React.FC<ChartTooltipProps> = ({ tooltip }) => {
  if (!tooltip) return null;
  return (
    <div
      className={styles.tooltip}
      style={{ left: tooltip.x, top: tooltip.y }}
    >
      {tooltip.content}
    </div>
  );
};
