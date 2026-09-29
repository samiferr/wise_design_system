# M3 review checklist

Run through this before finishing any UI change. Grep helpers are at the bottom.

## Color
- [ ] Only M3 role utilities / `--md-sys-color-*`; no hex, rgb, Tailwind palette colors
      (`blue-500`, `emerald-700`), `bg-white`, `text-white`, `text-black`.
- [ ] Every container is paired with its own `on-` role.
- [ ] Error roles only for destructive/error; success/warning only for status.
- [ ] At most one filled (`btn-primary`) button per view region; the rest are tonal/outlined/text.
- [ ] Looks right in `data-theme="dark"` and at least one other `data-palette`.

## Type
- [ ] Only `text-{display,headline,title,body,label}-{large,medium,small}` (or the heading
      elements' defaults). No `text-xs`/`text-[11px]` + `font-semibold` + `tracking-*` combos.
- [ ] No `uppercase`. Sentence case in labels, buttons, headings, table headers.

## Shape & elevation
- [ ] Radii come from the component or `rounded-{xs,sm,md,lg,xl,2xl,full}`; nothing arbitrary.
- [ ] Surfaces raised tonally (`surface-container-*`); shadows only on floating elements, using
      `shadow-elevation-N`.
- [ ] Still acceptable under `data-radius="sharp"` (nothing relies on roundness to be understood).

## Interaction & a11y
- [ ] Interactive elements use a component class with a state layer, not ad-hoc hover colors.
- [ ] Keyboard focus shows the 3px secondary ring (don't `outline: none` without a replacement).
- [ ] Icon-only buttons have `aria-label`; tabs have `role="tab"`/`aria-selected`; dialogs use
      `<dialog>`.
- [ ] Touch targets ≥ 40px (buttons) / 48px where possible.
- [ ] Disabled uses the `disabled` attribute (or `.btn-disabled` on `<a>`), not opacity hacks.

## Layout & density
- [ ] Spacing on the 4px grid; window margins 16px (compact) / 24px (medium+) - `.page-panel` does this.
- [ ] Heights come from density tokens; the view survives `data-density="compact"`.

## Build
- [ ] `npm run build:css` ran after template/CSS changes; `md3-palettes.css` untouched unless regenerated.

## Grep helpers

```bash
# raw colors / non-role Tailwind colors in templates
grep -rnE '#[0-9a-fA-F]{3,6}\b|(bg|text|border)-(white|black|(red|blue|green|emerald|amber|yellow|violet|slate|zinc)-[0-9]+)' --include=*.html .
# uppercase / tracking leftovers
grep -rnE 'uppercase|tracking-wid' --include=*.html .
# legacy aliases worth migrating
grep -rnE '(bg|text|border)-(action|brand|accent|panel|page|divider)(-[0-9]+)?\b' --include=*.html .
```
