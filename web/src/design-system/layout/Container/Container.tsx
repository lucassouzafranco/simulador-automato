import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './container.module.css';

export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  noPadding?: boolean;
}

export const Container = React.forwardRef<HTMLDivElement, ContainerProps>(
  ({ className, size = 'lg', noPadding = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          styles.container,
          styles[`size-${size}`],
          noPadding && styles.noPadding,
          className
        )}
        {...props}
      />
    );
  }
);
Container.displayName = 'Container';
