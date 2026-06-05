import * as React from 'react';
import { cn } from '../../foundations/cn';
import { variantUtils } from '../../foundations/variants';
import styles from './badge.module.css';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'outline' | 'destructive';
}

export const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variantAttrs = variantUtils.badge({ variant });

    return (
      <div
        ref={ref}
        className={cn(styles.badge, className)}
        {...variantAttrs}
        {...props}
      />
    );
  }
);
Badge.displayName = 'Badge';
