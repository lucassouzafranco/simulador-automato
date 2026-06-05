import * as React from 'react';
import { cn } from '../../foundations/cn';
import { variantUtils } from '../../foundations/variants';
import styles from './separator.module.css';

export interface SeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  decorative?: boolean;
}

export const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  ({ className, orientation = 'horizontal', decorative = true, ...props }, ref) => {
    const variantAttrs = variantUtils.separator({ orientation });

    return (
      <div
        ref={ref}
        role={decorative ? 'none' : 'separator'}
        className={cn(styles.separator, className)}
        {...variantAttrs}
        {...props}
      />
    );
  }
);
Separator.displayName = 'Separator';
