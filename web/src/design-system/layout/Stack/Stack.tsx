import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './stack.module.css';

export interface StackProps extends React.HTMLAttributes<HTMLDivElement> {
  direction?: 'row' | 'column' | 'row-reverse' | 'column-reverse';
  spacing?: '0' | '1' | '2' | '3' | '4' | '6' | '8' | '12' | '16';
  align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  wrap?: boolean;
}

export const Stack = React.forwardRef<HTMLDivElement, StackProps>(
  ({
    className,
    direction = 'column',
    spacing = '4',
    align = 'stretch',
    justify = 'start',
    wrap = false,
    ...props
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          styles.stack,
          styles[`direction-${direction}`],
          styles[`spacing-${spacing}`],
          styles[`align-${align}`],
          styles[`justify-${justify}`],
          wrap && styles.wrap,
          className
        )}
        {...props}
      />
    );
  }
);
Stack.displayName = 'Stack';
