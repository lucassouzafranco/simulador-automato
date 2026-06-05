import React, { forwardRef } from 'react';
import { cn } from '../../foundations/cn';
import styles from '../charts.module.css';

export interface ChartRootProps extends React.HTMLAttributes<HTMLDivElement> {
  width: number;
  height: number;
}

export const ChartRoot = forwardRef<HTMLDivElement, ChartRootProps>(
  ({ width, height, className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(styles.chartContainer, className)}
      style={{ width, height }}
      {...props}
    >
      {children}
    </div>
  )
);

ChartRoot.displayName = 'ChartRoot';
