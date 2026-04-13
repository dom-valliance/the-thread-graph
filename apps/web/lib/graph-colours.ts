/**
 * Centralised colour constants for D3 graph visualisations.
 *
 * All graph components should import from here rather than defining
 * local hex constants. When the Valliance design system tokens settle,
 * update values here once and all graphs update.
 */

// -- Semantic colours ---------------------------------------------------------

export const GRAPH_COLOURS = {
  primary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  purple: '#8b5cf6',
  pink: '#ec4899',
  indigo: '#6366f1',
  teal: '#14b8a6',
  orange: '#f97316',
  green: '#22c55e',
} as const;

// -- Arc colour palette (cycled by arc index) ---------------------------------

export const ARC_PALETTE = [
  GRAPH_COLOURS.primary,
  GRAPH_COLOURS.success,
  GRAPH_COLOURS.warning,
  GRAPH_COLOURS.danger,
  GRAPH_COLOURS.purple,
  GRAPH_COLOURS.pink,
  GRAPH_COLOURS.teal,
  GRAPH_COLOURS.orange,
] as const;

export function arcColour(index: number): string {
  return ARC_PALETTE[index % ARC_PALETTE.length];
}

// -- Neutral / chrome colours (slate scale) -----------------------------------

export const NEUTRAL = {
  50: '#f8fafc',
  100: '#f1f5f9',
  200: '#e2e8f0',
  300: '#cbd5e1',
  400: '#94a3b8',
  500: '#64748b',
  600: '#475569',
  700: '#334155',
  800: '#1e293b',
  900: '#0f172a',
} as const;

// -- Shorthand aliases for common graph roles ---------------------------------

export const LINK_COLOUR = NEUTRAL[300];
export const LABEL_COLOUR = NEUTRAL[600];
export const MUTED_NODE_COLOUR = NEUTRAL[400];
export const TOOLTIP_BG = NEUTRAL[800];
export const TOOLTIP_FG = NEUTRAL[50];
export const GRID_STROKE = NEUTRAL[200];
