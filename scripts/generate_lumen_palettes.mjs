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
 *     surface and every neutral fill, in both themes - and on the
 *     translucent row-hover and selected-subtle tints, composited over the
 *     surface they sit on
 *   - the alert tints (neutral / informative / positive / notice /
 *     negative -subtle) hold 4.5:1 for heading and body text, and 3:1 for
 *     the status icon and border drawn on them
 *   - an invalid field's border (negative-border) holds 3:1, also as the
 *     inset outline on the borderless picker fill
 *   - a focused field's border (border-focus) holds 3:1 on every surface and
 *     against the resting border it replaces
 *   - a control's border and the focus ring hold 3:1 on the page and surfaces
 *   - white text holds 4.5:1 on every accent / negative / status fill, in
 *     its rest, hover and pressed steps
 *   - the accent and status colors as text hold 4.5:1 on the page, every
 *     surface and the hover / subtle fills, for every accent
 *
 * It writes three things:
 *
 *   1. the scales, light under :root and dark under [data-theme="dark"]
 *   2. data-palette: the accent options. Each is defined by ONE OKLCH color
 *      (the fill of the main action in light) in ACCENTS below; the script
 *      grows a full 16-step --lumen-accent-<step> scale from it, light and
 *      dark, on the lightness ladder of the nearest Lumen hue, and checks it
 *      like every other scale. If white text would fall under 4.5:1 on the
 *      given color it is darkened (same hue and chroma) just enough
 *   3. --lumen-swatch-<name>: the rest fill of each option, so a picker can
 *      show every option whatever the current accent is
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

// The accent options (data-palette). Each is one OKLCH color - the fill of
// the main action in light - plus `ref`, the Lumen hue whose lightness and
// chroma ladder the 16-step scale follows. `blue` (the default, no
// attribute) is also accepted explicitly, so a stored preference keeps
// working. Preferences from the earlier palette list (indigo, purple,
// amber) match nothing and fall back to the default.
const ACCENT_COLORS = [
    {id: 'blue', label: 'Blue', oklch: [54.6, 0.1724, 254.2], ref: 'blue'},
    {id: 'red', label: 'Red', oklch: [58.29, 0.1941, 25.59], ref: 'red'},
    {id: 'graphite', label: 'Graphite', oklch: [27.39, 0.0055, 286.03], ref: 'blue'},
    {id: 'green', label: 'Green', oklch: [64.32, 0.1338, 164.7], ref: 'green'},
]
// data-palette values -> accent id. `null` is the default (no attribute).
const ACCENTS = [
    {name: null, id: 'blue'},
    ...ACCENT_COLORS.map(({id}) => ({name: id, id})),
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

// `fg` at `alpha` over `bg`, as an opaque hex - how a translucent token
// (row-hover is 7% gray-900, selected-subtle 10% accent) really paints.
function blend(fg, alpha, bg) {
    const f = hexToRgb(fg)
    const b = hexToRgb(bg)
    return '#' + f.map((c, i) => Math.round((c * alpha + b[i] * (1 - alpha)) * 255).toString(16).padStart(2, '0')).join('')
}

// ── OKLCH ────────────────────────────────────────────────────────────────
const toSrgb = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055)

function oklabToLinear(L, a, b) {
    const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    const s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3
    return [
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
    ]
}

// OKLCH -> sRGB hex. A color outside the sRGB gamut keeps its lightness and
// hue and loses chroma until it fits.
function oklchToHex(L, C, H) {
    if (L >= 1) return '#ffffff'
    if (L <= 0) return '#000000'
    const h = (H * Math.PI) / 180
    for (let c = C, i = 0; i < 120; i++, c *= 0.97) {
        const lin = oklabToLinear(L, c * Math.cos(h), c * Math.sin(h))
        if (lin.every((x) => x >= -1e-4 && x <= 1 + 1e-4)) {
            return '#' + lin.map((x) => Math.round(Math.min(1, Math.max(0, toSrgb(Math.min(1, Math.max(0, x))))) * 255)
                .toString(16).padStart(2, '0')).join('')
        }
    }
    return oklchToHex(L, 0, 0)
}

function hexToOklch(hex) {
    const [r, g, b] = hexToRgb(hex).map(toLinear)
    const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s
    const a = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s
    const bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s
    return [L, Math.hypot(a, bb), ((Math.atan2(bb, a) * 180) / Math.PI + 360) % 360]
}

