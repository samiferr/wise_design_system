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

The entire Tailwind radius scale (`--radius-xs` through `--radius-4xl`) is zeroed, so every
`rounded-*` utility across your templates resolves to a square corner with **no template changes
needed**. If you want rounded corners in your own project, redefine the radius scale back to
Tailwind's defaults in your own `@theme` — the component layer never hardcodes a radius, it only
reads these variables (`rounded-full` on a status dot, etc., is the one thing this breaks; give
those elements an explicit inline `border-radius: 9999px` if you need an actual circle).

```html
<div class="rounded-lg border">Square corner — rounded-lg resolves to 0</div>

<!-- to force an actual circle (status dot, avatar), bypass the token -->
<div class="h-2 w-2 bg-action-600" style="border-radius: 9999px;"></div>
```

## Shadows

Three elevation levels only, named for what they're used for rather than a generic sm/md/lg scale
confusion: `--shadow-blueprint-sm/md/lg`. Used by the flash-message stack, the filter side-panel,
and the autocomplete dropdown.

**Usage** — there's no `shadow-blueprint-*` Tailwind utility; reach these with the raw CSS custom
property in an inline `style` or your own CSS:

```html
<div class="filter-panel" style="box-shadow: var(--shadow-blueprint-lg)">...</div>
```

## Component class names

The component layer (`.btn`, `.card`, `.badge`, `.form-stack`, `.detail-panel`, `.data-table`,
`.menu-link`, `.tab-bar`, `.pagination-link`, ...) is the design system's real public API — stable
across token changes, matched 1:1 to DCMS7's own class names so templates ported from DCMS7 don't
need renaming. See [template-tags-and-filters.md](template-tags-and-filters.md) and
[generic-views-and-mixins.md](generic-views-and-mixins.md) for how the generic templates use them,
or `/components/` on the demo site for a rendered catalog.
