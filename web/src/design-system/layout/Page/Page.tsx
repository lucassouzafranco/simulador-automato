import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './page.module.css';

export interface PageProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  container?: boolean;
}

export const Page: React.FC<PageProps> = ({
  className,
  title,
  description,
  container = true,
  children,
  ...props
}) => {
  return (
    <div className={cn(styles.page, className)} {...props}>
      {(title || description) && (
        <div className={styles.header}>
          {title && <h1 className={styles.title}>{title}</h1>}
          {description && <p className={styles.description}>{description}</p>}
        </div>
      )}
      {container ? (
        <div className={styles.container}>{children}</div>
      ) : (
        children
      )}
    </div>
  );
};
Page.displayName = 'Page';
