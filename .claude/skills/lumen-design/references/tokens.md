# Lumen token reference

Three tiers:

1. **Reference**: `--lumen-<hue>-<step>` for gray, blue, red, orange, yellow, green, celery, cyan,
   indigo, purple, fuchsia and magenta (16 steps, 100–1600; gray has 13, 25–1000), plus
   `--lumen-accent-<step>` (the accent option: blue, red, graphite or green, each grown from one OKLCH
   color) and `--lumen-swatch-<option>` (each option's fill). Every step has a light and a dark value, so a step flips
   with the theme. Generated into `wise_core/static/wise_core/css/lumen-palettes.css` by
   `scripts/generate_lumen_palettes.mjs` from `scripts/lumen-scales.json`. Components and templates
   never use them (charts and illustration may).
2. **System**: the Lumen semantic tokens, registered as Tailwind theme colors (`--color-*`) in
   `@theme static` in `tokens.css`; the few that read a different step in dark are re-pointed in
   `:root[data-theme="dark"]`. Non-color system tokens (`--corner-radius-*`, `--component-height-*`,
   `--border-width-*`) are plain custom properties in a `:root` block.
3. **Compat**: Material 3 role names, M3 type names and pre-M3 names, as aliases onto the system tier.

Lumen's palette, spacing, radius, type-size and component-height values are adapted from Adobe's
open-source Spectrum design tokens (Apache License 2.0). Lumen is not affiliated with or endorsed by
Adobe.

## Color tokens (light / dark step)

| Token | Light | Dark | Tailwind |
|---|---|---|---|
| background-base (the fixed gray page) | gray-100 | gray-25 | `bg-background-base` |
| background-layer-1 (white in light) | gray-25 | gray-50 | `bg-background-layer-1` |
| background-layer-2 (cards, fields: white in light) | gray-25 | gray-75 | `bg-background-layer-2` |
| background-elevated (white in light) | gray-25 | gray-75 | `bg-background-elevated` |
| fill-neutral-hover / -down | gray-200 / 300 | gray-100 / 200 | `bg-fill-neutral-hover` |
| fill-neutral-subtle (Wise extension) | gray-75 | gray-100 | `bg-fill-neutral-subtle` |
| content-heading | gray-900 | gray-900 | `text-content-heading` |
| content-default | gray-800 | gray-800 | `text-content-default` |
| content-subdued | gray-700 | gray-700 | `text-content-subdued` |
| content-disabled | gray-400 | gray-400 | `text-content-disabled` |
| border-default | gray-600 | gray-600 | `border-border-default` |
| border-hover | gray-700 | gray-700 | `border-border-hover` |
| border-focus | gray-900 | gray-900 | `border-border-focus` |
| border-field | gray-300 (#dadada) | gray-300 | `border-border-field` (every text field, text area, listbox, OTP box; soft by design) |
| fill-picker / -hover | gray-300 (#dadada) / 400 | gray-300 / 400 | `bg-fill-picker` (the borderless select) |
| border-subtle | gray-300 | gray-300 | `border-border-subtle` |
| border-popover | transparent | gray-400 | `border-border-popover` |
| negative-border / -hover | red-900 / 1000 | red-900 / 1000 | `border-negative-border` |
| fill-disabled / border-disabled | gray-100 / gray-300 | gray-100 / gray-300 | `bg-fill-disabled` |
| row-hover | 7% gray-900 | 7% gray-900 | `bg-row-hover` |
| selected-subtle / -hover | 10% / 15% accent-900 | 10% / 15% accent-900 | `bg-selected-subtle` |
| neutral- / informative- / positive- / notice- / negative-`subtle` | gray-75, blue / green / orange / red-200 | same step names | `bg-negative-subtle` |
| accent-background | accent-900 | accent-800 | `bg-accent-background` |
| accent-background-hover | accent-1000 | accent-700 | `bg-accent-background-hover` |
| accent-background-down | accent-1100 | accent-600 | `bg-accent-background-down` |
| accent-content | accent-1000 | accent-1000 | `text-accent-content` |
| on-accent | white | white | `text-on-accent` |
| accent-subtle / on-accent-subtle (Wise extension) | accent-200 / 1300 | same step names | `bg-accent-subtle` |
| neutral-background / on-neutral | gray-800 / gray-25 | gray-800 / gray-25 | `bg-neutral-background` |
| negative-background (+ `-hover`, `-down`) | red-900 (1000, 1100) | red-800 (700, 600) | `bg-negative-background` |
| negative-content | red-1000 | red-1000 | `text-negative-content` |
| informative-background / -content | blue-900 / 1000 | blue-800 / 1000 | `bg-informative-background` |
| positive-background / -content | green-900 / 1000 | green-800 / 1000 | `bg-positive-background` |
| notice-background | orange-600 | orange-900 | `bg-notice-background` |
| on-notice | gray-900 | black | `text-on-notice` |
| notice-content | orange-1000 | orange-1000 | `text-notice-content` |
| focus-ring | accent-800 | accent-800 | `ring-focus-ring` |

Text on a filled control is always its own `on-` token. Because a Lumen hue step flips with the theme,
"gray-900" is near-black in light and near-white in dark; you never pick per theme.

Toasts and tooltips use `neutral-background` / `on-neutral`. Scrim: `--color-overlay` = black at 40%.

### Material 3 compat aliases

`primary` → accent-background · `on-primary` → on-accent · `primary-container` → accent-subtle ·
`secondary` → neutral-background · `secondary-container` → fill-neutral-hover · `tertiary(-container)` →
purple · `error` → negative-background · `error-container` → red-200 · `success` / `warning` →
positive / notice-background · `surface` → background-base · `surface-container-low` →
background-layer-1 · `surface-container` → gray-75 · `surface-container-high` → fill-neutral-hover ·
`surface-container-highest` → fill-neutral-down · `on-surface` → content-default ·
`on-surface-variant` → content-subdued · `outline` → border-default · `outline-variant` →
border-subtle · `inverse-surface` → neutral-background. `-fixed` roles and the `--md-sys-*` /
`--md-ref-*` custom properties no longer exist.

## Typography (`text-*` utilities; size px, line height, weight)

| Style | Sizes | Line height | Weight |
|---|---|---|---|
| heading | xxs 14 · xs 18 · s 20 · m 22 · l 28 · xl 36 · xxl 45 · xxxl 58 · xxxxl 73 | 1.3 | 800 |
| title | xs 12 · s 14 · m 16 · l 18 · xl 20 · xxl 22 · xxxl 25 | 1.3 | 700 |
| body | xxs 11 · xs 12 · s 14 · m 16 · l 18 · xl 20 · xxl 22 · xxxl 25 | 1.5 | 400 |
| detail | xs 11 · s 12 · m 14 · l 16 · xl 18 | 1.3 | 500 |
| code | xs 12 · s 14 · m 16 · l 18 · xl 20 (pair with `font-mono`) | 1.5 | 400 |

Element defaults: `body` = body-m; `h1` heading-l, `h2` heading-m, `h3` heading-s, `h4` title-l, `h5`
title-m, `h6` title-s, all in `content-heading`. Font: Source Sans 3 (`--font-brand`, `--font-plain`;
aliases `--font-heading`, `--font-body`, `--font-sans`), code in Source Code Pro (`--font-mono`).
Sizes are the desktop scale; add about 20% on touch.

M3 type names still resolve: `display-large/medium/small` → heading-xxxl/xxl/xl, `headline-*` →
heading-l/m/s, `title-large/medium/small` → title-xl/m/s, `body-large/medium/small` → body-m/s/xs,
`label-large/medium/small` → detail-m/s/xs.

## Shape (`--corner-radius-*`)

0 · 75 (3px) · 100 (4px, `rounded-xs`: checkboxes, tags) · 200 (5) · 300 (6px, `rounded-sm`) · 400 (7:
menu items) · 500 (8px, `rounded-md`: fields, cards, alerts, nav items) · 600 (9) · 700 (10px,
`rounded-lg`: popovers) · 800 (16px, `rounded-xl`/`2xl`: dialogs) · full (`rounded-full`: buttons,
badges, switches, progress tracks). `rounded-3xl` / `4xl` are 800 × 1.25 / × 1.5.
`data-radius="soft"` halves them; `"sharp"` zeroes all, including full.

## Layers and shadow

Layers: base (the fixed gray page) → layer-1 (panels) → layer-2 (cards, fields) → elevated (popovers,
dialogs); in light all three surfaces are white, in dark they step up from near-black. Shadows:
`--shadow-emphasized` (`0 1px 6px`, resting raised control), `--shadow-elevated` (`0 2px 8px`, menus,
popovers, tooltips, toasts), `--shadow-dragged` (`0 6px 16px`, dialogs, dragged items); alpha .15 in
light, .5 in dark. `shadow-elevation-1..5` and `--shadow-blueprint-*` alias onto them. `.elevation-1/2/3`
= matching layer + shadow. `--shadow-card` is what `.card` and panels use; it's set by `data-shadow`
(flat = none, soft = emphasized, elevated = elevated).

## Hover, press, disabled, focus

No overlay layers. Filled controls step their fill: `accent-background` → `-hover` → `-down` (negative
likewise); neutral buttons `fill-neutral-hover` → `fill-neutral-down`; outlined, quiet and list-row
items fill with `fill-neutral-hover` then `-down` (the quiet-hover `:where(...)` rule in `tokens.css`);
items on a colored surface (toast close, tag remove) use `color-mix(currentColor 16% / 24%)`.
Disabled: `--wise-disabled-content` (content-disabled) on `--wise-disabled-container`
(fill-neutral-hover). Focus ring: `--focus-ring-width` 2px, `--focus-ring-offset` 2px,
`--focus-ring-color` focus-ring, drawn on `:focus-visible` by one base rule.

## Motion

`--default-transition-duration` 130ms (Tailwind default too) for hover, press and color changes;
`--ease-standard` `cubic-bezier(0.4,0,0.2,1)`, `--ease-enter` `(0,0,0.2,1)` for things arriving
(dialog, drawer: 200ms), `--ease-exit` `(0.4,0,1,1)`. Animate color, opacity and transform only;
honour `prefers-reduced-motion`.

## Control heights

| Token | Default | Coarse pointer |
|---|---|---|
| `--control-height-sm / -md / -lg` | 24 / 32 / 40px | 32 / 40 / 48px |
| `--control-height-button` | 32px | 40px |
| `--control-padding-x-button` | 16px | 16px |
| `--control-padding-y` | 4px | 4px |
| `--list-item-height` | 32px | 40px |
| `--menu-item-height` | 32px | 40px |
| `--table-padding-y` | 8px | 8px |

There is no compact density mode: density is not a setting.

Lumen's own heights: `--component-height-50..500` = 20 / 24 / 32 / 40 / 48 / 56 / 64px.

## Spacing

Lumen's `spacing-*` tokens are all multiples of the 4px grid, so use Tailwind's scale: 75 → `1` (4px),
100 → `2` (8), 200 → `3` (12), 300 → `4` (16), 350 → `5` (20), 400 → `6` (24), 500 → `8` (32),
600 → `10` (40), 700 → `12` (48), 800 → `16` (64). Window margins 16px compact, 24px from `sm`
(`.page-panel` does this).

## Z-index

`--z-dropdown` 30 · `--z-sticky` 40 · `--z-drawer` 50 · `--z-dialog` 60 · `--z-toast` 70 · `--z-tooltip` 80.
