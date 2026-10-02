# Design tokens

Source: [`wise_core/static/wise_core/css/tokens.css`](../wise_core/static/wise_core/css/tokens.css)
plus the generated [`lumen-palettes.css`](../wise_core/static/wise_core/css/lumen-palettes.css) it
imports. Together they are a Tailwind CSS v4 partial (an `@theme` block plus `@layer
base`/`components`/`utilities`) styled after **Lumen**, a calm, neutral-first design system in the
Spectrum tradition: one neutral scale and a single accent hue, semantic tokens that reference a small
palette, a type scale in Source Sans 3, fully round buttons with 8px fields and cards, and layers and
borders instead of shadows. The page is one fixed gray canvas with white surfaces on it (cards, panels,
fields, popovers); the background is not a setting. See [getting-started.md](getting-started.md) for how a project builds this
into a real stylesheet.

Lumen's palette, spacing, radius, type-size and component-height values are adapted from Adobe's
open-source Spectrum design tokens (Apache License 2.0). Lumen is an independent system and is not
affiliated with or endorsed by Adobe.

Live, rendered version: run the demo site and visit `/docs/theming/design-tokens/` and
`/docs/theming/color-palettes/`. Every example there is a real, running control. AI agents: the
[Lumen design skill](../.claude/skills/lumen-design/SKILL.md) is the condensed version of this page,
plus the component → Wise-class mapping.

## Token tiers

| Tier | Names | Where | Use it for |
|---|---|---|---|
| Reference | `--lumen-<hue>-<step>` (e.g. `--lumen-blue-900`), `--lumen-accent-<step>` | `lumen-palettes.css`, generated | Charts and illustration. System tokens point at these. |
| System | `--color-background-base`, `--color-content-default`, `--color-accent-background`, ... `--text-*`, `--corner-radius-*`, `--shadow-*`, `--component-height-*`, `--border-width-*` | `tokens.css` (`@theme static` and `:root`) | Hand-written CSS (`var(--color-accent-background)`); the color and type tokens are also Tailwind theme values |
| Tailwind | `bg-accent-background`, `text-content-subdued`, `text-title-s`, `rounded-md`, `shadow-elevated`, ... | generated from the system tier | Templates |

## Color

Lumen color is one neutral scale (gray) and eleven hue scales (blue, red, orange, yellow, green, celery,
cyan, indigo, purple, fuchsia, magenta), each in numbered steps. **Every step has a light and a dark
value**, so a step flips with `data-theme` on its own. **Semantic tokens** pick steps, and components
only ever use semantic tokens, so contrast holds in every palette and both themes.

