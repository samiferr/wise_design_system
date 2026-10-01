---
name: lumen-design
description: Build or restyle UI in the Wise Design System the Lumen way - a calm, neutral-first, Spectrum-style system: semantic color tokens over a gray + hue palette, Source Sans 3 type scale, pill buttons and 8px fields, layers and borders instead of shadows, hover/press fill steps, 2px focus ring - using this repo's Lumen tokens and component classes. Use whenever writing or reviewing Django templates, Tailwind classes or CSS in this repo or in a project that consumes wise_core; when adding a component to tokens.css; when changing colors, fonts, radii or shadows; or when asked to rebrand, pick an accent color, or make something "look like Lumen".
---

# Lumen in the Wise Design System

`wise_core/static/wise_core/css/tokens.css` implements Lumen on Tailwind CSS v4. Lumen is a calm,
neutral-first system for dense productivity software that follows Adobe Spectrum's structure: a
small palette, semantic tokens that reference it, a size scale tied to component heights, and
pill-and-rounded-rectangle controls. Your job is to stay inside that system: **compose existing
component classes and Lumen token utilities; never invent raw colors, radii, shadows or font
sizes.**

## The six rules

1. **Color = semantic tokens, never hex.** Use `bg-background-layer-1`, `text-content-subdued`,
   `border-border-subtle`, `bg-accent-background`. Always pair a fill with its own `on-` token
   (`bg-accent-background text-on-accent`, `bg-neutral-background text-on-neutral`,
   `bg-notice-background text-on-notice`). No `text-white`, no `bg-[#...]`, no `dark:` variants:
   tokens already flip in dark mode. Palette steps like `--lumen-blue-900` are for charts and
   illustration only.
2. **One accent, one main action.** The accent hue (blue by default; `data-palette` swaps it) fills
   the single main action per view (`btn-primary`) and colors links (`text-accent-content`). Everything
   else is neutral: `btn-brand` (neutral fill), `btn-secondary` (outline), `btn-ghost` (quiet).
3. **Type = the Lumen scale.** `text-heading-*` (800), `text-title-*` (700), `text-body-*` (400),
   `text-detail-*` (500), and `font-mono text-code-*`. Body copy is `body-m` (16px); controls and
   labels are `title-s` / `detail-m` (14px). Don't combine them with `text-sm`/`font-semibold`/
   `tracking-*`. **Sentence case**: never `uppercase`.
4. **Shape = Lumen's corner radii.** Buttons, badges, switches, status dots and progress tracks are
   fully round; fields, pickers, cards, alerts and nav items are 8px (`rounded-md`); checkboxes and
   tags 4px (`rounded-xs`); menus and popovers 10px (`rounded-lg`); dialogs 16px (`rounded-xl`).
   Use the component, or those utilities.
5. **A gray canvas with white surfaces; layers and borders, not shadows.** The page
   (`background-base`) is one fixed gray - it is not a setting, never override it - and everything on
   it is a surface: raised panel `background-layer-1`, card/field `background-layer-2`,
   popover/dialog `background-elevated`. In light all three are white (so **cards are white**); in dark
   they step up from near-black. Cards use a `border-subtle` edge. Put quiet regions inside a surface
   (table header, hovered row) on `fill-neutral-subtle`. Shadows (`shadow-emphasized`, `shadow-elevated`,
   `shadow-dragged`) only for things that float: menus, toasts, dialogs. A control's own border is
   `border-default` (3:1 on the page and every surface); `border-subtle` is for decorative dividers only.
6. **Interaction = stepped fills.** Hover moves a fill one shade, press two; the component classes
   already do this. Don't hand-write hover colors - add the selector to the quiet-hover `:where(...)`
   rule in `tokens.css`. Every interactive element shows a 2px `focus-ring` outline (offset 2px) on
   keyboard focus; don't remove it.

## Pick the component first

Before writing markup, find the existing class. Full table with markup in
[references/components.md](references/components.md). The common ones:

| Need | Wise class |
|---|---|
| Accent / neutral fill / neutral outline / quiet / raised / negative button | `btn btn-primary` / `btn btn-brand` / `btn btn-secondary` / `btn btn-ghost` / `btn btn-elevated` / `btn btn-danger` |
| Button sizes | default 32px (40px on touch), `btn-sm` 24px, `btn-lg` 40px, `btn-xl` 48px |
| Icon button | `btn-icon` (+ `btn-ghost` / `btn-secondary` / `btn-primary`), always with `aria-label` |
| Segmented / action group | `btn-group` > `btn` (selected: `.selected`) |
| Card | `card` / `card card-outlined` / `card card-elevated` / `card card-filled` |
| Text field, select, textarea | `input`, `select`, `textarea`, or any control inside `.form-field` |
| Checkbox / radio / switch | `input.checkbox` / `input.radio` / `input.switch` (also automatic inside `.form-field`) |
| Tag | `tag` (`tag tag-action` = selected) |
| Badge (status pill) | `badge badge-green|orange|red|action|brand|tertiary|grey`, `badge-count` |
| Status light | `status-light status-light-positive|notice|negative|informative|purple|cyan` |
| Inline alert | `callout callout-info|success|warning|danger` (+ `.callout-icon`, `.callout-title`) |
| Menu | `details.dropdown` > `summary` + `.dropdown-panel` > `.dropdown-item` |
| Dialog | `dialog.dialog` > `.dialog-header/.dialog-title/.dialog-body/.dialog-footer` |
| Side sheet | `.drawer` (+ `.drawer-left`) with `.drawer-backdrop` |
| Toast | `.toast` (+ `-success/-error/-warning/-info`) in `.toast-stack` (Django messages: `.flash-messages`, automatic) |
| Tabs | `.tab-bar` > `.bar-item` (`.selected`, optional `.tab-count`) |
| Side-nav item | `.menu-link` (`.selected`), `.tree-leaf` |
| Progress | `.progress > .progress-value` / `.progress-ring`, `.spinner` |
| Tooltip | `.tooltip[data-tooltip]` |
| List-page layout, forms, CRUD pages | the generic templates in `wise_core/templates/wise_core/generic/`; don't rebuild them |

