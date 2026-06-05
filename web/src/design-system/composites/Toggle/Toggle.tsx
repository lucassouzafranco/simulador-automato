import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './toggle.module.css';

export interface ToggleProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onChange'> {
  pressed?: boolean;
  defaultPressed?: boolean;
  onChange?: (pressed: boolean) => void;
}

export const Toggle = React.forwardRef<HTMLButtonElement, ToggleProps>(
  ({
    className,
    pressed: controlledPressed,
    defaultPressed = false,
    onChange,
    children,
    ...props
  }, ref) => {
    const [uncontrolledPressed, setUncontrolledPressed] = React.useState(defaultPressed);
    const isControlled = controlledPressed !== undefined;
    const pressed = isControlled ? controlledPressed : uncontrolledPressed;

    const handleClick = () => {
      const newPressed = !pressed;
      if (!isControlled) {
        setUncontrolledPressed(newPressed);
      }
      onChange?.(newPressed);
    };

    return (
      <button
        ref={ref}
        type="button"
        className={cn(styles.toggle, pressed && styles.pressed, className)}
        onClick={handleClick}
        aria-pressed={pressed}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Toggle.displayName = 'Toggle';
