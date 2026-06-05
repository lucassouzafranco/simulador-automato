import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '../../foundations/cn';
import { variantUtils } from '../../foundations/variants';
import styles from './button.module.css';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  asChild?: boolean;
  fullWidth?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className,
    variant = 'primary',
    size = 'md',
    asChild = false,
    fullWidth = false,
    ...props
  }, ref) => {
    const Comp = asChild ? Slot : 'button';
    const variantAttrs = variantUtils.button({ variant, size });

    return (
      <Comp
        className={cn(
          styles.button,
          fullWidth && styles.fullWidth,
          className
        )}
        {...variantAttrs}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';
