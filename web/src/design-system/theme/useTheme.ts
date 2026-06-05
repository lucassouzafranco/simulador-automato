import { useEffect, useState } from 'react';

export type ThemeMode = 'light' | 'dark' | 'system';

export function useTheme(defaultTheme: ThemeMode = 'system') {
  const [theme, setTheme] = useState<ThemeMode>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme') as ThemeMode | null;
      return stored || defaultTheme;
    }
    return defaultTheme;
  });

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const root = document.documentElement;

    const applyTheme = (newTheme: ThemeMode) => {
      let activeTheme: 'light' | 'dark';
      
      if (newTheme === 'system') {
        const media = window.matchMedia('(prefers-color-scheme: dark)');
        activeTheme = media.matches ? 'dark' : 'light';
      } else {
        activeTheme = newTheme as 'light' | 'dark';
      }

      // 1. Set the raw theme ('light' | 'dark' | 'system') for logic
      // 2. Set the data-theme attribute for CSS targeting
      root.setAttribute('data-theme', activeTheme);
      setResolvedTheme(activeTheme);
      
      localStorage.setItem('theme', newTheme);
    };

    applyTheme(theme);

    // Watch for system preference changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      if (theme === 'system') {
        applyTheme('system');
      }
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [theme]);


  return { theme, setTheme, resolvedTheme };
}
