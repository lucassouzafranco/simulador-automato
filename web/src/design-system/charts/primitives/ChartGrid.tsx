import React from 'react';
import styles from '../charts.module.css';

export interface ChartGridProps {
  innerWidth: number;
  innerHeight: number;
  ticks?: number[];
}

export const ChartGrid: React.FC<ChartGridProps> = ({
  innerWidth,
  innerHeight,
  ticks = [0, 0.25, 0.5, 0.75, 1],
}) => (
  <>
    {ticks.map((t) => {
      const y = innerHeight * (1 - t);
      return (
        <line
          key={t}
          x1={0}
          y1={y}
          x2={innerWidth}
          y2={y}
          className={styles.chartGrid}
        />
      );
    })}
  </>
);