| Token (Tailwind utility suffix) | Use |
|---|---|
| `background-base` | The page: one fixed gray (gray-100 in light, near-black in dark). Not configurable |
| `background-layer-1` | Raised panels: the sidebar, the action bar, an empty state (white in light) |
| `background-layer-2` | Cards, tables and field fills (white in light) |
| `background-elevated` | Popovers, menus, dialogs, tooltips that float above the page (white in light) |
| `fill-neutral-hover` / `fill-neutral-down` | Hover and pressed fill for quiet buttons, list rows, tabs; the neutral button |
| `fill-neutral-subtle` | *Wise extension.* The faintest fill, for a quiet region inside a surface: a filled card, an autocomplete header, a calendar's outside days |
| `row-hover` / `selected-subtle` / `selected-subtle-hover` | Translucent row tints (7% content-heading; 10% / 15% accent) for a hovered, a selected and a selected-and-hovered table, list or tree row. Selection is never the tint alone |
| `fill-disabled` / `border-disabled` | A disabled field: its fill and outline, with `content-disabled` text |
| `content-heading` / `content-default` / `content-subdued` | Headings / body text and labels / help text, captions, icons |
| `content-disabled` | Disabled text. Never for live content |
| `border-default` / `border-hover` | A control's own border (3:1 on the page and every surface) / its hover |
| `border-focus` | A focused text field / text area: the 2px border turns this dark gray instead of drawing the ring (gray-900; Lumen's own is gray-800 - one step darker so the change from the resting border holds 3:1 on the gray canvas) |
| `fill-field` / `fill-field-hover` | The fill of every text field, text area, select, OTP box and the rich text editor: gray-300 (**#dadada** in light; it steps with the theme, so dark is #393939). A select has no border and deepens to `fill-field-hover` (gray-400) on hover |
| `border-subtle` | Decorative dividers and card edges only |
| `negative-border` / `negative-border-hover` | An invalid field's border: it stays 1px and changes color, with an icon and a message as the non-color cue |
| `border-popover` | A menu or picker popover's outline: none in light, 1px `gray-400` in dark |
| `accent-background` (+ `-hover`, `-down`) / `on-accent` | The single main action, selected checkbox / radio / switch; text on it |
| `accent-content` | Links and selected text. Step 1000 of the accent, so it holds 4.5:1 on the gray page, on white, and inside a hovered row |
| `accent-subtle` / `on-accent-subtle` | *Wise extension.* A quiet accent tint for a highlighted region (calendar event, autocomplete row) |
| `neutral-background` / `on-neutral` | The solid neutral: neutral badges, pressed action buttons, tooltips, toasts |
| `informative-` / `positive-` / `notice-` / `negative-` `background` and `-content` | Status. Fills take `on-accent` text (`on-notice` on the orange fill). Always with a word and an icon |
| `neutral-` / `informative-` / `positive-` / `notice-` / `negative-` `subtle` | The tinted background of an inline alert (`.callout`); its icon and 2px border use the `-content` color, its text stays `content-heading` / `content-default` |
| `focus-ring` | The 2px keyboard focus outline |

```html
<button class="bg-accent-background text-on-accent">Filled</button>
<div class="bg-background-elevated text-content-default rounded-xl p-6">Dialog-like surface</div>
<p class="text-content-subdued">Secondary text</p>
<span class="bg-positive-background text-on-accent rounded-full px-2">Approved</span>
<hr class="border-border-subtle">
```

Always pair a fill with its own `on-` token, and never hardcode `text-white`: in dark mode the filled
accent steps one shade lighter, and the notice (orange) fill's label turns black.

The accent is one color: blue by default, switchable to red, graphite or green with `data-palette`.
Each option is one OKLCH color (below) grown into a full scale for both themes, and every option is
checked, so white text on the accent fill and the accent as link text hold 4.5:1 whichever one you pick.

Also new in Lumen's form-input review: `fill-disabled` / `border-disabled` (a disabled field),
`negative-border` / `-hover` (an invalid field keeps its 1px border and changes its color),
`border-popover` (none in light, 1px in dark), `*-subtle` tints for inline alerts, and the translucent
row tints `row-hover` (7% content-heading), `selected-subtle` (10% accent) and `selected-subtle-hover`
(15%).

### Contrast on the gray canvas

Stock Lumen puts text on white. Here it also sits on a gray page, so a few tokens read one step darker
than Lumen's own: the accent and status `-content` colors use step 1000 (both themes), `border-default`
is gray-600 and `border-hover` gray-700 in light, and the neutral fills start at gray-200. Every pair is
asserted by `npm run build:palettes` on the page, every surface and every fill, in both themes and for
every palette, and the build refuses to write if one drops below 4.5:1 (text) or 3:1 (control borders,
focus ring).

### Material 3 and legacy color names

The Material 3 role names and the pre-M3 names still exist as aliases, so older templates and
downstream projects render correctly, but new markup should use the Lumen tokens above:

| Alias | Now points at |
|---|---|
| `primary` / `on-primary` | `accent-background` / `on-accent` |
| `primary-container` / `on-primary-container` | `accent-subtle` / `on-accent-subtle` |
| `secondary` / `secondary-container` | `neutral-background` / `fill-neutral-hover` |
| `tertiary(-container)` | the purple scale |
| `error`, `success`, `warning` (+ `-container`) | `negative-` / `positive-` / `notice-background`; containers are the 200 step of the hue |
| `surface`, `surface-container-low/(none)/high/highest` | `background-base`, `background-layer-1`, gray-75, `fill-neutral-hover`, `fill-neutral-down` |
| `on-surface` / `on-surface-variant` | `content-default` / `content-subdued` |
| `outline` / `outline-variant` | `border-default` / `border-subtle` |
| `inverse-surface` / `inverse-on-surface` | `neutral-background` / `on-neutral` |
| `brand-*`, `action-*` | the accent scale (`action-600` = `accent-content`, `action-100` = accent-200) |
| `accent-*` (legacy) | negative (`accent-500` = `negative-content`, `accent-50` = red-200) |
| `warning-50/500/600` | orange tints / `notice-content` |
| `page`, `panel`, `panel-alt`, `divider` | `background-base`, `background-layer-1`, gray-75, `border-subtle` |
| `on-action`, `on-brand`, `on-accent` | `on-accent` |
| `gray-50..950` | Lumen's gray scale itself (`gray-900` heading, `gray-800` default, `gray-700` subdued, `gray-500` border, `gray-300` subtle; `950` = gray-1000). Inverts in dark mode |
| `--shadow-blueprint-sm/md/lg`, `shadow-elevation-1..5` | `--shadow-emphasized` / `-elevated` / `-dragged` |

The `-fixed` roles and the `--md-sys-*` / `--md-ref-*` custom properties from the Material 3 release
no longer exist; read the `--color-*` tokens instead.

### Rebranding

The accent options are `ACCENT_COLORS` in
[`scripts/generate_lumen_palettes.mjs`](../scripts/generate_lumen_palettes.mjs). Each is an id (the
`data-palette` value), a label, **one OKLCH color** - the fill of the main action in light - and `ref`,
the Lumen hue from [`scripts/lumen-scales.json`](../scripts/lumen-scales.json) whose lightness and
chroma ladder the 16-step scale follows:

| Option | `data-palette` | OKLCH color | Applied fill (light) |
|---|---|---|---|
| Blue (default) | unset or `blue` | `oklch(54.6% 0.1724 254.2deg)` | `#066fd1` |
| Red | `red` | `oklch(58.29% 0.1941 25.59deg)` | `#d63939` |
| Graphite | `graphite` | `oklch(27.39% 0.0055 286.03deg)` | `#27272a` |
| Green | `green` | `oklch(64.32% 0.1338 164.7deg)` | `#088761` |

White text on the given green is only 3.1:1, so the generator darkens a color (same hue and chroma) just
enough to reach 4.5:1; the other three are used exactly as given. Graphite is a neutral accent: links
in it differ from body text by their underline, not their color. To add an option, add an entry to
`ACCENT_COLORS` and `ACCENTS`, a button in `_settings_panel.html`, and run:

```bash
npm run build:palettes && npm run build:css
```

The script checks the contrast of every token pair across both themes, every palette and every
ground (the page, each surface, each fill), and refuses to write anything that fails. In a consuming project that doesn't want to run
the generator, redefine `--color-accent-background`, `--color-accent-background-hover`,
`--color-accent-background-down`, `--color-accent-content` and `--color-focus-ring` in an `@theme`
block imported *after* `tokens.css` (keep 4.5:1 for white text on the fill and for the content color
on the page, in both themes). Every component follows, since they only read those tokens.

## Typography

Source Sans 3 for everything and Source Code Pro for code, vendored as variable woff2 (weights
200–900, latin + latin-ext, OFL - see `wise_core/static/wise_core/font/`).
`--font-brand`/`--font-plain` are the names; `--font-heading`/`--font-body`/`--font-sans` alias them
and `--font-mono` is the code face.

Lumen's type scale, each style one Tailwind utility setting size, line height and weight:

| Utility | Sizes (px) | Line height | Weight | Default use |
|---|---|---|---|---|
| `text-heading-xxs…xxxxl` | 14, 18, 20, 22, 28, 36, 45, 58, 73 | 1.3 | 800 | `h1` (l), `h2` (m), `h3` (s); page and section headings |
| `text-title-xs…xxxl` | 12, 14, 16, 18, 20, 22, 25 | 1.3 | 700 | `h4` (l), `h5` (m), `h6` (s); buttons, tabs, table headers, card titles |
| `text-body-xxs…xxxl` | 11, 12, 14, 16, 18, 20, 22, 25 | 1.5 | 400 | Body (`m` is the page default), cells (`s`), help text (`xs`) |
| `text-detail-xs…xl` | 11, 12, 14, 16, 18 | 1.3 | 500 | Labels, nav items, kickers, counts |
| `text-code-xs…xl` | 12, 14, 16, 18, 20 | 1.5 | 400 | Code (pair with `font-mono`) |

Headings get their style automatically. Sentence case everywhere: Lumen never uppercases headings,
labels or buttons. The sizes are the desktop scale; add about 20% on touch. The Material 3 names
(`text-body-large`, `text-label-medium`, ...) remain as aliases onto the nearest Lumen style.

## Shape

Lumen's corner radii, `--corner-radius-*`, and Tailwind's radius scale mapped onto them:

| Token | Value | Tailwind | Used by |
|---|---|---|---|
| `corner-radius-100` | 4px | `rounded-xs` | Checkboxes, tags, tooltips, calendar events |
| `corner-radius-300` | 6px | `rounded-sm` | Extra-small swatches |
| `corner-radius-400` | 7px | | Menu items |
| `corner-radius-500` | 8px | `rounded-md` | Text fields, cards, detail panel, alerts, nav items, toasts |
| `corner-radius-700` | 10px | `rounded-lg` | Popovers: menus, autocomplete results |
| `corner-radius-800` | 16px | `rounded-xl`, `rounded-2xl` | Dialogs, empty states, carousel items |
| `corner-radius-full` | 9999px | `rounded-full` | Buttons, icon buttons, badges, switches, progress tracks, avatars |

`data-radius="soft"` halves the scale; `data-radius="sharp"` zeroes all of it, pills included. Things
that are round by definition (spinner, donut, radio, `.avatar-circle`) use a literal `9999px`.

## Layers and shadow

Lumen raises a surface by layer and border, not shadow: `background-base` (the fixed gray page) →
`background-layer-1` (panels) → `background-layer-2` (cards, fields) → `background-elevated` (popovers,
dialogs). In light the three surfaces are white, so they read as white sheets on the gray page; in dark
they step up from near-black. Shadows
are for things that float, and there are three: `--shadow-emphasized` (`shadow-emphasized`, the resting
state of a raised control), `--shadow-elevated` (menus, popovers, tooltips, toasts) and
`--shadow-dragged` (dialogs, dragged items), deeper in dark mode. `.elevation-1/2/3` utility classes
apply a layer *and* a shadow together.

`.card`, `.detail-panel` and the other panels follow `data-shadow`: flat (default) = a white (layer-2)
surface with a `border-subtle` edge and no shadow, soft/elevated = the same card with no border and an
`emphasized` / `elevated` shadow. `.card-outlined`, `.card-elevated` and `.card-filled` pin one type.

## Hover, press, focus

There are no overlay layers: hover steps a fill one shade and press two. A filled accent control goes
`accent-background` → `-hover` → `-down` (negative likewise); outlined, quiet and list-row controls
fill with `fill-neutral-hover` then `fill-neutral-down`. The quiet-hover rule is one `:where(...)` block
in `tokens.css`; add your own component's selector to it rather than writing hover colors by hand.
Disabled: a button is `content-disabled` text on `fill-neutral-hover` (no fill for quiet buttons); a field,
checkbox, radio or switch uses `fill-disabled` / `border-disabled`.

Focus: a 2px `focus-ring` outline offset 2px (`--focus-ring-width/-offset/-color`) on every
`:focus-visible`, text fields included.

## Motion

Hover, press and color changes take 130ms (`--default-transition-duration`, Tailwind's default too) on
`--ease-standard` (`cubic-bezier(0.4, 0, 0.2, 1)`). Things arriving (dialogs, drawers) take 200ms on
`--ease-enter`; `--ease-exit` is for leaving. Animate color, opacity and transform only, and respect
`prefers-reduced-motion`.

## Control heights

Lumen's component heights are 20, 24, 32 (the default), 40 and 48px (`--component-height-50` …
`-300`). Components read the control tokens rather than a fixed height:

| Token | Default | Coarse pointer (touch) |
|---|---|---|
| `--control-height-md` | 2rem (32px text field) | 2.5rem |
| `--control-height-sm` / `-lg` | 1.5rem / 2.5rem | 2rem / 3rem |
| `--control-height-button` | 2rem (32px button) | 2.5rem |
| `--list-item-height` / `--menu-item-height` | 2rem | 2.5rem |
| `--table-padding-y` | 0.5rem | 0.5rem |

On a coarse pointer the values step up one size - 40px fields, buttons and rows - following Lumen's
"add about 20% on touch". Density is not a setting: there is no compact mode.

## Switchable axes

Four independent attributes on `<html>`, each redefining a handful of tokens at runtime (no rebuild,
no second stylesheet). They compose freely, because each touches a different tier: the accent re-points
the accent scale, theme re-points which step each semantic token reads. Nothing else is a setting - not
the page background, not density.
`base.html` applies whatever's in `localStorage` before first paint;
`wise_core/static/wise_core/js/common.js` exposes one setter per axis, and
`wise_core/components/_settings_panel.html` is a ready-made side sheet for all four (open it with
`wiseOpenDrawer('wise-settings-drawer')`, normally via `_settings_toggle.html`). Its **Copy tokens** tab
exports the current `data-*` line and the resolved `--color-*` / `--corner-radius-*` values (see
`WISE_EXPORT_TOKENS` in `common.js`).

| Attribute | Values | Retunes |
|---|---|---|
| `data-theme` | `light` (default), `dark` | Which palette step each semantic color token reads |
| `data-palette` | `blue` (default), `red`, `graphite`, `green` | The accent color |
| `data-radius` | Lumen radii (default), `soft`, `sharp` | Rounding: the whole corner scale |
| `data-shadow` | `flat` (default), `soft`, `elevated` | Card shadow: outlined vs. raised cards and panels |

```js
wiseSetTheme('dark')       // '' or 'light' resets to light
wiseSetPalette('green')    // 'red' | 'graphite' | 'green'; '' resets to blue
wiseSetRadius('sharp')     // 'soft' | 'sharp'; '' resets to the Lumen corner radii
wiseSetShadow('elevated')  // 'soft' | 'elevated'; '' resets to flat (outlined cards)
```

## Component class names

The component layer (`.btn`, `.card`, `.badge`, `.form-stack`, `.detail-panel`, `.data-table`,
`.menu-link`, `.tab-bar`, `.pagination-link`, ...) is the design system's real public API. The class
names stayed the same through the moves to Material 3 and then Lumen; only their look changed. In
Lumen terms: `.btn-primary` is the accent button, `.btn-brand` the neutral-fill button,
`.btn-secondary` the neutral outline, `.btn-ghost` the quiet action button, `.btn-group` an action
group, `.badge` a badge, `.status-light` a status light, `.callout` an inline alert, `.toast` a toast,
`.drawer` a side sheet, `.dropdown-panel` a menu, `.menu-link` a side-nav item. Material 3 aliases
(`.btn-filled`, `.btn-tonal`, `.btn-outlined`, `.btn-text`) sit alongside, with `.btn-elevated`, `.fab`,
`.card-elevated/-filled/-outlined` and `.badge-count`. The full mapping is in the
[Lumen design skill](../.claude/skills/lumen-design/references/components.md). See
[template-tags-and-filters.md](template-tags-and-filters.md) and
[generic-views-and-mixins.md](generic-views-and-mixins.md) for how the generic templates use them,
or the Components sections of `/docs/` for a rendered catalog.
