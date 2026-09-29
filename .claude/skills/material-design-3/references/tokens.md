# M3 token reference

Three tiers, the same as Material 3's own:

1. **Reference**: `--md-ref-palette-{primary,secondary,tertiary,error,success,warning,neutral,neutral-variant}{tone}`,
   tones 0–100. Generated into `wise_core/static/wise_core/css/md3-palettes.css` by
   `scripts/generate_m3_palettes.mjs` (Google's `@material/material-color-utilities`). Never used by
   components or templates.
2. **System**: `--md-sys-*` in `tokens.css` (`:root` for light, `:root[data-theme="dark"]` for dark).
3. **Tailwind**: `@theme static` in `tokens.css` → utilities.

## Color roles (light tone / dark tone)

| Role | Light | Dark | Tailwind |
|---|---|---|---|
| primary | P40 | P80 | `bg-primary`, `text-primary`, `border-primary` |
| on-primary | P100 | P20 | `text-on-primary` |
| primary-container | P90 | P30 | `bg-primary-container` |
| on-primary-container | P30 | P90 | `text-on-primary-container` |
| inverse-primary | P80 | P40 | `text-inverse-primary` |
| primary-fixed / -fixed-dim / on-primary-fixed / on-primary-fixed-variant | P90 / P80 / P10 / P30 | same | `bg-primary-fixed`, ... |
| secondary, on-secondary, secondary-container, on-secondary-container | S40, S100, S90, S30 | S80, S20, S30, S90 | `bg-secondary`, ... |
| tertiary (same four) | T40, T100, T90, T30 | T80, T20, T30, T90 | `bg-tertiary`, ... |
| error (same four) | E40, E100, E90, E30 | E80, E20, E30, E90 | `bg-error`, ... |
| success / warning (same four, harmonized custom colors) | 40, 100, 90, 30 | 80, 20, 30, 90 | `bg-success-container`, ... |
| surface / background | N98 | N6 | `bg-surface` |
| surface-dim / surface-bright | N87 / N98 | N6 / N24 | `bg-surface-dim` |
| surface-container-lowest / low / (base) / high / highest | N100 / N96 / N94 / N92 / N90 | N4 / N10 / N12 / N17 / N22 | `bg-surface-container-low`, ... |
| on-surface | N10 | N90 | `text-on-surface` |
| on-surface-variant | NV30 | NV80 | `text-on-surface-variant` |
| surface-variant | NV90 | NV30 | `bg-surface-variant` |
| outline / outline-variant | NV50 / NV80 | NV60 / NV30 | `border-outline`, `border-outline-variant` |
| inverse-surface / inverse-on-surface | N20 / N95 | N90 / N20 | `bg-inverse-surface` |
| scrim / shadow | N0 | N0 | `bg-scrim` |

Extra system colors used by snackbars: `--md-sys-color-inverse-success|warning|error` (tone 80 in
light, 40 in dark, readable on inverse-surface).

Scrims: `--color-overlay` = scrim at 32%.

## Typography (`text-*` utilities; size/line-height in px, tracking)

| Role | Large | Medium | Small | Weight |
|---|---|---|---|---|
| display | 57/64, -0.25 | 45/52, 0 | 36/44, 0 | 400 |
| headline | 32/40 | 28/36 | 24/32 | 400 |
| title | 22/28, 0 (400) | 16/24, 0.15 | 14/20, 0.1 | 500 (large 400) |
| body | 16/24, 0.5 | 14/20, 0.25 | 12/16, 0.4 | 400 |
| label | 14/20, 0.1 | 12/16, 0.5 | 11/16, 0.5 | 500 |

Element defaults: `body` = body-large; `h1` headline-large, `h2` headline-medium, `h3` headline-small,
`h4` title-large, `h5` title-medium, `h6` title-small. Font: Roboto (`--font-brand`, `--font-plain`;
aliases `--font-heading`, `--font-body`, `--font-sans`).

## Shape (`--md-sys-shape-corner-*`)

none 0 · extra-small 4 (`rounded-xs`) · small 8 (`rounded-sm`) · medium 12 (`rounded-md`) · large 16
(`rounded-lg`) · large-increased 20 (`rounded-xl`) · extra-large 28 (`rounded-2xl`) ·
extra-large-increased 32 (`rounded-3xl`) · extra-extra-large 48 (`rounded-4xl`) · full (`rounded-full`).
`data-radius="soft"` halves them; `"sharp"` zeroes all, including full.

## Elevation (`--md-sys-elevation-level0..5`, `shadow-elevation-1..5`)

| Level | Typical |
|---|---|
| 0 | Flat surfaces, outlined/filled cards |
| 1 | Elevated card, elevated button, modal side sheet, filled button on hover |
| 2 | Menu, autocomplete results, elevated card on hover |
| 3 | Dialog, snackbar, FAB |
| 4 | FAB on hover |
| 5 | (rare) |

`.elevation-1/2/3` = matching surface-container role + shadow. `--shadow-card` is what `.card` and
panels use; it's set by `data-shadow`.

## State layers

`--md-sys-state-hover-state-layer-opacity` 0.08, `focus` 0.10, `pressed` 0.10, `dragged` 0.16
(percent twins `--wise-state-hover` etc. for `color-mix`). Implementation:

```css
:where(.btn, .menu-link, /* ...add yours... */) {
    --wise-state-layer: color-mix(in srgb, currentColor var(--wise-state-opacity, 0%), transparent);
    background-image: linear-gradient(var(--wise-state-layer), var(--wise-state-layer));
}
:where(...):hover { --wise-state-opacity: var(--wise-state-hover); }
```

For table rows use `background-color: color-mix(in srgb, var(--md-sys-color-on-surface) var(--wise-state-hover), transparent)` on the cells.

Disabled: `--wise-disabled-content` (on-surface 38%) and `--wise-disabled-container` (on-surface 12%).
Focus ring: `--focus-ring-width` 3px, `--focus-ring-offset` 2px, `--focus-ring-color` secondary.

## Motion

Easing: `--md-sys-motion-easing-standard` `cubic-bezier(0.2,0,0,1)` (Tailwind default, `ease-standard`),
`-standard-decelerate` `(0,0,0,1)`, `-standard-accelerate` `(0.3,0,1,1)`, `-emphasized` `(0.2,0,0,1)`,
`-emphasized-decelerate` `(0.05,0.7,0.1,1)` (enter), `-emphasized-accelerate` `(0.3,0,0.8,0.15)` (exit).
Durations `--md-sys-motion-duration-short1..4` 50/100/150/200ms, `medium1..4` 250/300/350/400ms,
`long1..4` 450–600ms. Small component state changes: short4 standard. Sheets/dialogs entering: medium2
emphasized-decelerate.

## Density

| Token | Default | `data-density="compact"` |
|---|---|---|
| `--control-height-sm / -md / -lg` | 40 / 56 / 64px | 32 / 40 / 48px |
| `--control-height-button` | 40px | 32px |
| `--control-padding-x-button` | 24px | 16px |
| `--control-padding-y` | 16px | 8px |
| `--list-item-height` | 56px | 40px |
| `--menu-item-height` | 48px | 36px |
| `--table-padding-y / --table-header-padding-y` | 14 / 16px | 6 / 10px |

## Z-index

`--z-dropdown` 30 · `--z-sticky` 40 · `--z-drawer` 50 · `--z-dialog` 60 · `--z-toast` 70 · `--z-tooltip` 80.
