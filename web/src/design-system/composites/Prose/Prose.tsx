import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './prose.module.css';

export interface ProseProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'base' | 'lg';
  children: React.ReactNode;
}

export const Prose = React.forwardRef<HTMLDivElement, ProseProps>(
  ({ className, size = 'base', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(styles.prose, styles[`size-${size}`], className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Prose.displayName = 'Prose';