// The 16-step accent scale for one option, {light: {step: hex}, dark: {...}}.
// Lightness follows the reference hue's ladder, re-anchored so light step 900
// IS the given color (darkened only if white text on it would fall under
// 4.5:1); chroma follows the reference ladder scaled to the given chroma; the
// hue is the given hue. Dark keeps the reference's own (flipped) lightness
// ladder, nudged down at the low steps only if white on dark step 800 - the
// dark accent fill - would fall under 4.5:1.
function buildAccentScale({oklch: [l, c, h], ref}) {
    const lch = (theme, step) => hexToOklch(SCALES[ref][step][theme])
    const ratio = c / lch(0, '900')[1]
    const hex = (L, chroma) => oklchToHex(L, chroma, h)

    let fill = l / 100
    while (contrast('#ffffff', hex(fill, c)) < 4.5) fill -= 0.002

    const [top, bottom] = [lch(0, '100')[0], lch(0, '1600')[0]]
    const mid = lch(0, '900')[0]
    const light = {}
    STEPS.forEach((step) => {
        const [rl, rc] = lch(0, step)
        const L = Number(step) <= 900
            ? fill + ((rl - mid) / (top - mid)) * (top - fill)
            : fill - ((mid - rl) / (mid - bottom)) * (fill - bottom)
        light[step] = hex(L, rc * ratio)
    })

    // Accent text is step 1000. Make sure it still reads inside a selected
    // row on the bare gray page (10% accent, or 7% gray on hover, over gray-100) -
    // the hardest ground it meets - by darkening it if the ladder left it a touch light.
    const page = SCALES.gray['100'][0]
    const worst = [blend(light['900'], 0.1, page), blend(SCALES.gray['900'][0], 0.07, page)]
    let text = fill - ((mid - lch(0, '1000')[0]) / (mid - bottom)) * (fill - bottom)
    while (worst.some((bg) => contrast(hex(text, lch(0, '1000')[1] * ratio), bg) < 4.55)) text -= 0.002
    light['1000'] = hex(text, lch(0, '1000')[1] * ratio)

    let drop = 0
    const [d800L, d800C] = lch(1, '800')
    while (contrast('#ffffff', hex(d800L + drop, d800C * ratio)) < 4.5) drop -= 0.002
    const dark = {}
    STEPS.forEach((step) => {
        const [rl, rc] = lch(1, step)
        const weight = Number(step) <= 800 ? 1 : Math.max(0, (1100 - Number(step)) / 300)
        dark[step] = hex(rl + drop * weight, rc * ratio)
    })
    return {light, dark}
}

const ACCENT_SCALES = Object.fromEntries(ACCENT_COLORS.map((a) => [a.id, buildAccentScale(a)]))

// ── css ──────────────────────────────────────────────────────────────────
const lines = (hues, themeIndex) => hues.flatMap((hue) =>
    Object.keys(SCALES[hue]).map((step) => `    --lumen-${hue}-${step}: ${SCALES[hue][step][themeIndex]};`))

const scaleBlock = (selector, themeIndex) =>
    `${selector} {\n${lines(Object.keys(SCALES), themeIndex).join('\n')}\n}`

// One accent option: its light scale under :root[data-palette] and its dark
// scale under :root[data-theme="dark"][data-palette] (more specific than the
// default dark block, so the order of the blocks never matters).
function accentBlock({name, id}) {
    const body = (theme) => STEPS.map((step) => `    --lumen-accent-${step}: ${ACCENT_SCALES[id][theme][step]};`).join('\n')
    const [light, dark] = name
        ? [`:root[data-palette="${name}"]`, `:root[data-theme="dark"][data-palette="${name}"]`]
        : [':root', ':root[data-theme="dark"]']
    return `/* ${name ? `data-palette="${name}"` : 'default'} - ${id} */\n${light} {\n${body('light')}\n}\n${dark} {\n${body('dark')}\n}`
}

