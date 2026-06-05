import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './radio-group.module.css';

export interface RadioGroupProps {
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
  className?: string;
  name?: string;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  value,
  onValueChange,
  children,
  className,
  name,
}) => {
  return (
    <div className={cn(styles.group, className)} role="radiogroup">
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) return child;
        return React.cloneElement(child as any, {
          checked: (child.props as any).value === value,
          onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.checked) {
              onValueChange?.((child.props as any).value);
            }
          },
          name,
        });
      })}
    </div>
  );
};
RadioGroup.displayName = 'RadioGroup';

export interface RadioItemProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string;
}

export const RadioItem = React.forwardRef<HTMLInputElement, RadioItemProps>(
  ({ className, label, id, ...props }, ref) => {
    const generatedId = React.useId();
    const itemId = id || generatedId;

    return (
      <div className={cn(styles.item, className)}>
        <input
          type="radio"
          id={itemId}
          ref={ref}
          className={styles.input}
          {...props}
        />
        <label htmlFor={itemId} className={styles.label}>
          <span className={styles.control}></span>
          <span>{label}</span>
        </label>
      </div>
    );
  }
);
RadioItem.displayName = 'RadioItem';
