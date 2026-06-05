import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '../../foundations/cn';
import styles from './text.module.css';

export type TextSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl';
export type TextWeight = 400 | 500 | 600 | 700;
export type TextColor = 'default' | 'muted' | 'primary' | 'destructive';
export type TextAlign = 'left' | 'center' | 'right' | 'justify';
export type TextTransform = 'uppercase' | 'lowercase' | 'capitalize' | 'normal-case';
export type TextDecoration = 'underline' | 'line-through' | 'no-underline';

export interface TextProps extends React.HTMLAttributes<HTMLElement> {
  as?: 'p' | 'span' | 'div' | 'label' | 'small' | 'strong' | 'em';
  asChild?: boolean;
  size?: TextSize;
  weight?: TextWeight;
  color?: TextColor;
  align?: TextAlign;
  transform?: TextTransform;
  decoration?: TextDecoration;
  truncate?: boolean;
  children: React.ReactNode;
}

export const Text = React.forwardRef<HTMLElement, TextProps>(
  (
    {
      as = 'p',
      asChild = false,
      size = 'base',
      weight = 400,
      color = 'default',
      align = 'left',
      transform,
      decoration,
      truncate = false,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : as;

    return (
      <Comp
        ref={ref as any}
        className={cn(
          styles.text,
          styles[`size-${size}`],
          styles[`weight-${weight}`],
          styles[`color-${color}`],
          styles[`align-${align}`],
          transform && styles[`transform-${transform}`],
          decoration && styles[`decoration-${decoration}`],
          truncate && styles.truncate,
          className
        )}
        {...props}
      >
        {children}
      </Comp>
    );
  }
);
Text.displayName = 'Text';