const swatchBlock = () => `/* One swatch per accent option - its rest fill in light - so a picker can show every option whatever the current accent is. */
:root {
${ACCENT_COLORS.map(({id}) => `    --lumen-swatch-${id}: ${ACCENT_SCALES[id].light['900']};`).join('\n')}
}`

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
            // text fields, text areas, selects, OTP boxes: gray-300 (#dadada in light); hover gray-400
            'fill-field': g('300'),
            'fill-field-hover': g('400'),
        }
        const grounds = {...surfaces, ...fills}
        const borderDefault = g(pick('600', '600'))
        const borderHover = g(pick('700', '700'))

        // Text: heading, default, subdued on every ground.
        Object.entries(grounds).forEach(([name, bg]) => {
            note(`content-heading on ${name}`, theme, contrast(g('900'), bg), 4.5)
            note(`content-default on ${name}`, theme, contrast(g('800'), bg), 4.5)
            if (name !== 'fill-field-hover') note(`content-subdued on ${name}`, theme, contrast(g('700'), bg), 4.5)
        })

        // Control borders and the focus ring sit on the page and surfaces.
        Object.entries(surfaces).forEach(([name, bg]) => {
            note(`border-default on ${name}`, theme, contrast(borderDefault, bg), 3)
            note(`border-hover on ${name}`, theme, contrast(borderHover, bg), 3)
        })
        // A focused field's border turns border-focus (gray-900): it must hold
        // 3:1 on every surface AND against the resting border it replaces,
        // or the change is invisible.
        const borderFocus = g('900')
        Object.entries(surfaces).forEach(([name, bg]) =>
            note(`border-focus on ${name}`, theme, contrast(borderFocus, bg), 3))
        note('border-focus against border-default (the focus change)', theme, contrast(borderFocus, borderDefault), 3)

        // Field fills (#dadada in light): the control's own border, the focused
        // border and the invalid outline must still hold 3:1 against them, and
        // the borderless select relies on the deeper hover fill too.
        note('border-default on fill-field', theme, contrast(borderDefault, fills['fill-field']), 3)
        note('border-focus on fill-field', theme, contrast(borderFocus, fills['fill-field']), 3)
        note('negative-border on fill-field', theme, contrast(hue('red', '900'), fills['fill-field']), 3)
        // The hover fill belongs to the borderless select only: its value text
        // is content-default (no placeholder), and invalid is the inset outline.
        note('negative-border-hover on fill-field-hover', theme, contrast(hue('red', '1000'), fills['fill-field-hover']), 3)

        // Invalid fields: the 1px negative-border (and its hover step) is a
        // control boundary like border-default.
        Object.entries(surfaces).forEach(([name, bg]) => {
            note(`negative-border on ${name}`, theme, contrast(hue('red', '900'), bg), 3)
            note(`negative-border-hover on ${name}`, theme, contrast(hue('red', '1000'), bg), 3)
        })

        // Neutral solid (badges, tooltips, toasts, pressed action buttons).
        note('on-neutral on neutral-background', theme, contrast(g('25'), g('800')), 4.5)
        note('neutral-background on page', theme, contrast(g('800'), surfaces.page), 3)

        // Accent: fill (+ hover and press), text, ring, subtle tint.
        const textStep = '1000' // accent and status text: step 1000 in both themes
        const acc = (id, step) => ACCENT_SCALES[id][theme][step]
        ACCENT_COLORS.forEach(({id}) => {
            const label = `accent ${id}`
            ;[pick('900', '800'), pick('1000', '700'), pick('1100', '600')].forEach((step, i) =>
                note(`on-accent on ${label} fill ${['rest', 'hover', 'down'][i]}`, theme, contrast('#ffffff', acc(id, step)), 4.5))
            Object.entries(grounds).forEach(([gname, bg]) => {
                if (gname === 'fill-down' || gname.startsWith('fill-field')) return
                note(`${label} text on ${gname}`, theme, contrast(acc(id, textStep), bg), 4.5)
            })
            Object.entries(surfaces).forEach(([gname, bg]) =>
                note(`focus ring ${label} on ${gname}`, theme, contrast(acc(id, '800'), bg), 3))
            note(`on-accent-subtle on ${label} subtle`, theme, contrast(acc(id, '1300'), acc(id, '200')), 4.5)
            note(`${label} fill on page`, theme, contrast(acc(id, pick('900', '800')), surfaces.page), 3)
        })

        // Status: negative / positive / informative fills and text.
        ;[['red', 'negative'], ['green', 'positive'], ['blue', 'informative']].forEach(([h, name]) => {
            ;[pick('900', '800'), pick('1000', '700'), pick('1100', '600')].forEach((step, i) => {
                if (name !== 'negative' && i > 0) return
                note(`on-accent on ${name} fill ${['rest', 'hover', 'down'][i]}`, theme, contrast('#ffffff', hue(h, step)), 4.5)
            })
            Object.entries(grounds).forEach(([gname, bg]) => {
                if (gname === 'fill-down' || gname.startsWith('fill-field')) return
                note(`${name}-content on ${gname}`, theme, contrast(hue(h, textStep), bg), 4.5)
            })
        })
        const noticeFill = hue('orange', pick('600', '900'))
        note('on-notice on notice fill', theme, contrast(pick(g('900'), '#000000'), noticeFill), 4.5)
        Object.entries(grounds).forEach(([gname, bg]) => {
            if (gname === 'fill-down' || gname.startsWith('fill-field')) return
            note(`notice-content on ${gname}`, theme, contrast(hue('orange', textStep), bg), 4.5)
        })

        // Row tints: hover is 7% gray-900, selected 10% (hover 15%) accent-900,
        // painted over the page or a surface. Text inside must still read.
        // Neutral text is checked everywhere; an accent's own text on its own
        // selected tint too (a link inside a selected row); status text on
        // the surfaces a selected row actually lives in - a card or a panel,
        // never the bare page.
        const rowGrounds = []
        ;['page', 'layer-2'].forEach((sname) =>
            rowGrounds.push({label: `row-hover on ${sname}`, bg: blend(g('900'), 0.07, surfaces[sname]), accents: ACCENT_COLORS.map((a) => a.id), status: true}))
        ACCENT_COLORS.forEach(({id}) => {
            ;['page', 'layer-2'].forEach((sname) =>
                [[0.1, 'selected-subtle'], [0.15, 'selected-subtle-hover']].forEach(([alpha, token]) => {
                    if (sname === 'page' && alpha > 0.1) return
                    rowGrounds.push({
                        label: `${token} (${id}) on ${sname}`, bg: blend(acc(id, '900'), alpha, surfaces[sname]),
                        accents: [id], status: sname !== 'page',
                    })
                }))
        })
        rowGrounds.forEach(({label, bg, accents, status}) => {
            note(`content-heading on ${label}`, theme, contrast(g('900'), bg), 4.5)
            note(`content-default on ${label}`, theme, contrast(g('800'), bg), 4.5)
            note(`content-subdued on ${label}`, theme, contrast(g('700'), bg), 4.5)
            accents.forEach((id) => note(`accent ${id} text on ${label}`, theme, contrast(acc(id, textStep), bg), 4.5))
            if (status) note(`negative-content on ${label}`, theme, contrast(hue('red', textStep), bg), 4.5)
        })

        // Alert tints: heading and body text on the *-subtle fill, and the
        // status icon / border (the -content color) drawn on it.
        ;[['neutral', g('75'), g('800')], ['informative', hue('blue', '200'), hue('blue', textStep)],
            ['positive', hue('green', '200'), hue('green', textStep)], ['notice', hue('orange', '200'), hue('orange', textStep)],
            ['negative', hue('red', '200'), hue('red', textStep)]].forEach(([name, bg, icon]) => {
            note(`content-heading on ${name}-subtle`, theme, contrast(g('900'), bg), 4.5)
            note(`content-default on ${name}-subtle`, theme, contrast(g('800'), bg), 4.5)
            note(`${name} icon on ${name}-subtle`, theme, contrast(icon, bg), 3)
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

   --lumen-accent-<step> is the accent scale: blue by default, replaced by
   data-palette (red, graphite, green). Each accent is grown from one OKLCH
   color in ACCENT_COLORS (scripts/generate_lumen_palettes.mjs).

   Palette, spacing, radius, type-size and component-height values are
   adapted from Adobe's open-source Spectrum design tokens (Apache
   License 2.0); Lumen is not affiliated with or endorsed by Adobe.
   ══════════════════════════════════════════════════════════════════════ */`

const blocks = [
    header,
    `/* Light */\n${scaleBlock(':root', 0)}`,
    `/* Dark */\n${scaleBlock(':root[data-theme="dark"]', 1)}`,
    swatchBlock(),
    ...ACCENTS.map(accentBlock),
]

writeFileSync(OUT, blocks.join('\n\n') + '\n')
console.log(`wrote ${OUT}\ncontrast checks passed`)
