import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './grid.module.css';

export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12;
  rows?: 1 | 2 | 3 | 4 | 5 | 6;
  gap?: '0' | '1' | '2' | '3' | '4' | '6' | '8' | '12';
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'stretch';
}

export const Grid = React.forwardRef<HTMLDivElement, GridProps>(
  ({
    className,
    cols = 1,
    rows,
    gap = '4',
    align = 'stretch',
    justify = 'start',
    ...props
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          styles.grid,
          styles[`cols-${cols}`],
          rows && styles[`rows-${rows}`],
          styles[`gap-${gap}`],
          styles[`align-${align}`],
          styles[`justify-${justify}`],
          className
        )}
        {...props}
      />
    );
  }
);
Grid.displayName = 'Grid';
