import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './label.module.css';

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {}

export const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(styles.label, className)}
        {...props}
      />
    );
  }
);
Label.displayName = 'Label';