If nothing fits, build from tokens (below) and, if it's reusable, add it to `tokens.css` following
[references/authoring.md](references/authoring.md).

## Tokens cheat sheet

Details and values: [references/tokens.md](references/tokens.md).

- **Tailwind color tokens** (`bg-`/`text-`/`border-` + name): `background-base`, `background-layer-1`,
  `background-layer-2`, `background-elevated`, `fill-neutral-hover`, `fill-neutral-down`,
  `fill-neutral-subtle` (Wise extension),
  `content-heading`, `content-default`, `content-subdued`, `content-disabled`, `border-default`,
  `border-hover`, `border-subtle`, `accent-background` (+ `-hover`, `-down`), `accent-content`,
  `on-accent`, `accent-subtle` / `on-accent-subtle` (Wise extension), `neutral-background`,
  `on-neutral`, `informative-` / `positive-` / `notice-` / `negative-background` and `-content`,
  `on-notice`, `focus-ring`. (`border-border-subtle` is the real utility name: Lumen's token is
  `border-subtle`, Tailwind's prefix is `border-`.)
- **In CSS:** `var(--color-content-default)`, `var(--corner-radius-500)`, `var(--shadow-elevated)`,
  `var(--border-width-200)`, `var(--component-height-100)`, `var(--control-height-md)`.
- **Which layer?** page `background-base` (the fixed gray), panels/sidebar `background-layer-1`,
  cards and fields `background-layer-2` (white), menus/popovers/dialogs `background-elevated`.
  Text and controls that sit directly on the page use the same tokens as everywhere else: they are
  all verified against the gray.
- **Which text color?** headings `content-heading`; body, labels, field values `content-default`;
  help text, captions, icons `content-subdued`; links and selected text `accent-content`; errors
  `negative-content`. `content-disabled` is never used for live content.
- **Which fill?** main action `accent-background`; neutral button / hover `fill-neutral-hover`;
  pressed / selected action `neutral-background`; destructive `negative-background`; status
  `positive-` / `notice-` / `informative-background`.
- **Density:** read `--control-height-md` (fields), `--control-height-button`, `--list-item-height`,
  `--menu-item-height`. Never hardcode component heights. Spacing is the 4px grid: Lumen's
  `spacing-75/100/200/300/400/600` are Tailwind `1/2/3/4/6/10`.
- **Legacy and Material 3 names** (`brand-*`, `action-*`, `accent-*`, `page`, `panel`, `divider`,
  `gray-*`, `primary`, `surface-container-*`, `on-surface`, `outline`, `--shadow-blueprint-*`,
  `text-body-large`, ...) still work as aliases. Don't write new code with them; when you touch a
  template that uses them, migrating is welcome (`text-action-600` → `text-accent-content`,
  `bg-panel` → `bg-background-layer-1`, `border-divider` → `border-border-subtle`,
  `text-gray-600/700` → `text-content-subdued`, `text-gray-900` → `text-content-heading`,
  `text-on-surface-variant` → `text-content-subdued`, `bg-primary` → `bg-accent-background`).

## Theming axes (runtime, on `<html>`)

`data-theme` light|dark · `data-palette` (blue)|indigo|purple|green|amber · `data-density`
comfortable|compact · `data-radius` (Lumen)|soft|sharp · `data-shadow` flat|soft|elevated. There is
deliberately no background axis. JS setters: `wiseSetTheme()` etc. in `wise_core/static/wise_core/js/common.js`.
Anything you build must look right under **every** combination, which it will as long as it only reads
tokens.

## Rebranding / new accent

The palette is generated, not hand-picked. Lumen's hues live in `scripts/lumen-scales.json`; the
accent options are `ACCENTS` in `scripts/generate_lumen_palettes.mjs`. Add a hue there, then
`npm run build:palettes && npm run build:css`. The script checks the contrast of every token pair in
both themes, every palette and every background, and refuses to write if one fails. Never hand-edit
`lumen-palettes.css`. To override the accent in one project without the generator, redefine
`--color-accent-background`, `-hover`, `-down`, `--color-accent-content` and `--color-focus-ring` in an
`@theme` block imported after `tokens.css`.

## Workflow

1. Map the request to components (table above). Reuse; don't restyle per-page.
2. Write markup with component classes + token utilities only. Layout utilities (`flex`, `gap-*`,
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
- No shadows to raise static content; use a layer step or a `border-subtle` edge. No custom
  `box-shadow` values.
- No more than one `btn-primary` per view; don't use the accent for decoration.
- Status is never color alone: pair `positive`/`notice`/`negative`/`informative` with a word and an icon.
- No `opacity-50` for disabled; use the `disabled` attribute (components handle the disabled colors).
- No hover color hacks (`hover:bg-gray-100`): add the selector to the quiet-hover rule instead.
- Don't rename or remove component classes: they are the public API.
