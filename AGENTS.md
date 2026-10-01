# Agent notes

The Wise Design System is styled after **Lumen**, a calm, neutral-first system in the Spectrum
tradition (one accent hue, semantic color tokens, Source Sans 3, pill buttons and 8px fields, layers
and borders instead of shadows). Before writing or reviewing any UI (Django templates, Tailwind
classes, `tokens.css`), read the Lumen design skill:

- [`.claude/skills/lumen-design/SKILL.md`](.claude/skills/lumen-design/SKILL.md): rules,
  component → Wise-class map, token cheat sheet, workflow
- [`references/components.md`](.claude/skills/lumen-design/references/components.md): markup
  for every component
- [`references/tokens.md`](.claude/skills/lumen-design/references/tokens.md): every color token,
  type style, shape, shadow, motion and size token
- [`references/authoring.md`](.claude/skills/lumen-design/references/authoring.md): adding a
  component or palette
- [`references/review-checklist.md`](.claude/skills/lumen-design/references/review-checklist.md):
  pre-merge checks

Build: `npm install && npm run build:css` (and `npm run build:palettes` after changing an accent in
`scripts/generate_lumen_palettes.mjs`). Demo site: see the README's "Run the site".
