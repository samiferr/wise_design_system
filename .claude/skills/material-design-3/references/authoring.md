# Adding or changing a component in tokens.css

Components live in `@layer components` in `wise_core/static/wise_core/css/tokens.css`. Class names
are public API: add, don't rename.

## Recipe

1. **Find the M3 spec** for the component (m3.material.io/components/...): container color role,
   content role, shape token, height, padding, type role, elevation per state.
2. **Write it from system tokens only:**

```css
/* ── Navigation rail item ────────────────────────────────────────────
   One line on what it is, which M3 component it follows, and anything
   non-obvious about the markup it expects. */
.rail-item {
    @apply inline-flex flex-col items-center gap-1 text-label-medium;  /* layout + type role */
    min-height: var(--list-item-height);                               /* density token */
    color: var(--md-sys-color-on-surface-variant);                     /* content role */
    border-radius: var(--md-sys-shape-corner-full);                    /* shape token */
}

.rail-item.selected {
    background-color: var(--md-sys-color-secondary-container);
    color: var(--md-sys-color-on-secondary-container);
}
```

3. **Interactive?** Add its selector to all four `:where(...)` lists of the state-layer block at the
   top of `@layer components` (base, `:hover`, `:focus-visible`, `:active`). Don't write
   `:hover { background: ... }` yourself.
4. **Disabled?** `color: var(--wise-disabled-content)`, container
   `var(--wise-disabled-container)`, `cursor: not-allowed`.
5. **Floats?** Use `--md-sys-elevation-levelN` and a `--z-*` token. **Moves?** Use the M3 motion
   tokens, e.g. `transition: transform var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized-decelerate);`
6. **Specificity:** keep selectors flat (one or two classes). When a base rule needs a long `:not()`
   chain, wrap it in `:where()` so state and error modifiers can still win (see the text-field rules).
7. **Legacy aliases:** don't use `--color-action-*`, `--color-panel` & co. inside tokens.css. Use
   `--md-sys-*`.
8. Build (`npm run build:css`), add a docs page or example under
   `demo/showcase/templates/showcase/docs/<section>/` if the component is new, and check light, dark,
   compact density and `data-radius="sharp"`.

## Colors / palettes

- Change a seed or add a palette: `scripts/generate_m3_palettes.mjs` → `npm run build:palettes`.
- Change which tone a role uses: the `:root` / `:root[data-theme="dark"]` blocks in `tokens.css`,
  following the M3 tone mapping in `tokens.md`. Keep light/dark symmetric.
- New semantic color family (like success/warning): add a harmonized seed in the generator (see
  `SUCCESS_SEED`), then the four roles in both theme blocks and the four `--color-*` aliases in
  `@theme static`.

## Charts

`wise_core/charts.py` `SERIES_COLORS` uses `var(--md-sys-color-*)`. `charts.js` resolves those from
the computed style, so only use tokens whose values are plain colors (not `color-mix()`).
