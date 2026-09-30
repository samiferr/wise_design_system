# Agent notes

The Wise Design System is styled after **Material Design 3**. Before writing or reviewing any UI
(Django templates, Tailwind classes, `tokens.css`), read the Material Design 3 skill:

- [`.claude/skills/material-design-3/SKILL.md`](.claude/skills/material-design-3/SKILL.md): rules,
  M3-component → Wise-class map, token cheat sheet, workflow
- [`references/components.md`](.claude/skills/material-design-3/references/components.md): markup
  for every component
- [`references/tokens.md`](.claude/skills/material-design-3/references/tokens.md): every color role,
  type role, shape, elevation, motion and density token
- [`references/authoring.md`](.claude/skills/material-design-3/references/authoring.md): adding a
  component or palette
- [`references/review-checklist.md`](.claude/skills/material-design-3/references/review-checklist.md):
  pre-merge checks

Build: `npm install && npm run build:css` (and `npm run build:palettes` after changing a seed in
`scripts/generate_m3_palettes.mjs`). Demo site: see the README's "Run the site".
