import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './input.module.css';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(styles.input, error && styles.error, className)}
        {...props}
      />
    );
  }
);
Input.displayName = 'Input';
