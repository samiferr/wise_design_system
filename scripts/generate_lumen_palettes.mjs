#!/usr/bin/env node
/*
 * Generates wise_core/static/wise_core/css/lumen-palettes.css - the Lumen
 * *reference* palettes (`--lumen-<hue>-<step>`) behind every color in the
 * design system.
 *
 *     npm run build:palettes      (then `npm run build:css`)
 *
 * Lumen (a Spectrum-style system) ships one neutral scale and eleven hue
 * scales, each as 16 numbered steps with a light and a dark value, so a
 * step already flips with the theme. The steps live in lumen-scales.json
 * (next to this file); this script turns them into CSS and then checks the
 * contrast promises the semantic tokens in tokens.css make. The page is one
 * fixed gray (gray-100 in light) with white surfaces on it, so every pair is
 * checked on every ground that text or a control can actually sit on:
 *
 *   - heading / default / subdued text holds 4.5:1 on the page, every
 *     surface and every neutral fill, in both themes
 *   - a control's border and the focus ring hold 3:1 on the page and surfaces
 *   - white text holds 4.5:1 on every accent / negative / status fill, in
 *     its rest, hover and pressed steps
 *   - the accent and status colors as text hold 4.5:1 on the page, every
 *     surface and the hover / subtle fills, for every palette
 *
 * It writes two things:
 *
 *   1. the scales, light under :root and dark under [data-theme="dark"]
 *   2. data-palette: one block per accent hue that re-points the
 *      --lumen-accent-<step> scale (blue is the default). Every Lumen hue is
 *      built to the same contrast ladder, so any hue can be the accent
 *
 * The page background is deliberately not configurable (there is no
 * data-bg axis): one canvas means one set of contrast checks.
 *
 * To rebrand: add a hue to ACCENTS (it must exist in lumen-scales.json) and
 * re-run. If a check fails the script exits non-zero and writes nothing.
 *
 * Lumen's palette, spacing, radius, type-size and component-height values
 * are adapted from Adobe's open-source Spectrum design tokens (Apache
 * License 2.0). Lumen is an independent system and is not affiliated with
 * or endorsed by Adobe.
 */
import {readFileSync, writeFileSync} from 'node:fs'
import {dirname, resolve} from 'node:path'
import {fileURLToPath} from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const OUT = resolve(HERE, '../wise_core/static/wise_core/css/lumen-palettes.css')
const SCALES = JSON.parse(readFileSync(resolve(HERE, 'lumen-scales.json'), 'utf8'))

const THEMES = ['light', 'dark']
const STEPS = Object.keys(SCALES.blue)

// data-palette values -> the Lumen hue that becomes the accent. `null` is
// the default (no attribute). `blue` is also accepted explicitly so a
// stored preference from the earlier palette list keeps working.
const ACCENTS = [
    {name: null, hue: 'blue'},
    {name: 'blue', hue: 'blue'},
    {name: 'indigo', hue: 'indigo'},
    {name: 'purple', hue: 'purple'},
    {name: 'green', hue: 'green'},
    {name: 'amber', hue: 'yellow'},
]

// ── color math ───────────────────────────────────────────────────────────
const hexToRgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
const toLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)

