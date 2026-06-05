import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './tooltip.module.css';

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  delay?: number;
  className?: string;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  side = 'top',
  align = 'center',
  delay = 200,
  className,
}) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const timeoutRef = React.useRef<any>(null);

  const show = () => {
    timeoutRef.current = setTimeout(() => setIsVisible(true), delay);
  };

  const hide = () => {
    clearTimeout(timeoutRef.current as any);
    setIsVisible(false);
  };

  return (
    <div className={styles.wrapper} onMouseEnter={show} onMouseLeave={hide}>
      {children}
      {isVisible && (
        <div
          className={cn(
            styles.tooltip,
            styles[side],
            styles[`align-${align}`],
            className
          )}
          role="tooltip"
        >
          {content}
        </div>
      )}
    </div>
  );
};
Tooltip.displayName = 'Tooltip';
