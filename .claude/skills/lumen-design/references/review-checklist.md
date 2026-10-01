# Lumen review checklist

Run through this before finishing any UI change. Grep helpers are at the bottom.

## Color
- [ ] Only Lumen token utilities / `--color-*`; no hex, rgb, Tailwind palette colors
      (`blue-500`, `emerald-700`), `bg-white`, `text-white`, `text-black`.
- [ ] Every fill is paired with its own `on-` token (`on-accent`, `on-neutral`, `on-notice`).
- [ ] One accent fill (`btn-primary`) per view region; the rest are neutral fill, outline or quiet.
- [ ] Negative only for destructive/error; positive/notice/informative only for status.
- [ ] Status carries a word and an icon, never color alone.
- [ ] Text is `content-heading` / `content-default` / `content-subdued` (never `content-disabled`
      for live content); a control's border is `border-default`, not `border-subtle`.
- [ ] Cards, panels, fields and popovers are white surfaces (`background-layer-1/2`, `-elevated`) on the
      fixed gray page; nothing overrides `background-base`, and nothing assumes the page is white.
- [ ] Accent and status text uses the `-content` tokens (never an `*-background` token as text color).
- [ ] Looks right in `data-theme="dark"` and at least one other `data-palette` (red, graphite or green).

## Type
- [ ] Only `text-{heading,title,body,detail,code}-*` (or the heading elements' defaults). No
      `text-xs`/`text-[11px]` + `font-semibold` + `tracking-*` combos.
- [ ] No `uppercase`. Sentence case in labels, buttons, headings, table headers.
- [ ] Body copy is `body-m`; controls and labels are 14px (`title-s` / `detail-m`).

## Shape & layers
- [ ] Radii come from the component or `rounded-{xs,sm,md,lg,xl,full}`; nothing arbitrary. Buttons,
      badges, switches and progress tracks are round; fields, cards, alerts and nav items 8px.
- [ ] Raised by layer step or `border-subtle` edge; shadows only on floating elements
      (`shadow-elevated` menus/toasts, `shadow-dragged` dialogs).
- [ ] Still acceptable under `data-radius="sharp"` (nothing relies on roundness to be understood).

## Interaction & a11y
- [ ] Interactive elements use a component class with stepped fills, not ad-hoc hover colors.
- [ ] Keyboard focus shows the 2px `focus-ring` outline (don't `outline: none` without a replacement).
- [ ] Icon-only buttons have `aria-label`; tabs have `role="tab"`/`aria-selected`; dialogs use
      `<dialog>`.
- [ ] Touch targets: components step up to 40px on a coarse pointer; don't override heights.
- [ ] Disabled uses the `disabled` attribute (or `.btn-disabled` on `<a>`), not opacity hacks.

## Layout & sizes
- [ ] Spacing on the 4px grid; window margins 16px (compact) / 24px (medium+) - `.page-panel` does this.
- [ ] Heights come from the `--control-height-*` / `--component-height-*` tokens (they step up on touch);
      nothing hardcodes a control height.

## Build
- [ ] `npm run build:css` ran after template/CSS changes; `lumen-palettes.css` untouched unless
      regenerated with `npm run build:palettes`.

## Grep helpers

```bash
# raw colors / non-token Tailwind colors in templates
grep -rnE '#[0-9a-fA-F]{3,6}\b|(bg|text|border)-(white|black|(red|blue|green|emerald|amber|yellow|violet|slate|zinc)-[0-9]+)' --include=*.html .
# uppercase / tracking leftovers
grep -rnE 'uppercase|tracking-wid' --include=*.html .
# Material 3 and legacy aliases worth migrating
grep -rnE '(bg|text|border)-(action|brand|accent|panel|page|divider|primary|secondary|surface[a-z-]*|on-surface[a-z-]*|outline[a-z-]*)(-[0-9]+)?\b' --include=*.html .
grep -rnE 'text-(display|headline|title|body|label)-(small|medium|large)' --include=*.html .
```
