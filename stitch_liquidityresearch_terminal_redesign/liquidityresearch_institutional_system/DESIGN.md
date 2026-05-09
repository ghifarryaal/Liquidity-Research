---
name: LiquidityResearch Institutional System
colors:
  surface: '#0f1418'
  surface-dim: '#0f1418'
  surface-bright: '#343a3e'
  surface-container-lowest: '#0a0f12'
  surface-container-low: '#171c20'
  surface-container: '#1b2024'
  surface-container-high: '#252b2e'
  surface-container-highest: '#303539'
  on-surface: '#dee3e8'
  on-surface-variant: '#bdc8d1'
  inverse-surface: '#dee3e8'
  inverse-on-surface: '#2c3135'
  outline: '#87929a'
  outline-variant: '#3e484f'
  surface-tint: '#7bd0ff'
  primary: '#8ed5ff'
  on-primary: '#00354a'
  primary-container: '#38bdf8'
  on-primary-container: '#004965'
  inverse-primary: '#00668a'
  secondary: '#b7c8e1'
  on-secondary: '#213145'
  secondary-container: '#3a4a5f'
  on-secondary-container: '#a9bad3'
  tertiary: '#ffc176'
  on-tertiary: '#472a00'
  tertiary-container: '#f1a02b'
  on-tertiary-container: '#613b00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#c4e7ff'
  primary-fixed-dim: '#7bd0ff'
  on-primary-fixed: '#001e2c'
  on-primary-fixed-variant: '#004c69'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb960'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f1418'
  on-background: '#dee3e8'
  surface-variant: '#303539'
typography:
  display-sm:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  heading-table:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  body-standard:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  data-mono:
    fontFamily: Geist Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
  ticker-lg:
    fontFamily: Geist Mono
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  component-gap-sm: 8px
  component-gap-md: 12px
  section-margin: 32px
---

## Brand & Style

The design system is engineered for high-stakes financial analysis, prioritizing clarity, speed of cognition, and institutional trust. It avoids the whimsical trends of consumer fintech in favor of a "Bloomberg-refined" aesthetic—dense with information yet strictly organized to prevent cognitive overload.

The visual style is **Corporate / Modern** with a lean toward **High-Density Minimalism**. It utilizes a structural grid, precision geometry, and a monochromatic foundation to allow critical financial data to occupy the foreground. The emotional response is one of "Investment Grade" reliability: calm, objective, and authoritative.

## Colors

This design system utilizes a deep "Obsidian Slate" palette to reduce eye strain during prolonged research sessions. 

- **Primary Canvas:** The background uses `#0F172A` as the base, with `#1E293B` for elevated surface containers like cards and sidebars.
- **Semantic Accents:** Bullish and Bearish indicators are muted enough to avoid "vibrating" against the dark background but remain functionally distinct for rapid scanning.
- **Neutrality:** The system relies heavily on `#334155` for structural borders, creating a clear "blueprint" feel without the harshness of high-contrast white lines.
- **Interactive:** A refined Sky Blue (`#38BDF8`) is used sparingly for primary actions and focus states.

## Typography

The typography strategy separates **UI Narrative** from **Data Intelligence**.

1.  **UI Elements:** `Inter` is used for all navigational elements, labels, and descriptive text. It provides a neutral, highly legible foundation that disappears into the interface.
2.  **Financial Data:** `Geist Mono` (or Roboto Mono) is used exclusively for prices, percentages, timestamps, and tickers. The tabular figures ensure that columns of numbers align perfectly for vertical scanning, which is critical for identifying patterns in data grids.
3.  **Hierarchy:** We employ tight line heights and smaller base sizes (14px) to facilitate the "data-dense" requirement while maintaining readability through generous letter spacing on uppercase labels.

## Layout & Spacing

The design system employs a **Fixed-Fluid Hybrid Grid**. Sidebars and utility panels are fixed-width to maintain tool consistency, while the primary data stage (charts and grids) is fluid.

The spacing rhythm is based on a **4px baseline grid**. 
- **Density:** Information-heavy views use "Compact" spacing (8px between elements).
- **Margins:** 24px outer margins ensure the data-dense content doesn't feel cramped against the edges of the viewport.
- **Grids:** Data grids use 12px vertical padding on rows to balance density with "breathability."

## Elevation & Depth

This design system rejects heavy shadows and depth-based lighting. Instead, it uses **Tonal Layering** and **Low-Contrast Outlines**.

- **Surface Levels:** Z-index hierarchy is communicated through color shifts. The background is the darkest level (`#0F172A`). Cards and modules sit one step higher (`#1E293B`).
- **Borders over Shadows:** Physical separation is achieved via 1px solid borders in `#334155`. 
- **Hover States:** Interactive elements like table rows or cards use a subtle background shift (e.g., adding a 5% white overlay) rather than an outer shadow. 
- **Focus:** Active states are indicated by a 1px border of the Primary Accent color, rather than a "glow."

## Shapes

The shape language is "Engineering Grade." It avoids the "bubbly" appearance of consumer apps, favoring sharp, intentional geometry.

- **Primary Radius:** A consistent **6px radius** is applied to buttons, input fields, and small containers. This provides just enough softness to feel modern without losing the "Institutional" edge.
- **Card Radius:** Larger layout containers (cards, data modules) use an **8px radius**.
- **Interactive Elements:** Checkboxes and radio buttons maintain a minimal 2px radius or remain circular, respectively, to ensure they are instantly recognizable as form controls.

## Components

### Top Bar & Navigation
A slim, 48px high navigation bar. Use a background of `#1E293B` with a bottom border of `#334155`. Icons should be 18px, stroked (not filled), with a 1.5px weight.

### Data Grids
Rows must include a subtle `:hover` state using background color `#2D3748`. Column headers use `heading-table` typography with a subtle down-chevron for sorting. Cell alignment: Text left, Numbers/Monospaced right.

### Toggle Switches
Small, rectangular toggles with a 2px internal margin. The "off" state is a dark slate; the "on" state uses the Primary Sky Blue. No shadows on the toggle handle—use a flat white/gray.

### Progress Bars & Gauges
Ultra-slim (4px-6px height). Use the background color `#334155` for the "track" and semantic colors (Bullish/Bearish) for the "fill." 

### Buttons
- **Primary:** Solid `#38BDF8` with dark text. 
- **Secondary:** Ghost style with `#334155` border and `#F8FAFC` text. 
- **Tertiary:** Text-only for utility actions, using the Secondary Text color.

### Inputs
Search and data-entry fields use the background `#0F172A` with a `#334155` border. On focus, the border changes to the Primary Sky Blue.