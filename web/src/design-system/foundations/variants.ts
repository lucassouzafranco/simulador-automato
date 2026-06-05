export function createVariants<T extends Record<string, Record<string, string>>>(
  config: T
) {
  return (variants: { [K in keyof T]?: keyof T[K] }) => {
    const attributes: Record<string, string> = {};

    Object.entries(variants).forEach(([key, value]) => {
      if (value && config[key] && config[key][value as string]) {
        attributes[`data-${key}`] = value as string;
      }
    });

    return attributes;
  };
}

export const variantUtils = {
  button: createVariants({
    variant: {
      primary: 'primary',
      secondary: 'secondary',
      outline: 'outline',
      ghost: 'ghost',
      destructive: 'destructive',
    },
    size: {
      sm: 'sm',
      md: 'md',
      lg: 'lg',
    },
  }),
  badge: createVariants({
    variant: {
      default: 'default',
      secondary: 'secondary',
      outline: 'outline',
      destructive: 'destructive',
    },
  }),
  separator: createVariants({
    orientation: {
      horizontal: 'horizontal',
      vertical: 'vertical',
    },
  }),
};
