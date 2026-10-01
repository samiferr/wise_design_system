# Adding or changing a component in tokens.css

Components live in `@layer components` in `wise_core/static/wise_core/css/tokens.css`. Class names
are public API: add, don't rename.

## Recipe

1. **Find the nearest Lumen shape.** Lumen specifies Button, ActionButton, TextField, Checkbox,
   Switch, RadioGroup, Tabs, StatusLight, Badge, ProgressBar, InlineAlert and Divider; anything else
   (menus, dialogs, tables) is built from the same tokens in the same shapes. Decide: which layer it
   sits on, its fill / content / border tokens, its corner radius, its height from the control-height
   tokens, its type style, and whether it floats (shadow) or sits (border).
2. **Write it from system tokens only:**

```css
/* ── Side-nav badge row ──────────────────────────────────────────────
   One line on what it is, which Lumen component it follows, and anything
   non-obvious about the markup it expects. */
.nav-row {
    @apply inline-flex items-center gap-2 px-3 text-detail-m;       /* layout + type style */
    min-height: var(--list-item-height);                            /* control-height token */
    color: var(--color-content-default);                            /* content token */
    border-radius: var(--corner-radius-500);                        /* shape token */
}

.nav-row.selected {
    background-color: var(--color-fill-neutral-hover);
    color: var(--color-content-heading);
    font-weight: 700;
}
```

3. **Interactive?** A row on a neutral surface: add its selector to both `:where(...)` lists of the
   "Quiet hover and press" block (`:hover` → `fill-neutral-hover`, `:active` → `fill-neutral-down`).
   A filled control: write `:hover` / `:active` that step the fill (`accent-background-hover` /
   `-down`, `negative-background-hover` / `-down`). A control that sits on a colored surface: use
   the `color-mix(in srgb, currentColor 16%, transparent)` veil like `.tag-remove`. Never an ad-hoc
   hover color. Add `.selected` states *after* the generic hover so they win (and a
   `.selected:hover` that steps to `fill-neutral-down`).
4. **Disabled?** `color: var(--wise-disabled-content)`, container `var(--wise-disabled-container)`,
   `cursor: not-allowed`.
5. **Keyboard focus?** Nothing to write: the base `:focus-visible` rule draws the 2px `focus-ring`
   outline. Only add a rule if the visible box isn't the element's own box (see `.ql-container` in
   `wise_richtext.css`).
6. **Floats?** Use a shadow token (`--shadow-elevated` for menus and popovers, `--shadow-dragged` for
   dialogs) plus a `--z-*` token, and a `background-elevated` fill with a `border-subtle` edge.
   **Moves?** `transition: ... 130ms var(--ease-standard)` for state changes; 200ms with
   `--ease-enter` for things arriving. Animate color, opacity and transform; add a
   `prefers-reduced-motion` override for anything that loops.
7. **Specificity:** keep selectors flat (one or two classes). When a base rule needs a long `:not()`
   chain, wrap it in `:where()` so state and error modifiers can still win (see the text-field rules).
8. **Don't use the compat names** (`--color-primary`, `--color-on-surface-variant`,
   `--color-action-*`, `--color-panel`, `--color-gray-*`) inside `tokens.css`. Use the Lumen tokens.
9. Build (`npm run build:css`), add a docs page or example under
   `demo/showcase/templates/showcase/docs/<section>/` if the component is new, and check light, dark,
   `data-radius="sharp"` and one other accent (red, graphite or green).

## Colors / palettes

- Add or change an accent option: `ACCENT_COLORS` in `scripts/generate_lumen_palettes.mjs` - an id, a
  label, one OKLCH color (the main-action fill in light) and `ref`, the Lumen hue in
  `scripts/lumen-scales.json` whose lightness ladder the scale follows - plus an entry in `ACCENTS`, then
  `npm run build:palettes`. A color whose white label would fall under 4.5:1 is darkened automatically. Add a matching button to the settings
  panel (`_settings_panel.html`) and the docs palette switcher. The script fails if any token pair
  drops below its contrast target (4.5:1 text, 3:1 control borders and focus ring).
- Change which step a token uses: the `@theme static` block (light) and the
  `:root[data-theme="dark"]` block in `tokens.css`. Keep light and dark symmetric, and re-run
  `npm run build:palettes` so its checks mirror the change (its `checks()` function lists the pairs).
- New semantic color family (like negative / positive): add `-background` and `-content` tokens in
  `@theme static` (and the dark step in the dark block), then a pair of checks in the generator.
- The page background is fixed on purpose (no `data-bg` axis): to change the gray, change
  `--color-background-base` (and the matching `page` ground in the generator's `checks()`), then re-run
  `npm run build:palettes` so every pair is re-verified against it.

## Charts

`wise_core/charts.py` `SERIES_COLORS` uses `var(--color-*)` and `var(--lumen-*-900)`. `charts.js`
resolves those from the computed style, so only use tokens whose values are plain colors (not
`color-mix()`).