function luminance(hex) {
    const [r, g, b] = hexToRgb(hex).map(toLinear)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function contrast(a, b) {
    const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
    return (hi + 0.05) / (lo + 0.05)
}

// ── css ──────────────────────────────────────────────────────────────────
const lines = (hues, themeIndex) => hues.flatMap((hue) =>
    Object.keys(SCALES[hue]).map((step) => `    --lumen-${hue}-${step}: ${SCALES[hue][step][themeIndex]};`))

const scaleBlock = (selector, themeIndex) =>
    `${selector} {\n${lines(Object.keys(SCALES), themeIndex).join('\n')}\n}`

function accentBlock({name, hue}) {
    const selector = name ? `:root[data-palette="${name}"]` : ':root'
    const body = STEPS.map((s) => `    --lumen-accent-${s}: var(--lumen-${hue}-${s});`)
    return `/* ${name ? `data-palette="${name}"` : 'default'} - ${hue} */\n${selector} {\n${body.join('\n')}\n}`
}

// ── contrast checks ──────────────────────────────────────────────────────
// Mirrors the semantic tokens in tokens.css, step for step. Where a token
// reads a different step per theme the table below says so ([light, dark]).
function checks() {
    const failures = []
    const note = (label, where, ratio, min) => {
        if (ratio + 1e-9 < min) failures.push(`${label} (${where}): ${ratio.toFixed(2)} < ${min}`)
    }

    THEMES.forEach((theme, t) => {
        const g = (step) => SCALES.gray[step][t]
        const hue = (name, step) => SCALES[name][step][t]
        const pick = (light, dark) => (t === 0 ? light : dark)

        // The grounds text and controls sit on. `ground` pairs are the ones a
        // component paints; the fills only host text that is already inside
        // a hovered or pressed control.
        const surfaces = {
            page: g(pick('100', '25')),
            'layer-1': g(pick('25', '50')),
            'layer-2': g(pick('25', '75')),
            elevated: g(pick('25', '75')),
        }
        const fills = {
            'fill-hover': g(pick('200', '100')),
            'fill-down': g(pick('300', '200')),
            'fill-subtle': g(pick('75', '100')),
        }
        const grounds = {...surfaces, ...fills}
        const borderDefault = g(pick('600', '500'))
        const borderHover = g(pick('700', '600'))

        // Text: heading, default, subdued on every ground.
        Object.entries(grounds).forEach(([name, bg]) => {
            note(`content-heading on ${name}`, theme, contrast(g('900'), bg), 4.5)
            note(`content-default on ${name}`, theme, contrast(g('800'), bg), 4.5)
            note(`content-subdued on ${name}`, theme, contrast(g('700'), bg), 4.5)
        })

        // Control borders and the focus ring sit on the page and surfaces.
        Object.entries(surfaces).forEach(([name, bg]) => {
            note(`border-default on ${name}`, theme, contrast(borderDefault, bg), 3)
            note(`border-hover on ${name}`, theme, contrast(borderHover, bg), 3)
        })
        // Neutral solid (badges, tooltips, toasts, pressed action buttons).
        note('on-neutral on neutral-background', theme, contrast(g('25'), g('800')), 4.5)
        note('neutral-background on page', theme, contrast(g('800'), surfaces.page), 3)

        // Accent: fill (+ hover and press), text, ring, subtle tint.
        const textStep = '1000' // accent and status text: step 1000 in both themes
        ACCENTS.forEach(({name, hue: h}) => {
            const label = `accent ${name || 'default'}`
            ;[pick('900', '800'), pick('1000', '700'), pick('1100', '600')].forEach((step, i) =>
                note(`on-accent on ${label} fill ${['rest', 'hover', 'down'][i]}`, theme, contrast('#ffffff', hue(h, step)), 4.5))
            Object.entries(grounds).forEach(([gname, bg]) => {
                if (gname === 'fill-down') return
                note(`${label} text on ${gname}`, theme, contrast(hue(h, textStep), bg), 4.5)
            })
            Object.entries(surfaces).forEach(([gname, bg]) =>
                note(`focus ring ${label} on ${gname}`, theme, contrast(hue(h, '800'), bg), 3))
            note(`on-accent-subtle on ${label} subtle`, theme, contrast(hue(h, '1300'), hue(h, '200')), 4.5)
        })

        // Status: negative / positive / informative fills and text.
        ;[['red', 'negative'], ['green', 'positive'], ['blue', 'informative']].forEach(([h, name]) => {
            ;[pick('900', '800'), pick('1000', '700'), pick('1100', '600')].forEach((step, i) => {
                if (name !== 'negative' && i > 0) return
                note(`on-accent on ${name} fill ${['rest', 'hover', 'down'][i]}`, theme, contrast('#ffffff', hue(h, step)), 4.5)
            })
            Object.entries(grounds).forEach(([gname, bg]) => {
                if (gname === 'fill-down') return
                note(`${name}-content on ${gname}`, theme, contrast(hue(h, textStep), bg), 4.5)
            })
        })
        const noticeFill = hue('orange', pick('600', '900'))
        note('on-notice on notice fill', theme, contrast(pick(g('900'), '#000000'), noticeFill), 4.5)
        Object.entries(grounds).forEach(([gname, bg]) => {
            if (gname === 'fill-down') return
            note(`notice-content on ${gname}`, theme, contrast(hue('orange', textStep), bg), 4.5)
        })

        // Tertiary (purple) badge fill.
        note('on-tertiary on tertiary fill', theme, contrast('#ffffff', hue('purple', pick('900', '800'))), 4.5)

        // Status solids next to the page: a badge or toast fill must read as a shape.
        ;[['red', 'negative'], ['green', 'positive'], ['blue', 'informative']].forEach(([h, name]) =>
            note(`${name} fill on page`, theme, contrast(hue(h, pick('900', '800')), surfaces.page), 3))
    })
    return failures
}

const failures = checks()
if (failures.length) {
    console.error(`Contrast check failed (${failures.length}):\n  ` + failures.join('\n  '))
    process.exit(1)
}

const header = `/* ══════════════════════════════════════════════════════════════════════
   GENERATED by scripts/generate_lumen_palettes.mjs - do not edit by hand.

   Lumen reference palettes (--lumen-<hue>-<step>). Each step carries a
   light and a dark value, so the scale already flips with data-theme. The
   semantic color tokens in tokens.css (--color-content-default,
   --color-accent-background, ...) point at these steps; components never
   read them directly - they exist for charts and illustration.

   --lumen-accent-<step> is the accent scale: blue by default, re-pointed by
   data-palette.

   Palette, spacing, radius, type-size and component-height values are
   adapted from Adobe's open-source Spectrum design tokens (Apache
   License 2.0); Lumen is not affiliated with or endorsed by Adobe.
   ══════════════════════════════════════════════════════════════════════ */`

const blocks = [
    header,
    `/* Light */\n${scaleBlock(':root', 0)}`,
    `/* Dark */\n${scaleBlock(':root[data-theme="dark"]', 1)}`,
    ...ACCENTS.map(accentBlock),
]

writeFileSync(OUT, blocks.join('\n\n') + '\n')
console.log(`wrote ${OUT}\ncontrast checks passed`)
