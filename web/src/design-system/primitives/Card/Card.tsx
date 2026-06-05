import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './card.module.css';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outline' | 'elevated';
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(styles.card, styles[`variant-${variant}`], className)}
        {...props}
      />
    );
  }
);
Card.displayName = 'Card';
