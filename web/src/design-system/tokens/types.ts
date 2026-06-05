import { tokens } from './tokens';

export type Tokens = typeof tokens;
export type ThemeMode = 'light' | 'dark';
export type ColorToken = keyof typeof tokens.colors.light;
export type SpacingToken = keyof typeof tokens.spacing;
export type RadiusToken = keyof typeof tokens.radius;
export type ShadowToken = keyof typeof tokens.shadows;
export type FontSizeToken = keyof typeof tokens.typography.fontSize;
export type FontWeightToken = keyof typeof tokens.typography.fontWeight;
export type LineHeightToken = keyof typeof tokens.typography.lineHeight;
export type TransitionToken = keyof typeof tokens.transitions;
export type BreakpointToken = keyof typeof tokens.breakpoints;
export type ZIndexToken = keyof typeof tokens.zIndex;
