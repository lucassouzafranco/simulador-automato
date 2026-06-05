import { tokens } from '../tokens/tokens';

function camelToKebab(str: string): string {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/([a-zA-Z])(\d)/g, '$1-$2')
    .toLowerCase();
}

function generateThemeCSS(theme: 'light' | 'dark'): string {
  const colorTokens = tokens.colors[theme];
  let css = '';

  Object.entries(colorTokens).forEach(([key, value]) => {
    css += `  --color-${camelToKebab(key)}: ${value};\n`;
  });

  Object.entries(tokens.spacing).forEach(([key, value]) => {
    css += `  --spacing-${key}: ${value};\n`;
  });

  Object.entries(tokens.radius).forEach(([key, value]) => {
    css += `  --radius-${key}: ${value};\n`;
  });

  Object.entries(tokens.shadows).forEach(([key, value]) => {
    css += `  --shadow-${key}: ${value};\n`;
  });

  css += `  --font-family-sans: ${tokens.typography.fontFamily.sans};\n`;
  css += `  --font-family-mono: ${tokens.typography.fontFamily.mono};\n`;

  Object.entries(tokens.typography.fontSize).forEach(([key, value]) => {
    css += `  --font-size-${key}: ${value};\n`;
  });

  Object.entries(tokens.typography.fontWeight).forEach(([key, value]) => {
    css += `  --font-weight-${key}: ${value};\n`;
  });

  Object.entries(tokens.typography.lineHeight).forEach(([key, value]) => {
    css += `  --line-height-${key}: ${value};\n`;
  });

  Object.entries(tokens.transitions).forEach(([key, value]) => {
    css += `  --transition-${key}: ${value};\n`;
  });

  Object.entries(tokens.breakpoints).forEach(([key, value]) => {
    css += `  --breakpoint-${key}: ${value};\n`;
  });

  Object.entries(tokens.zIndex).forEach(([key, value]) => {
    css += `  --z-index-${key}: ${value};\n`;
  });

  if (theme === 'dark') {
    css += '  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);\n';
    css += '  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3);\n';
    css += '  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.3);\n';
    css += '  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);\n';
    css += '  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.5);\n';
  }

  return css;
}

export function generateCSSVariables(): string {
  const lightCSS = generateThemeCSS('light');
  const darkCSS = generateThemeCSS('dark');

  return `:root {
${lightCSS}}

@media (prefers-color-scheme: dark) {
  :root {
${darkCSS}  }
}

:root[data-theme="light"] {
${lightCSS}  color-scheme: light;
}

:root[data-theme="dark"] {
${darkCSS}  color-scheme: dark;
}`;
}

