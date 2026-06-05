import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '../../foundations/cn';
import styles from './heading.module.css';
import type { TextSize, TextWeight, TextColor, TextAlign } from '../Text/Text';

export type HeadingLevel = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';

const defaultSizeMap: Record<HeadingLevel, TextSize> = {
  h1: '4xl',
  h2: '3xl',
  h3: '2xl',
  h4: 'xl',
  h5: 'lg',
  h6: 'base',
};

export interface HeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  as?: HeadingLevel;
  asChild?: boolean;
  size?: TextSize;
  weight?: TextWeight;
  color?: TextColor;
  align?: TextAlign;
  transform?: 'uppercase' | 'lowercase' | 'capitalize' | 'normal-case';
  truncate?: boolean;
  children: React.ReactNode;
}

export const Heading = React.forwardRef<HTMLHeadingElement, HeadingProps>(
  (
    {
      as = 'h2',
      asChild = false,
      size,
      weight = 600,
      color = 'default',
      align = 'left',
      transform,
      truncate = false,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : as;
    const finalSize = size || defaultSizeMap[as];

    return (
      <Comp
        ref={ref}
        className={cn(
          styles.heading,
          styles[`size-${finalSize}`],
          styles[`weight-${weight}`],
          styles[`color-${color}`],
          styles[`align-${align}`],
          transform && styles[`transform-${transform}`],
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
Heading.displayName = 'Heading';
