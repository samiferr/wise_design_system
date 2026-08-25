# Design tokens

Source: [`wise_core/static/wise_core/css/tokens.css`](../wise_core/static/wise_core/css/tokens.css) —
a Tailwind CSS v4 partial (an `@theme` block plus `@layer base`/`components`/`utilities`), extracted
from DCMS7's `core/static/core/css/input.css`. See [getting-started.md](getting-started.md) for how
a project builds this into a real stylesheet.

Live, rendered version: run the demo site and visit `/tokens/` and `/components/`.

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

`--color-action-600` (not `-500`) is what buttons use for white-on-color text: `-500` only clears
3.3:1 contrast (fails WCAG AA's 4.5:1 normal-text minimum for a button label); `-600` clears 5:1.
Keep that in mind if you re-tune the ramp.

## Typography

- `--font-heading`: "Barlow Condensed" — all `h1`–`h6`, semibold, tight (1.12) line-height, `h6` set
  in uppercase small-caps-style tracking.
- `--font-body` / `--font-sans`: "Barlow" — body copy.
- Both fonts are vendored as self-hosted `woff2` files (`wise_core/static/wise_core/font/`) with
  `font-display: swap`.
- Fixed heading scale (not `clamp()`/responsive): h1 42px, h2 32px, h3 25px, h4 20px, h5 16px, h6 13px.

## Radius

The entire Tailwind radius scale (`--radius-xs` through `--radius-4xl`) is zeroed, so every
`rounded-*` utility across your templates resolves to a square corner with **no template changes
needed**. If you want rounded corners in your own project, redefine the radius scale back to
Tailwind's defaults in your own `@theme` — the component layer never hardcodes a radius, it only
reads these variables (`rounded-full` on a status dot, etc., is the one thing this breaks; give
those elements an explicit inline `border-radius: 9999px` if you need an actual circle).

## Shadows

Three elevation levels only, named for what they're used for rather than a generic sm/md/lg scale
confusion: `--shadow-blueprint-sm/md/lg`. Used by the flash-message stack, the filter side-panel,
and the autocomplete dropdown.

## Component class names

The component layer (`.btn`, `.card`, `.badge`, `.form-stack`, `.detail-panel`, `.data-table`,
`.menu-link`, `.tab-bar`, `.pagination-link`, ...) is the design system's real public API — stable
across token changes, matched 1:1 to DCMS7's own class names so templates ported from DCMS7 don't
need renaming. See [template-tags-and-filters.md](template-tags-and-filters.md) and
[generic-views-and-mixins.md](generic-views-and-mixins.md) for how the generic templates use them,
or `/components/` on the demo site for a rendered catalog.
