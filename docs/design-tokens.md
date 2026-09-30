# Design tokens

Source: [`wise_core/static/wise_core/css/tokens.css`](../wise_core/static/wise_core/css/tokens.css)
plus the generated [`md3-palettes.css`](../wise_core/static/wise_core/css/md3-palettes.css) it
imports. Together they are a Tailwind CSS v4 partial (an `@theme` block plus `@layer
base`/`components`/`utilities`) styled after **[Material Design 3](https://m3.material.io/)**. See
[getting-started.md](getting-started.md) for how a project builds this into a real stylesheet.

Live, rendered version: run the demo site and visit `/docs/theming/design-tokens/` and
`/docs/theming/color-palettes/`. Every example there is a real, running control. AI agents: the
[Material Design 3 skill](../.claude/skills/material-design-3/SKILL.md) is the condensed version
of this page, plus the M3-component → Wise-class mapping.

## Token tiers

The same three tiers Material 3 itself uses:

| Tier | Names | Where | Use it for |
|---|---|---|---|
| Reference | `--md-ref-palette-<palette><tone>` (e.g. `--md-ref-palette-primary40`) | `md3-palettes.css`, generated | Nothing directly. System tokens point at these. |
| System | `--md-sys-color-*`, `--md-sys-shape-corner-*`, `--md-sys-elevation-level*`, `--md-sys-motion-*`, `--md-sys-state-*` | `tokens.css` | Hand-written CSS (`var(--md-sys-color-primary)`) |
| Tailwind | `--color-primary`, `--text-title-medium`, `--radius-md`, `--shadow-elevation-2`, `--ease-standard`, ... | `tokens.css` `@theme static` | Templates (`bg-primary`, `text-title-medium`, `rounded-md`, `shadow-elevation-2`) |

## Color

M3 dynamic color. A **seed color** is expanded by Google's
[`@material/material-color-utilities`](https://github.com/material-foundation/material-color-utilities)
into tonal palettes: primary, secondary, tertiary, neutral, neutral-variant and error, plus
harmonized **success** and **warning** (M3 "custom colors"). Each palette has tones 0–100.
**Color roles** then pick tones: `primary` = primary40 in light and primary80 in dark,
`on-primary` = primary100 / primary20, and so on. Components only ever use roles, so contrast holds
in every palette and both themes.

| Role (Tailwind utility suffix) | Use |
|---|---|
| `primary` / `on-primary` | Filled buttons, the most important action, active indicators, links |
| `primary-container` / `on-primary-container` | FAB, info callouts, highlighted accents |
| `secondary` / `secondary-container` / `on-secondary-container` | Tonal buttons, selected nav item, selected chip or segment |
| `tertiary` / `tertiary-container` / `on-tertiary-container` | Contrasting accents |
| `error` / `error-container` / `on-error(-container)` | **Destructive and error only** |
| `success-*`, `warning-*` | Status: done / needs attention (same four-role shape as error) |
| `surface`, `surface-dim`, `surface-bright` | The page |
| `surface-container-lowest/low/(none)/high/highest` | Tonal elevation: cards & sheets (low), menus (container), dialogs (high), filled fields & chips (highest) |
| `on-surface` / `on-surface-variant` | Body text / secondary text and icons |
| `outline` / `outline-variant` | Field and outlined-button borders / dividers and card outlines |
| `inverse-surface` / `inverse-on-surface` / `inverse-primary` | Snackbars, tooltips |
| `scrim`, `shadow` | Modal backdrops, shadows |

```html
<button class="bg-primary text-on-primary">Filled</button>
<div class="bg-surface-container-high text-on-surface rounded-2xl p-6">Dialog-like surface</div>
<p class="text-on-surface-variant">Secondary text</p>
<span class="bg-tertiary-container text-on-tertiary-container rounded-sm px-2">Accent</span>
<hr class="border-outline-variant">
```

Always pair a container with its own `on-` role, and never hardcode `text-white`: in dark mode the
filled roles become light tones and need a dark label.

### Legacy color names

The pre-M3 names still exist as aliases, so older templates render correctly, but new markup should
use the roles above:

| Legacy | Now points at |
|---|---|
| `brand-*`, `action-*` | primary palette tones (`action-600` = `primary`, `action-100` = `primary-container`, `action-700` = `on-primary-container`) |
| `accent-*` | error roles (`accent-500` = `error`, `accent-50` = `error-container`) |
| `warning-50/500/600` | `warning-container` / `warning` / `on-warning-container` |
| `page`, `panel`, `panel-alt`, `divider` | `surface`, `surface-container-low`, `surface-container`, `outline-variant` |
| `surface` | **now the M3 `surface` role** (the page). It used to be the input fill; M3 outlined fields are transparent. |
| `on-action`, `on-brand`, `on-accent` | `on-primary`, `on-primary`, `on-error` |
| `gray-50..950` | M3 neutral tones: `gray-900` = on-surface, `gray-600` = on-surface-variant, `gray-500` = outline, `gray-300` = outline-variant. Inverts in dark mode. |
| `--shadow-blueprint-sm/md/lg` | `--md-sys-elevation-level1/2/3` |

### Rebranding

Add a seed to `PALETTES` in [`scripts/generate_m3_palettes.mjs`](../scripts/generate_m3_palettes.mjs)
(or change the `null` entry, which is the default palette) and run:

```bash
npm run build:palettes && npm run build:css
```

In a consuming project that doesn't want to run the generator, export a scheme from
[Material Theme Builder](https://material-foundation.github.io/material-theme-builder/) and paste its
`--md-sys-color-*` values into `:root { ... }` and `:root[data-theme="dark"] { ... }` blocks in your
own entry CSS, imported *after* `tokens.css`. Every component follows, since they only read those
system tokens.

## Typography

Roboto, vendored as a variable woff2 (weights 100–900, latin + latin-ext, OFL - see
`wise_core/static/wise_core/font/`). `--font-brand`/`--font-plain` are the M3 names;
`--font-heading`/`--font-body`/`--font-sans` alias them.

The M3 type scale, each role one Tailwind utility setting size, line height, tracking and weight:

| Utility | Size / line height | Weight | Default use |
|---|---|---|---|
| `text-display-large/medium/small` | 57/64, 45/52, 36/44 | 400 | Hero numbers and headlines |
| `text-headline-large/medium/small` | 32/40, 28/36, 24/32 | 400 | `h1`, `h2`, `h3`; dialog titles |
| `text-title-large/medium/small` | 22/28 (400), 16/24, 14/20 (500) | | `h4`, `h5`, `h6`; card titles, tabs, table headers |
| `text-body-large/medium/small` | 16/24, 14/20, 12/16 | 400 | Body (large is the page default), cells, help text |
| `text-label-large/medium/small` | 14/20, 12/16, 11/16 | 500 | Buttons, nav items, chips / badges / counts |

Headings get their role automatically. Sentence case everywhere: M3 never uppercases headings,
labels or buttons.

## Shape

The M3 corner scale, `--md-sys-shape-corner-*`, and Tailwind's radius scale mapped onto it:

| M3 token | Value | Tailwind | Used by |
|---|---|---|---|
| `extra-small` | 4px | `rounded-xs` | Text fields, menus, snackbars, tooltips |
| `small` | 8px | `rounded-sm` | Chips (`.tag`), badges |
| `medium` | 12px | `rounded-md` | Cards, detail panel, callouts, accordion |
| `large` | 16px | `rounded-lg` | Side sheets (`.drawer`), FAB, toolbar |
| `large-increased` | 20px | `rounded-xl` | |
| `extra-large` | 28px | `rounded-2xl` | Dialogs, carousel items |
| `full` | 9999px | `rounded-full` | Buttons, icon buttons, nav items, switches, avatars |

`data-radius="soft"` halves the scale; `data-radius="sharp"` zeroes all of it, pills included.
Things that are round by definition (spinner, donut, `.avatar-circle`) use a literal `9999px`.

## Elevation

M3 elevation is mostly **tonal** (a higher `surface-container-*` role). Shadows are for things that
float: `--md-sys-elevation-level1..5` / `shadow-elevation-1..5`. Menus use level 2, dialogs and
snackbars level 3, the FAB level 3 (4 on hover). `.elevation-1/2/3` utility classes apply the
matching surface *and* shadow together.

`.card`, `.detail-panel` and the other panels follow `data-shadow`: flat (default) = M3 **outlined**
card, soft/elevated = M3 **elevated** card (level 1/2). `.card-outlined`, `.card-elevated` and
`.card-filled` pin one type.

## State layers

Every interactive component paints the M3 state layer: an overlay of its own content color
(`currentColor`) at 8% on hover, 10% on focus-visible and 10% while pressed
(`--md-sys-state-*-state-layer-opacity`). It's one `:where(...)` rule in `tokens.css`; add your own
component's selector to it rather than writing hover colors by hand. Disabled: 38% `on-surface`
content on a 12% `on-surface` container.

Focus: the M3 focus indicator, a 3px `secondary` ring 2px out (`--focus-ring-width/-offset/-color`)
on every `:focus-visible`. Text fields use their own 2px `primary` outline instead.

## Motion

`--md-sys-motion-easing-standard` (`cubic-bezier(0.2, 0, 0, 1)`) is also Tailwind's default
transition easing, with a 200ms default duration. Emphasized decelerate/accelerate are for
entering/leaving elements. Durations `short1`–`long4` run 50–600ms. Utilities: `ease-standard`,
`ease-emphasized-decelerate`, ...

## Density

| Token | Comfortable (M3 density 0) | Compact |
|---|---|---|
| `--control-height-md` | 3.5rem (56px text field) | 2.5rem |
| `--control-height-sm` / `-lg` | 2.5rem / 4rem | 2rem / 3rem |
| `--control-height-button` | 2.5rem (40px button) | 2rem |
| `--control-padding-x-button` | 1.5rem | 1rem |
| `--list-item-height` | 3.5rem (nav item) | 2.5rem |
| `--menu-item-height` | 3rem | 2.25rem |
| `--table-padding-y` / `--table-header-padding-y` | 0.875rem / 1rem | 0.375rem / 0.625rem |

## Switchable axes

Six independent attributes on `<html>`, each redefining a handful of tokens at runtime (no rebuild,
no second stylesheet). They compose freely, because each touches a different tier: palette and
background swap reference tones, theme swaps which tone each system role reads. `base.html` applies
whatever's in `localStorage` before first paint; `wise_core/static/wise_core/js/common.js` exposes
one setter per axis, and `wise_core/components/_settings_panel.html` is a ready-made side sheet for
all six (open it with `wiseOpenDrawer('wise-settings-drawer')`, normally via
`_settings_toggle.html`). Its **Copy tokens** tab exports the current `data-*` line and the resolved
`--md-sys-*` values (see `WISE_EXPORT_TOKENS` in `common.js`).

| Attribute | Values | Retunes |
|---|---|---|
| `data-theme` | `light` (default), `dark` | Which palette tone every M3 color role reads |
| `data-palette` | baseline (default, seed `#6750A4`), `green`, `blue`, `amber` | The seed - every generated palette |
| `data-density` | `comfortable` (default), `compact` | Field, button, list-item and table heights |
| `data-radius` | M3 scale (default), `soft`, `sharp` | The whole corner scale |
| `data-shadow` | `flat` (default), `soft`, `elevated` | Outlined vs. elevated cards and panels |
| `data-bg` | tonal (default, seed-tinted), `warm`, `cool` | The neutral palettes behind every surface role |

```js
wiseSetTheme('dark')       // '' or 'light' resets to light
wiseSetPalette('blue')     // '' resets to the M3 baseline
wiseSetDensity('compact')  // '' resets to comfortable
wiseSetRadius('sharp')     // '' resets to the M3 shape scale
wiseSetShadow('elevated')  // '' resets to flat (outlined cards)
wiseSetBg('warm')          // '' resets to tonal
```

## Component class names

The component layer (`.btn`, `.card`, `.badge`, `.form-stack`, `.detail-panel`, `.data-table`,
`.menu-link`, `.tab-bar`, `.pagination-link`, ...) is the design system's real public API. The class
names stayed the same through the move to Material 3; only their look changed. Each maps onto an M3
component: `.btn-primary` is a filled button, `.btn-brand` tonal, `.btn-secondary` outlined,
`.btn-ghost` text, `.btn-group` a segmented button, `.tag` a chip, `.toast` a snackbar, `.drawer` a
side sheet, `.dropdown-panel` a menu, `.menu-link` a navigation-drawer item. M3-named aliases
(`.btn-filled`, `.btn-tonal`, `.btn-outlined`, `.btn-text`) and a few new M3 pieces (`.btn-elevated`,
`.fab`, `.card-elevated/-filled/-outlined`, `.badge-count`) sit alongside. The full mapping is in the
[Material Design 3 skill](../.claude/skills/material-design-3/references/components.md). See
[template-tags-and-filters.md](template-tags-and-filters.md) and
[generic-views-and-mixins.md](generic-views-and-mixins.md) for how the generic templates use them,
or the Components sections of `/docs/` for a rendered catalog.
