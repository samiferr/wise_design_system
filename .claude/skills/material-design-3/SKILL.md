---
name: material-design-3
description: Build or restyle UI in the Wise Design System the Material Design 3 (M3, https://m3.material.io/) way - color roles, type scale, shape, elevation, state layers, motion - using this repo's M3 tokens and component classes. Use whenever writing or reviewing Django templates, Tailwind classes or CSS in this repo or in a project that consumes wise_core; when adding a component to tokens.css; when changing colors, fonts, radii or shadows; or when asked to make something "look Material", rebrand, or pick a color.
---

# Material Design 3 in the Wise Design System

`wise_core/static/wise_core/css/tokens.css` implements Material Design 3 on Tailwind CSS v4. Your
job is to stay inside that system: **compose existing component classes and M3 token utilities;
never invent raw colors, radii, shadows or font sizes.**

## The five rules

1. **Color = roles, never hex.** Use M3 role utilities (`bg-primary`, `text-on-surface-variant`,
   `bg-surface-container-high`, `border-outline-variant`). Always pair a container with its own `on-`
   role (`bg-secondary-container text-on-secondary-container`). No `text-white`, no `bg-[#...]`, no
   `dark:` variants: roles already flip in dark mode.
2. **Type = the M3 scale.** `text-display-*`, `text-headline-*`, `text-title-*`, `text-body-*`,
   `text-label-*` (each `-large|-medium|-small`). Don't combine them with `text-sm`/`font-semibold`/
   `tracking-*`. **Sentence case**: never `uppercase`.
3. **Shape = the M3 corner scale**, via the component or `rounded-xs` (4) / `rounded-sm` (8) /
   `rounded-md` (12) / `rounded-lg` (16) / `rounded-2xl` (28) / `rounded-full`. Buttons, nav items
   and switches are pills; cards 12; dialogs 28; fields and menus 4; chips 8.
4. **Elevation is tonal first.** Raise a surface by picking a higher `surface-container-*` role.
   Shadows (`shadow-elevation-1..5`) only for things that float: menus 2, dialogs/snackbars 3, FAB 3.
5. **Interaction = state layers.** Don't hand-write hover colors. Interactive components get an
   8% hover / 10% focus / 10% pressed overlay of their content color from one `:where(...)` rule at the
   top of `@layer components` in `tokens.css`. Add new interactive selectors to that rule.

## Pick the component first

Before writing markup, map the M3 component you want to the existing class. Full table with markup
in [references/components.md](references/components.md). The common ones:

| M3 component | Wise class |
|---|---|
| Filled / tonal / outlined / text / elevated button | `btn btn-primary` / `btn btn-brand` / `btn btn-secondary` / `btn btn-ghost` / `btn btn-elevated` (M3 aliases: `btn-filled`, `btn-tonal`, `btn-outlined`, `btn-text`) |
| Destructive filled button | `btn btn-danger` |
| Icon button (standard / outlined / filled) | `btn-icon` (+ `btn-ghost` / `btn-secondary` / `btn-primary`), always with `aria-label` |
| FAB / extended FAB | `fab` / `fab fab-extended` |
| Segmented button | `btn-group` > `btn` (selected: `.selected`) |
| Card (follows data-shadow / outlined / elevated / filled) | `card` / `card card-outlined` / `card card-elevated` / `card card-filled` |
| Outlined text field, select, textarea | `input`, `select`, `textarea`, or any control inside `.form-field` |
| Chip (input/filter, selected) | `tag` (`tag tag-action`) |
| Status label / notification badge | `badge badge-green|orange|red|grey|action|brand|tertiary` / `badge-count` |
| Menu | `details.dropdown` > `summary` + `.dropdown-panel` > `.dropdown-item` |
| Dialog | `dialog.dialog` > `.dialog-header/.dialog-title/.dialog-body/.dialog-footer` |
| Side sheet | `.drawer` (+ `.drawer-left`) with `.drawer-backdrop` |
| Snackbar | `.toast` in `.toast-stack` (Django messages: `.flash-messages`, automatic) |
| Primary tabs | `.tab-bar` > `.bar-item` (`.selected`, optional `.tab-count`) |
| Navigation drawer item | `.menu-link` (`.selected`), `.tree-leaf` |
| Linear / circular progress | `.progress > .progress-value` / `.progress-ring`, `.spinner` |
| Switch / checkbox / radio | `input.switch` / `.checkbox` / `.radio` |
| Tooltip | `.tooltip[data-tooltip]` |
| List-page layout, forms, CRUD pages | the generic templates in `wise_core/templates/wise_core/generic/`; don't rebuild them |

If nothing fits, build from tokens (below) and, if it's reusable, add it to `tokens.css` following
[references/authoring.md](references/authoring.md).

## Tokens cheat sheet

Details and values: [references/tokens.md](references/tokens.md).

- **Color roles** (Tailwind `bg-/text-/border-` + name): `primary`, `on-primary`, `primary-container`,
  `on-primary-container`, `secondary(-container)`, `tertiary(-container)`, `error(-container)`,
  `success(-container)`, `warning(-container)` (each with `on-`), `surface`,
  `surface-container-lowest|low|(none)|high|highest`, `on-surface`, `on-surface-variant`, `outline`,
  `outline-variant`, `inverse-surface`, `inverse-on-surface`, `inverse-primary`, `scrim`.
- **In CSS:** `var(--md-sys-color-<role>)`, `var(--md-sys-shape-corner-<size>)`,
  `var(--md-sys-elevation-level<n>)`, `var(--md-sys-motion-easing-standard)`,
  `var(--md-sys-motion-duration-short4)`.
- **Which surface?** page `surface`, cards/sheets `surface-container-low`, menus `surface-container`,
  dialogs `surface-container-high`, filled fields/chips/tracks `surface-container-highest`.
- **Which text color?** primary content `on-surface`; secondary text, icons, labels
  `on-surface-variant`; links and emphasis `primary`; errors `error`.
- **Which accent?** Most important action `primary`; selected/active state `secondary-container`;
  a contrasting highlight `tertiary-container`; destructive only `error`; status `success`/`warning`.
- **Density:** read `--control-height-md` (fields), `--control-height-button`, `--list-item-height`,
  `--menu-item-height`. Never hardcode component heights.
- **Legacy names** (`brand-*`, `action-*`, `accent-*`, `page`, `panel`, `divider`, `gray-*`,
  `--shadow-blueprint-*`) still work as aliases. Don't write new code with them; when you touch a
  template that uses them, migrating to the role names is welcome
  (`text-action-600` → `text-primary`, `bg-panel` → `bg-surface-container-low`,
  `border-divider` → `border-outline-variant`, `text-gray-600` → `text-on-surface-variant`,
  `text-gray-900` → `text-on-surface`).

## Theming axes (runtime, on `<html>`)

`data-theme` light|dark · `data-palette` (baseline #6750A4)|green|blue|amber · `data-density`
comfortable|compact · `data-radius` (M3)|soft|sharp · `data-shadow` flat|soft|elevated · `data-bg`
(tonal)|warm|cool. JS setters: `wiseSetTheme()` etc. in `wise_core/static/wise_core/js/common.js`.
Anything you build must look right under **every** combination, which it will as long as it only
reads tokens.

## Rebranding / new palette

Palettes are generated, not hand-picked. Edit `PALETTES` in `scripts/generate_m3_palettes.mjs` (the
`null` entry is the default), then `npm run build:palettes && npm run build:css`. Never hand-edit
`md3-palettes.css`. A consuming project can instead paste a Material Theme Builder export of
`--md-sys-color-*` into `:root` / `:root[data-theme="dark"]` after `tokens.css`.

## Workflow

1. Map the request to M3 components (table above). Reuse; don't restyle per-page.
2. Write markup with component classes + role/type utilities only. Layout utilities (`flex`, `gap-*`,
   `p-*`, `grid`) are fine; the spacing grid is 4px (use even Tailwind steps: `gap-2`, `p-4`, `p-6`).
3. If you edited `tokens.css`, `input.css` or any template, run `npm run build:css` (Tailwind only
   emits utilities it finds in templates).
4. Verify in **light and dark**, and ideally one other palette and `data-density="compact"`. The demo
   site: `cd demo && python manage.py runserver` → `/docs/` (component catalog), `/demo/` (login
   `demo` / `wise-demo-2026`).
5. Run the checklist in [references/review-checklist.md](references/review-checklist.md) before
   finishing.

## Don'ts

- No hex/rgb/hsl colors, no `bg-white`/`text-black`/`text-white`, no Tailwind palette colors
  (`bg-blue-500`, `text-emerald-700`) in templates.
- No `uppercase`, `tracking-wider`, `font-bold` headings, or `text-[11px]`-style one-off sizes.
- No borders to separate every region: M3 separates with tone and space. Use `outline-variant`
  dividers sparingly.
- No custom `box-shadow` values; no shadows on static cards unless `data-shadow` asks for it.
- No `opacity-50` for disabled; use the `disabled` attribute (components handle 38%/12%).
- No hover color hacks (`hover:bg-gray-100`): add the selector to the state-layer rule instead.
- Don't rename or remove component classes: they are the public API.
