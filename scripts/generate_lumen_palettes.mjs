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
 * contrast promises the semantic tokens in tokens.css make:
 *
 *   - body / subdued text holds 4.5:1 on every layer, fill and palette
 *   - a control border holds 3:1 on the page
 *   - white text holds 4.5:1 on every accent fill, and the accent as text
 *     holds 4.5:1 on every layer
 *
 * It writes three things:
 *
 *   1. the scales, light under :root and dark under [data-theme="dark"]
 *   2. data-palette: one block per accent hue that re-points the
 *      --lumen-accent-<step> scale (blue is the default). Every Lumen hue is
 *      built to the same contrast ladder, so any hue can be the accent
 *   3. data-bg: warm and cool variants of the neutral scale, tinted in
 *      OKLab (lightness is kept, so the contrast checks hold)
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

// Neutral-only overrides for the data-bg axis (OKLab hue in degrees, chroma).
const BACKGROUNDS = [
    {name: 'warm', hue: 75, chroma: 0.012},
    {name: 'cool', hue: 255, chroma: 0.012},
]

// ── color math ───────────────────────────────────────────────────────────
const hexToRgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
const toLinear = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
const toGamma = (c) => (c <= 0.0031308 ? c * 12.92 : 1.055 * c ** (1 / 2.4) - 0.055)

