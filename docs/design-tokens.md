# Design tokens

Source: [`wise_core/static/wise_core/css/tokens.css`](../wise_core/static/wise_core/css/tokens.css) —
a Tailwind CSS v4 partial (an `@theme` block plus `@layer base`/`components`/`utilities`), extracted
from DCMS7's `core/static/core/css/input.css`. See [getting-started.md](getting-started.md) for how
a project builds this into a real stylesheet.

Live, rendered version: run the demo site and visit `/docs/theming/design-tokens/` (and the rest of
the Theming & Utilities section) — every example on that page is a real, running control, not a
screenshot. `/demo/` is a separate section of the same site: a small CRUD app built from these
tokens, with a settings panel (see [Switchable axes](#switchable-axes) below) for trying them
against real data.

## Color

One brand/accent color (`brand`/`action` — both draw from the same green ramp, matching the source
system's mono-accent rule), plus functional-only reds/ambers and an overridden neutral gray scale:

| Token | Use |
|---|---|
| `--color-brand-50..950` | Chrome, links, tags, kickers |
| `--color-action-50..700` | Buttons, focus rings, primary interactive state |
| `--color-accent-50..600` | **Destructive only** — delete buttons, error states |
| `--color-warning-50..600` | **Status/caution only** — pending states, warning banners |
| `--color-gray-50..950` | Overrides Tailwind's built-in gray scale — every `text-gray-*`/`bg-gray-*`/`border-gray-*` utility already picks up these tones |
| `--color-page` / `--color-surface` / `--color-divider` | Page background, input/filter background, hairline borders |

To rebrand: define your own `--color-brand-*`/`--color-action-*` ramps in an `@theme` block that
`@import`s *after* `tokens.css` in your project's entry CSS — Tailwind v4 merges `@theme` blocks by
variable name, so your values win without touching this file.

```css
/* your-project/static_src/input.css */
@import "tailwindcss";
@import "path/to/wise_core/static/wise_core/css/tokens.css";

@theme {
    --color-brand-500: #7c3aed;
    --color-brand-600: #6d28d9;
    --color-action-500: #7c3aed;
    --color-action-600: #6d28d9;
}
```

`--color-action-600` (not `-500`) is what buttons use for white-on-color text: `-500` only clears
3.3:1 contrast (fails WCAG AA's 4.5:1 normal-text minimum for a button label); `-600` clears 5:1.
Keep that in mind if you re-tune the ramp.

**Usage** — colors are consumed as ordinary Tailwind utility classes (`bg-*`/`text-*`/`border-*`),
never as raw CSS custom properties, except where noted below:

```html
<button class="bg-action-600 text-white hover:bg-action-700">Action button</button>
<span class="bg-brand-100 text-brand-800 font-semibold">Brand tag</span>
<button class="bg-accent-500 text-white hover:bg-accent-600">Delete</button>
<div class="border border-warning-500 bg-warning-50 text-warning-600 px-3 py-2 text-sm">
    Something needs your attention.
</div>

<!-- gray-* is the same Tailwind utility you already know, repointed at this system's tones -->
<p class="text-gray-900">Primary text</p>
<p class="text-gray-600">Secondary / muted text</p>

<!-- page/surface/divider aren't part of the numbered gray ramp - they get their own utilities -->
<body class="bg-page">
    <div class="border border-divider bg-white p-6">...</div>
    <input class="bg-surface border border-divider">
</body>
```

## Typography

- `--font-heading`: "Barlow Condensed" — all `h1`–`h6`, semibold, tight (1.12) line-height, `h6` set
  in uppercase small-caps-style tracking.
- `--font-body` / `--font-sans`: "Barlow" — body copy.
- Both fonts are vendored as self-hosted `woff2` files (`wise_core/static/wise_core/font/`) with
  `font-display: swap`.
- Fixed heading scale (not `clamp()`/responsive): h1 42px, h2 32px, h3 25px, h4 20px, h5 16px, h6 13px.

**Usage** — both fonts apply automatically to their elements (every `<h1>`–`<h6>` and body text need
no class at all); reach for the utility classes only to force one onto something else:

```html
<h2>Section title</h2>  <!-- font-heading applied automatically -->
<p>Body copy needs no class — font-body is the default.</p>

<!-- forcing the heading font onto a non-heading element -->
<div class="font-heading font-semibold uppercase tracking-wide">Eyebrow label</div>
```

## Radius

The entire Tailwind radius scale (`--radius-xs` through `--radius-4xl`) is zeroed **by default**, so
every `rounded-*` utility across your templates resolves to a square corner with **no template
changes needed** — this system's baseline look. The component layer (`.btn`, `.card`,
`.detail-panel`, `.input`, `.select`, `.textarea`, `.badge`, `.tag`, `.dialog`, `.dropdown-panel`,
`.toast`, `.callout`, `.avatar`, ...) reads this same scale rather than hardcoding a radius, so
redefining it moves the whole UI together — either permanently in your own `@theme` block, or live
via the `data-radius` attribute (see [Switchable axes](#switchable-axes)).

```html
<div class="rounded-lg border">Square corner — rounded-lg resolves to 0 by default</div>

<!-- to force an actual circle (status dot, avatar), bypass the token -->
<div class="h-2 w-2 bg-action-600" style="border-radius: 9999px;"></div>
```

## Shadows

Three fixed elevation levels for chrome that's always elevated, named for what they're used for
rather than a generic sm/md/lg scale: `--shadow-blueprint-sm/md/lg`, used by the flash-message
stack, the filter side-panel, the autocomplete dropdown, `.dialog`, `.dropdown-panel` and `.toast`.

**Usage** — there's no `shadow-blueprint-*` Tailwind utility; reach these with the raw CSS custom
property in an inline `style` or your own CSS:

```html
<div class="filter-panel" style="box-shadow: var(--shadow-blueprint-lg)">...</div>
```

`.card` and `.detail-panel` are the exception: both read the same `--shadow-card` token (`none` by
default — a border, not a shadow, separates a raised panel from the page) rather than the
blueprint scale directly, so a project can retune *just* panel elevation without touching
dropdowns/dialogs/toasts. See `data-shadow` below.

## Switchable axes

Six independent attributes on `<html>`, each redefining a handful of the tokens above at runtime
(no rebuild, no second stylesheet) — they compose freely, so e.g. a compact dark violet UI with
round corners and a warm background is a valid combination. `base.html` applies whatever's in
`localStorage` before first paint; `wise_core/static/wise_core/js/common.js` exposes one setter per
axis (`wiseSetTheme`/`wiseSetPalette`/`wiseSetDensity`/`wiseSetRadius`/`wiseSetShadow`/`wiseSetBg`),
and `wise_core/components/_settings_panel.html` is a ready-made drawer UI for all six — open it with
`wiseOpenDrawer('wise-settings-drawer')`, normally via `_settings_toggle.html`. It ships wired into
`wise_core/base.html`'s default authenticated chrome (sidebar + mobile topbar), so any project
pulling in `wise_core` gets it for free.

The panel has two tabs: **Settings** (the controls above) and **Copy tokens**, which renders the
exact combination currently selected — the `<html data-*>` attribute line to reproduce it at
runtime, and the resolved `:root { --token: value; }` block behind it (a curated subset — brand/
action colors, page/panel/surface, radius, `--shadow-card`, control heights — not the full
`@theme`) — behind one `.copy-button`. See `wiseBuildTokenExport()` in `common.js` if you need to
change which tokens it exports.

| Attribute | Values | Retunes |
|---|---|---|
| `data-theme` | `light` (default), `dark` | Neutral ramp, surfaces, shadows, on-colors |
| `data-palette` | `green` (default), `blue`, `violet`, `amber` | Brand/action ramps only |
| `data-density` | `comfortable` (default), `compact` | Control heights, form/table rhythm |
| `data-radius` | `sharp` (default), `soft`, `round` | The whole radius scale |
| `data-shadow` | `flat` (default), `soft`, `elevated` | `--shadow-card` only |
| `data-bg` | `neutral` (default), `warm`, `cool` | `--color-page`/`-panel-alt`/`-surface` (never `-panel`) |

```js
wiseSetTheme('dark')       // '' or 'light' resets to light
wiseSetPalette('violet')   // '' resets to green
wiseSetDensity('compact')  // '' resets to comfortable
wiseSetRadius('round')     // '' resets to sharp
wiseSetShadow('elevated')  // '' resets to flat
wiseSetBg('warm')          // '' resets to neutral
```

## Component class names

The component layer (`.btn`, `.card`, `.badge`, `.form-stack`, `.detail-panel`, `.data-table`,
`.menu-link`, `.tab-bar`, `.pagination-link`, ...) is the design system's real public API — stable
across token changes, matched 1:1 to DCMS7's own class names so templates ported from DCMS7 don't
need renaming. See [template-tags-and-filters.md](template-tags-and-filters.md) and
[generic-views-and-mixins.md](generic-views-and-mixins.md) for how the generic templates use them,
or the Components sections (Actions, Forms, Layout, Navigation, Feedback, Media, Data Viz) of
`/docs/` for a rendered catalog.
