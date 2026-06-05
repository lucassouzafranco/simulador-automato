import React from 'react';
import styles from '../charts.module.css';

export interface ChartAxisProps {
  innerWidth: number;
  innerHeight: number;
  showX?: boolean;
  showY?: boolean;
}

export const ChartAxis: React.FC<ChartAxisProps> = ({
  innerWidth,
  innerHeight,
  showX = true,
  showY = true,
}) => (
  <>
    {showX && (
      <line
        x1={0}
        y1={innerHeight}
        x2={innerWidth}
        y2={innerHeight}
        className={styles.chartAxis}
      />
    )}
    {showY && (
      <line
        x1={0}
        y1={0}
        x2={0}
        y2={innerHeight}
        className={styles.chartAxis}
      />
    )}
  </>
);