function luminance(hex) {
    const [r, g, b] = hexToRgb(hex).map(toLinear)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function contrast(a, b) {
    const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
    return (hi + 0.05) / (lo + 0.05)
}

function rgbToOklab(hex) {
    const [r, g, b] = hexToRgb(hex).map(toLinear)
    const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return [
        0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s,
    ]
}

function oklabToRgb([L, a, b]) {
    const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    const s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3
    return [
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
    ]
}

const inGamut = (rgb) => rgb.every((c) => c >= -0.0005 && c <= 1.0005)

function rgbToHex(rgb) {
    return '#' + rgb.map((c) => Math.round(Math.min(1, Math.max(0, toGamma(Math.min(1, Math.max(0, c))))) * 255)
        .toString(16).padStart(2, '0')).join('')
}

// Re-hue a neutral: keep its lightness, give it `chroma` at `hue`, and pull
// the chroma back until the result is a real sRGB color. Pure white and
// black are left alone except that white is dipped to L 0.985 so the tint
// has somewhere to live; steps near either end get a fraction of the chroma.
function tint(hex, hue, chroma) {
    const [L0] = rgbToOklab(hex)
    if (L0 < 0.02) return hex
    const L = Math.min(L0, 0.985)
    const edge = Math.min(1, (L < 0.5 ? L : 1 - L) / 0.25 + 0.35)
    const rad = (hue * Math.PI) / 180
    for (let c = chroma * Math.min(1, edge); c >= 0; c -= 0.0005) {
        const rgb = oklabToRgb([L, c * Math.cos(rad), c * Math.sin(rad)])
        if (inGamut(rgb)) return rgbToHex(rgb)
    }
    return hex
}

// ── css ──────────────────────────────────────────────────────────────────
const lines = (hues, themeIndex, mapper = (v) => v) => hues.flatMap((hue) =>
    Object.keys(SCALES[hue]).map((step) => `    --lumen-${hue}-${step}: ${mapper(SCALES[hue][step][themeIndex])};`))

const scaleBlock = (selector, themeIndex) =>
    `${selector} {\n${lines(Object.keys(SCALES), themeIndex).join('\n')}\n}`

function accentBlock({name, hue}) {
    const selector = name ? `:root[data-palette="${name}"]` : ':root'
    const body = STEPS.map((s) => `    --lumen-accent-${s}: var(--lumen-${hue}-${s});`)
    return `/* ${name ? `data-palette="${name}"` : 'default'} - ${hue} */\n${selector} {\n${body.join('\n')}\n}`
}

function backgroundBlocks({name, hue, chroma}) {
    const tinted = (themeIndex) => lines(['gray'], themeIndex, (v) => tint(v, hue, chroma)).join('\n')
    return `/* data-bg="${name}" - neutral scale tinted at OKLab hue ${hue}, chroma ${chroma} */\n` +
        `:root[data-bg="${name}"] {\n${tinted(0)}\n}\n\n` +
        `:root[data-bg="${name}"][data-theme="dark"] {\n${tinted(1)}\n}`
}

// ── contrast checks ──────────────────────────────────────────────────────
// Mirrors the semantic tokens in tokens.css. A `step` reads the same step of
// a hue in both themes unless a [light, dark] pair says otherwise.
function checks() {
    const failures = []
    const note = (label, theme, ratio, min) => {
        if (ratio + 1e-9 < min) failures.push(`${label} (${theme}): ${ratio.toFixed(2)} < ${min}`)
    }
    const variants = [{label: 'default', gray: (hex) => hex}]
    BACKGROUNDS.forEach((bg) => variants.push({label: `bg=${bg.name}`, gray: (hex) => tint(hex, bg.hue, bg.chroma)}))

    THEMES.forEach((theme, t) => {
        variants.forEach((variant) => {
            const g = (step) => variant.gray(SCALES.gray[step][t])
            const hue = (name, step) => SCALES[name][step][t]
            const where = `${theme}, ${variant.label}`
            const layers = {base: g('25'), 'layer-1': g('50'), 'layer-2': t === 0 ? g('25') : g('75'),
                'fill-hover': g('100'), 'fill-down': g('200')}

            Object.entries(layers).forEach(([name, bg]) => {
                note(`content-default on ${name}`, where, contrast(g('800'), bg), 4.5)
                note(`content-subdued on ${name}`, where, contrast(g('700'), bg), 4.5)
                note(`content-heading on ${name}`, where, contrast(g('900'), bg), 4.5)
            })
            note('border-default on base', where, contrast(g('500'), layers.base), 3)
            note('neutral-background / on-neutral', where, contrast(g('800'), g('25')), 4.5)

            ACCENTS.forEach(({name, hue: h}) => {
                const label = `accent ${name || 'default'}`
                const fill = hue(h, t === 0 ? '900' : '800')
                note(`on-accent on ${label} fill`, where, contrast('#ffffff', fill), 4.5)
                const text = hue(h, '900')
                ;['base', 'layer-1', 'layer-2'].forEach((layer) =>
                    note(`${label} text on ${layer}`, where, contrast(text, layers[layer]), 4.5))
                note(`focus ring ${label} on base`, where, contrast(hue(h, '800'), layers.base), 3)
            })

            ;[['red', 'negative'], ['green', 'positive'], ['blue', 'informative']].forEach(([h, name]) => {
                const fill = hue(h, t === 0 ? '900' : '800')
                note(`on-accent on ${name} fill`, where, contrast('#ffffff', fill), 4.5)
                ;['base', 'layer-2'].forEach((layer) =>
                    note(`${name} content on ${layer}`, where, contrast(hue(h, '900'), layers[layer]), 4.5))
            })
            const noticeFill = hue('orange', t === 0 ? '600' : '900')
            note('on-notice on notice fill', where, contrast(t === 0 ? g('900') : '#000000', noticeFill), 4.5)
            note('notice content on base', where, contrast(hue('orange', '900'), layers.base), 4.5)
        })
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
   data-palette. data-bg blocks come last so they override the neutrals.

   Palette, spacing, radius, type-size and component-height values are
   adapted from Adobe's open-source Spectrum design tokens (Apache
   License 2.0); Lumen is not affiliated with or endorsed by Adobe.
   ══════════════════════════════════════════════════════════════════════ */`

const blocks = [
    header,
    `/* Light */\n${scaleBlock(':root', 0)}`,
    `/* Dark */\n${scaleBlock(':root[data-theme="dark"]', 1)}`,
    ...ACCENTS.map(accentBlock),
    ...BACKGROUNDS.map(backgroundBlocks),
]

writeFileSync(OUT, blocks.join('\n\n') + '\n')
console.log(`wrote ${OUT}\ncontrast checks passed`)
