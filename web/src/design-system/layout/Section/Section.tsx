import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './section.module.css';

export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  container?: boolean;
  background?: 'default' | 'muted' | 'card' | 'primary';
}

export const Section = React.forwardRef<HTMLElement, SectionProps>(
  ({ className, size = 'md', container = true, background = 'default', children, ...props }, ref) => {
    const content = container ? (
      <div className={styles.container}>{children}</div>
    ) : (
      children
    );

    return (
      <section
        ref={ref}
        className={cn(
          styles.section,
          styles[`size-${size}`],
          styles[`bg-${background}`],
          className
        )}
        {...props}
      >
        {content}
      </section>
    );
  }
);
Section.displayName = 'Section';
