// Tailwind's Preflight resets <img> to `max-width:100%; height:auto` for responsive
// images. This app's icons rely on bare <img width="…" height="…"> HTML attributes for
// sizing everywhere, and a CSS-only override can't restore attribute-based sizing (the
// browser only auto-derives an aspect-ratio when BOTH attributes are present, and most
// icons here only set one). Mirror the attributes onto inline style instead, which always
// wins over external stylesheet rules.
function fixImageIfMatching(img) {
    const h = img.getAttribute('height')
    const w = img.getAttribute('width')
    if (h && !img.style.height) img.style.height = h + 'px'
    if (w && !img.style.width) img.style.width = w + 'px'
    if (h && !w) img.style.width = 'auto'
    if (w && !h) img.style.height = 'auto'
}

function fixAttributeSizedImages(root) {
    root.querySelectorAll('img[height], img[width]').forEach(fixImageIfMatching)
}

fixAttributeSizedImages(document)
new MutationObserver(function (mutations) {
    mutations.forEach(function (m) {
        m.addedNodes.forEach(function (node) {
            if (node.nodeType !== 1) return
            if (node.tagName === 'IMG') fixImageIfMatching(node)
            if (node.querySelectorAll) fixAttributeSizedImages(node)
        })
    })
}).observe(document.documentElement, {childList: true, subtree: true})

let closeSideBarButton = document.getElementById("close_sidebar_icon")
let openSideBarButton = document.getElementById("open_sidebar_icon")
let sideBarElm = document.getElementById("mySidebar")
let topBarElm = document.getElementById("top_bar")

function openSideBar() {
    if (!sideBarElm) return;
    sideBarElm.classList.remove("hidden");
    if (openSideBarButton) openSideBarButton.classList.add("hidden");
    if (closeSideBarButton) closeSideBarButton.classList.remove("hidden");
}

function closeSideBar() {
    if (!sideBarElm) return;
    sideBarElm.classList.add("hidden");
    if (openSideBarButton) openSideBarButton.classList.remove("hidden");
    if (closeSideBarButton) closeSideBarButton.classList.add("hidden");
}

window.onscroll = function () {
    closeSideBar()
}


const compressImage = async (file, resize_width, {quality = 1, type = file.type}) => {
    console.log('compressing image...')
    // Get as image data
    const imageBitmap = await createImageBitmap(file);


    // Draw to canvas
    const canvas = document.createElement('canvas');

    //scale the image to 600 (width) and keep aspect ratio
    let scaleFactor = resize_width / imageBitmap.width;
    canvas.width = resize_width;
    canvas.height = imageBitmap.height * scaleFactor;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(imageBitmap, 0, 0, canvas.width, canvas.height);


    // Turn into Blob
    const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, type, quality)
    );
    console.log('Image compressed')
    // Turn Blob into File
    return new File([blob], file.name, {
        type: blob.type,
    });

};
// ── Theme / accent / rounding / card-shadow switching ──────────────────────
// The *initial* value is applied by the inline bootstrap script in base.html
// (before first paint); these helpers only handle switching at runtime and
// persisting the choice. Each writes one attribute on <html>, which the token
// layer keys off - see docs/design-tokens.md.

function wiseSetPreference(name, value) {
    var attr = 'data-' + name.replace('wise-', '')
    if (value) {
        document.documentElement.setAttribute(attr, value)
    } else {
        document.documentElement.removeAttribute(attr)
    }
    try {
        if (value) {
            localStorage.setItem(name, value)
        } else {
            localStorage.removeItem(name)
        }
    } catch (e) { /* storage disabled - the attribute still applies for this page */ }
    wiseSyncPreferenceButtons()
}

// Marks the settings-panel button for the current choice aria-pressed (the
// .btn[aria-pressed="true"] rule in tokens.css fills it). A button declares
// what it sets with data-wise-pref="theme" data-wise-value="dark"; an unset
// attribute means the default - light for the theme, '' for the rest - and
// so does a stored value no button offers any more (an old palette name),
// which the stylesheet ignores too.
function wiseSyncPreferenceButtons() {
    var root = document.documentElement
    var buttons = document.querySelectorAll('[data-wise-pref]')
    var fallback = function (key) { return key === 'theme' ? 'light' : '' }
    var offered = {}
    buttons.forEach(function (button) {
        var key = button.getAttribute('data-wise-pref')
        var own = button.getAttribute('data-wise-value') || fallback(key)
        ;(offered[key] = offered[key] || []).push(own)
    })
    buttons.forEach(function (button) {
        var key = button.getAttribute('data-wise-pref')
        var current = root.getAttribute('data-' + key) || fallback(key)
        if (offered[key].indexOf(current) === -1) current = fallback(key)
        var own = button.getAttribute('data-wise-value') || fallback(key)
        button.setAttribute('aria-pressed', String(current === own))
    })
}

document.addEventListener('DOMContentLoaded', wiseSyncPreferenceButtons)

function wiseSetTheme(theme) {
    wiseSetPreference('wise-theme', theme)
}

function wiseSetPalette(palette) {
    wiseSetPreference('wise-palette', palette)
}

function wiseSetRadius(radius) {
    wiseSetPreference('wise-radius', radius)
}

function wiseSetShadow(shadow) {
    wiseSetPreference('wise-shadow', shadow)
}

function wiseToggleTheme() {
    var current = document.documentElement.getAttribute('data-theme')
    wiseSetTheme(current === 'dark' ? 'light' : 'dark')
}

// ── Settings panel: "Copy tokens" tab ───────────────────────────────────────
// Reads back the *resolved* value of a curated set of custom properties
// (the Lumen semantic tokens, not the full token set - that's 400+ vars, most of them irrelevant to
// a quick copy/paste) plus whichever data-* axis attributes are actually set
// on <html>, so a developer can lift the exact combination chosen on the
// Settings tab out of the live page instead of re-deriving it from
// tokens.css by hand.

var WISE_EXPORT_TOKENS = [
    '--color-background-base', '--color-background-layer-1', '--color-background-layer-2',
    '--color-background-elevated',
    '--color-fill-neutral-hover', '--color-fill-neutral-down',
    '--color-content-heading', '--color-content-default', '--color-content-subdued',
    '--color-border-default', '--color-border-hover', '--color-border-subtle',
    '--color-accent-background', '--color-accent-background-hover', '--color-accent-content',
    '--color-on-accent', '--color-neutral-background', '--color-on-neutral',
    '--color-informative-background', '--color-positive-background', '--color-notice-background',
    '--color-negative-background', '--color-focus-ring',
    '--corner-radius-100', '--corner-radius-500', '--corner-radius-800', '--corner-radius-full',
    '--shadow-card',
    '--component-height-100',
]

function wiseBuildTokenExport() {
    var root = document.documentElement
    var attrs = ['theme', 'palette', 'radius', 'shadow']
        .map(function (key) {
            var value = root.getAttribute('data-' + key)
            return value ? 'data-' + key + '="' + value + '"' : null
        })
        .filter(Boolean)
        .join(' ')

    var style = getComputedStyle(root)
    var lines = WISE_EXPORT_TOKENS.map(function (name) {
        return '    ' + name + ': ' + style.getPropertyValue(name).trim() + ';'
    })

    return (attrs ? '<html ' + attrs + '>' : '<html> (all defaults)') +
        '\n\n:root {\n' + lines.join('\n') + '\n}'
}

function wiseRefreshTokenExport() {
    var el = document.getElementById('wise-token-export')
    if (el) el.textContent = wiseBuildTokenExport()
}

function wiseShowSettingsTab(tab) {
    var showTokens = tab === 'tokens'
    var panels = {controls: !showTokens, tokens: showTokens}
    Object.keys(panels).forEach(function (name) {
        var panel = document.getElementById('wise-settings-tab-' + name)
        var tabButton = document.getElementById('wise-settings-tabbtn-' + name)
        if (panel) panel.classList.toggle('hidden', !panels[name])
        if (tabButton) {
            tabButton.classList.toggle('selected', panels[name])
            tabButton.setAttribute('aria-selected', String(panels[name]))
        }
    })
    if (showTokens) wiseRefreshTokenExport()
}

// ── Dropdown (picker) ──────────────────────────────────────────────────────
// Behavior for `.picker` (see tokens.css and wise_core.widgets.DropdownSelect):
// click or Up/Down on the button opens the listbox; Up/Down/Home/End move the
// active option, Enter or Space chooses, Escape closes and returns focus to
// the button, Tab closes. Choosing writes the hidden input's value and fires a
// bubbling `change` event on it.

function wisePickerParts(picker) {
    return {
        button: picker.querySelector('.picker-button'),
        list: picker.querySelector('.picker-popover'),
        input: picker.querySelector('input[type="hidden"]'),
        options: Array.prototype.slice.call(picker.querySelectorAll('.picker-option')),
    }
}

function wisePickerEnabled(parts) {
    return parts.options.filter(function (o) { return o.getAttribute('aria-disabled') !== 'true' })
}

function wisePickerActivate(parts, option) {
    parts.options.forEach(function (o) { o.classList.toggle('is-active', o === option) })
    if (option) {
        parts.list.setAttribute('aria-activedescendant', option.id)
        option.scrollIntoView({block: 'nearest'})
    }
}

function wisePickerClose(picker, refocus) {
    var parts = wisePickerParts(picker)
    if (parts.list.hidden) return
    parts.list.hidden = true
    parts.button.setAttribute('aria-expanded', 'false')
    if (refocus) parts.button.focus()
}

function wisePickerOpen(picker, last) {
    var parts = wisePickerParts(picker)
    if (parts.button.disabled || !parts.list.hidden) return
    document.querySelectorAll('.picker').forEach(function (p) { if (p !== picker) wisePickerClose(p, false) })
    parts.list.hidden = false
    parts.button.setAttribute('aria-expanded', 'true')
    var enabled = wisePickerEnabled(parts)
    var selected = parts.options.filter(function (o) { return o.getAttribute('aria-selected') === 'true' })[0]
    wisePickerActivate(parts, selected || (last ? enabled[enabled.length - 1] : enabled[0]))
    parts.list.focus()
}

function wisePickerChoose(picker, option) {
    if (!option || option.getAttribute('aria-disabled') === 'true') return
    var parts = wisePickerParts(picker)
    parts.options.forEach(function (o) { o.setAttribute('aria-selected', String(o === option)) })
    var value = parts.button.querySelector('.picker-value')
    value.textContent = option.getAttribute('data-label') || option.querySelector('.picker-option-label').textContent
    value.classList.toggle('is-placeholder', option.getAttribute('data-value') === '')
    if (parts.input) {
        parts.input.value = option.getAttribute('data-value')
        parts.input.dispatchEvent(new Event('change', {bubbles: true}))
    }
    wisePickerClose(picker, true)
}

// Name the button by its <label> plus the chosen value, once, on load.
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.picker-button:not([aria-labelledby]):not([aria-label])').forEach(function (button) {
        var label = button.id ? document.querySelector('label[for="' + button.id + '"]') : null
        var value = button.querySelector('.picker-value')
        if (!label || !value) return
        label.id = label.id || button.id + '_label'
        value.id = value.id || button.id + '_value'
        button.setAttribute('aria-labelledby', label.id + ' ' + value.id)
    })
})

document.addEventListener('click', function (e) {
    var target = e.target.closest ? e.target : e.target.parentElement
    var picker = target && target.closest('.picker')
    if (!picker) {
        document.querySelectorAll('.picker').forEach(function (p) { wisePickerClose(p, false) })
        return
    }
    var option = target.closest('.picker-option')
    if (option) { wisePickerChoose(picker, option); return }
    if (target.closest('.picker-button')) {
        var parts = wisePickerParts(picker)
        if (parts.list.hidden) wisePickerOpen(picker, false)
        else wisePickerClose(picker, true)
    }
})

document.addEventListener('mousemove', function (e) {
    var option = e.target.closest && e.target.closest('.picker-option')
    if (!option || option.getAttribute('aria-disabled') === 'true') return
    wisePickerActivate(wisePickerParts(option.closest('.picker')), option)
})

document.addEventListener('keydown', function (e) {
    var target = e.target
    var picker = target.closest && target.closest('.picker')
    if (!picker) return
    var parts = wisePickerParts(picker)
    if (target === parts.button) {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault()
            wisePickerOpen(picker, e.key === 'ArrowUp')
        }
        return
    }
    if (target !== parts.list) return
    var enabled = wisePickerEnabled(parts)
    var current = parts.options.filter(function (o) { return o.classList.contains('is-active') })[0]
    var index = enabled.indexOf(current)
    var move = function (i) { e.preventDefault(); wisePickerActivate(parts, enabled[Math.max(0, Math.min(enabled.length - 1, i))]) }
    if (e.key === 'ArrowDown') move(index + 1)
    else if (e.key === 'ArrowUp') move(index < 0 ? enabled.length - 1 : index - 1)
    else if (e.key === 'Home') move(0)
    else if (e.key === 'End') move(enabled.length - 1)
    else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); wisePickerChoose(picker, current) }
    else if (e.key === 'Escape') { e.preventDefault(); wisePickerClose(picker, true) }
    else if (e.key === 'Tab') wisePickerClose(picker, false)
})

// ── Search field ───────────────────────────────────────────────────────────
// The clear button of `.search-field` (and Escape in its input) empties the
// input, tells listeners (`input` event), and keeps the focus in the field.

function wiseClearSearch(input) {
    input.value = ''
    input.dispatchEvent(new Event('input', {bubbles: true}))
    input.focus()
}

document.addEventListener('click', function (e) {
    var button = e.target.closest ? e.target.closest('.search-field-clear') : null
    if (!button) return
    var input = button.parentElement.querySelector('input')
    if (input) wiseClearSearch(input)
})

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && e.target.matches && e.target.matches('.search-field > input') && e.target.value) {
        e.preventDefault()
        wiseClearSearch(e.target)
    }
})

// ── Copy button ────────────────────────────────────────────────────────────
// One delegated listener, so buttons rendered later (in a drawer, a dialog, an
// HTMX swap) work with no re-binding.

function wiseCopy(button, text) {
    if (!text) return

    var done = function () {
        button.classList.add('is-copied')
        clearTimeout(button._wiseCopyTimer)
        button._wiseCopyTimer = setTimeout(function () {
            button.classList.remove('is-copied')
        }, 1500)
    }

    // navigator.clipboard needs a secure context; over plain HTTP it is
    // undefined, so fall back to the legacy execCommand path rather than
    // failing silently.
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, function () { wiseCopyFallback(text, done) })
    } else {
        wiseCopyFallback(text, done)
    }
}

function wiseCopyFallback(text, done) {
    var area = document.createElement('textarea')
    area.value = text
    area.setAttribute('readonly', '')
    area.style.position = 'fixed'
    area.style.opacity = '0'
    document.body.appendChild(area)
    area.select()
    try {
        document.execCommand('copy')
        done()
    } catch (e) { /* nothing more we can do - the value stays selected */ }
    document.body.removeChild(area)
}

document.addEventListener('click', function (e) {
    var button = e.target.closest ? e.target.closest('.copy-button') : null
    if (!button) return
    var text = button.dataset.copy
    if (!text && button.dataset.copyTarget) {
        var target = document.querySelector(button.dataset.copyTarget)
        text = target ? (target.innerText || target.textContent) : ''
    }
    wiseCopy(button, text)
})

// ── Dropdown click-away ────────────────────────────────────────────────────
// <details> stays open until its summary is clicked again; this closes any
// open dropdown when the click lands outside it.

document.addEventListener('click', function (e) {
    document.querySelectorAll('details.dropdown[open]').forEach(function (d) {
        if (!d.contains(e.target)) d.removeAttribute('open')
    })
})

document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return
    document.querySelectorAll('details.dropdown[open]').forEach(function (d) {
        d.removeAttribute('open')
    })
})

// ── Dropdown panel positioning ───────────────────────────────────────────────
// .dropdown-panel is `position: absolute` against its .dropdown parent (see
// tokens.css), so a scrollable ancestor - e.g. the overflow-x-auto wrapper a
// wide data-table sits in - clips it once it would extend past that
// ancestor's own edge, typically a row-actions menu on one of the table's
// last rows. Reposition the open panel to `position: fixed`, computed from
// the trigger's own on-screen rect, so it renders relative to the viewport
// instead and is no longer confined by any ancestor's overflow.
//
// Capture phase, not bubble: the native `toggle` event a <details> fires does
// not bubble, but capture-phase listening reaches it regardless - capturing
// is a separate propagation phase that doesn't require bubbling.

function wisePositionDropdownPanel(details) {
    var panel = details.querySelector(':scope > .dropdown-panel')
    var trigger = details.querySelector(':scope > summary')
    if (!panel || !trigger) return
    var rect = trigger.getBoundingClientRect()
    var alignLeft = panel.classList.contains('left-0')
    panel.style.position = 'fixed'
    panel.style.top = rect.bottom + 'px'
    if (alignLeft) {
        panel.style.left = rect.left + 'px'
        panel.style.right = 'auto'
    } else {
        panel.style.left = 'auto'
        panel.style.right = (window.innerWidth - rect.right) + 'px'
    }
    // Keep it on screen: a left-aligned menu on a trigger near the right edge
    // (a row-actions menu in the corner of a card row, on a phone) opens
    // leftwards instead, and one that would run past the bottom opens above
    // its trigger when there is room there.
    var margin = 8
    var box = panel.getBoundingClientRect()
    if (box.right > window.innerWidth - margin) {
        panel.style.left = 'auto'
        panel.style.right = Math.max(margin, window.innerWidth - rect.right) + 'px'
    } else if (box.left < margin) {
        panel.style.left = margin + 'px'
        panel.style.right = 'auto'
    }
    box = panel.getBoundingClientRect()
    if (box.bottom > window.innerHeight - margin && rect.top - box.height - margin > 0) {
        panel.style.top = (rect.top - box.height - margin) + 'px'
    }
}

function wiseResetDropdownPanel(details) {
    var panel = details.querySelector(':scope > .dropdown-panel')
    if (!panel) return
    panel.style.position = ''
    panel.style.top = ''
    panel.style.left = ''
    panel.style.right = ''
}

document.addEventListener('toggle', function (e) {
    var details = e.target
    if (!details.classList || !details.classList.contains('dropdown')) return
    if (details.open) {
        wisePositionDropdownPanel(details)
    } else {
        wiseResetDropdownPanel(details)
    }
}, true)

// ── Dialog / drawer ────────────────────────────────────────────────────────
// The native <dialog> element supplies focus trapping, Esc-to-close and
// top-layer stacking; these are just the open/close calls.

function wiseOpenDialog(id) {
    var dialog = document.getElementById(id)
    if (dialog && typeof dialog.showModal === 'function') dialog.showModal()
}

function wiseCloseDialog(id) {
    var dialog = document.getElementById(id)
    if (dialog && typeof dialog.close === 'function') dialog.close()
}

function wiseOpenDrawer(id) {
    var drawer = document.getElementById(id)
    if (drawer) drawer.classList.remove('hidden')
    var backdrop = document.getElementById(id + '_backdrop')
    if (backdrop) backdrop.classList.remove('hidden')
}

function wiseCloseDrawer(id) {
    var drawer = document.getElementById(id)
    if (drawer) drawer.classList.add('hidden')
    var backdrop = document.getElementById(id + '_backdrop')
    if (backdrop) backdrop.classList.add('hidden')
}

// ── Data table card rows ─────────────────────────────────────────────────────
// `.data-table-cards` shows each row as a card on a phone, every cell as
// "label  value" (see tokens.css). The label is the cell's `data-label`; give
// every body cell without one the text of its column's header, following
// colspans. Call wiseLabelTableCells(root) after inserting a table yourself.

function wiseLabelTableCells(root) {
    (root || document).querySelectorAll('table.data-table-cards').forEach(function (table) {
        var headerRow = table.tHead && table.tHead.rows[table.tHead.rows.length - 1]
        if (!headerRow) return
        var labels = []
        Array.prototype.forEach.call(headerRow.cells, function (th) {
            var text = (th.getAttribute('data-label') !== null ? th.getAttribute('data-label') : th.innerText || th.textContent || '').replace(/\s+/g, ' ').trim()
            for (var i = 0; i < (th.colSpan || 1); i++) labels.push(text)
        })
        Array.prototype.forEach.call(table.tBodies, function (tbody) {
            Array.prototype.forEach.call(tbody.rows, function (row) {
                var column = 0
                Array.prototype.forEach.call(row.cells, function (cell) {
                    if (!cell.hasAttribute('data-label') && (cell.colSpan || 1) === 1) {
                        cell.setAttribute('data-label', labels[column] || '')
                    }
                    column += cell.colSpan || 1
                })
            })
        })
    })
}

document.addEventListener('DOMContentLoaded', function () {
    wiseLabelTableCells(document)
})

// ── Image gallery ─────────────────────────────────────────────────────
// `_image_gallery.html`: the thumbnails are anchors to the slides' ids, so
// they work without this. It makes the jump scroll only the stage (not the
// page), keeps the selected thumbnail and dot in step as the visitor swipes,
// and moves between images with the arrow keys, Home and End.
function wiseGalleryParts(gallery) {
    const stage = gallery.querySelector('.gallery-stage')
    return {
        stage: stage,
        slides: stage ? Array.from(stage.querySelectorAll('.gallery-slide')) : [],
        thumbs: Array.from(gallery.querySelectorAll('.gallery-thumb')),
        dots: Array.from(gallery.querySelectorAll('.gallery-dots > .carousel-dot')),
    }
}

// The slide nearest the stage's centre. Measured from the slides' boxes
// rather than scrollLeft, so it reads the same in right-to-left pages.
function wiseGalleryCurrent(parts) {
    const box = parts.stage.getBoundingClientRect()
    const centre = box.left + box.width / 2
    let best = 0
    let bestDistance = Infinity
    parts.slides.forEach(function (slide, index) {
        const rect = slide.getBoundingClientRect()
        const distance = Math.abs(rect.left + rect.width / 2 - centre)
        if (distance < bestDistance) {
            best = index
            bestDistance = distance
        }
    })
    return best
}

function wiseGalleryMark(parts, index) {
    parts.thumbs.forEach(function (thumb, i) {
        thumb.classList.toggle('selected', i === index)
        if (i === index) thumb.setAttribute('aria-current', 'true')
        else thumb.removeAttribute('aria-current')
    })
    parts.dots.forEach(function (dot, i) {
        dot.classList.toggle('selected', i === index)
    })
    // Keep the selected thumbnail in view in a long strip, without moving the page.
    const thumb = parts.thumbs[index]
    const strip = thumb && thumb.parentElement
    if (strip && strip.scrollWidth > strip.clientWidth) {
        const stripBox = strip.getBoundingClientRect()
        const thumbBox = thumb.getBoundingClientRect()
        if (thumbBox.left < stripBox.left || thumbBox.right > stripBox.right) {
            strip.scrollBy({left: thumbBox.left - stripBox.left - (stripBox.width - thumbBox.width) / 2})
        }
    }
    if (strip && strip.scrollHeight > strip.clientHeight) {
        const stripBox = strip.getBoundingClientRect()
        const thumbBox = thumb.getBoundingClientRect()
        if (thumbBox.top < stripBox.top || thumbBox.bottom > stripBox.bottom) {
            strip.scrollBy({top: thumbBox.top - stripBox.top - (stripBox.height - thumbBox.height) / 2})
        }
    }
}

function wiseGalleryGo(gallery, index, instant) {
    const parts = wiseGalleryParts(gallery)
    if (!parts.slides.length) return
    index = Math.max(0, Math.min(parts.slides.length - 1, index))
    const box = parts.stage.getBoundingClientRect()
    const rect = parts.slides[index].getBoundingClientRect()
    // Hold the highlight on the target while a long smooth jump passes the
    // images in between; the scroll handler lets go once it arrives.
    if (!instant && index !== wiseGalleryCurrent(parts)) gallery.dataset.galleryTarget = index
    parts.stage.scrollTo({
        left: parts.stage.scrollLeft + rect.left - box.left,
        behavior: instant ? 'instant' : undefined,
    })
    wiseGalleryMark(parts, index)
}

function wiseInitGallery(gallery) {
    if (gallery.dataset.galleryReady) return
    gallery.dataset.galleryReady = '1'
    const parts = wiseGalleryParts(gallery)
    if (parts.slides.length < 2) return
    const selected = parseInt(gallery.dataset.gallerySelected, 10) || 1
    if (selected > 1) wiseGalleryGo(gallery, selected - 1, true)
    let frame = null
    parts.stage.addEventListener('scroll', function () {
        if (frame) return
        frame = requestAnimationFrame(function () {
            frame = null
            const current = wiseGalleryCurrent(parts)
            const target = gallery.dataset.galleryTarget
            if (target !== undefined) {
                if (current !== parseInt(target, 10)) return
                delete gallery.dataset.galleryTarget
            }
            wiseGalleryMark(parts, current)
        })
    }, {passive: true})
    // The visitor taking over mid-jump (a swipe, the wheel) drops the hold.
    ;['pointerdown', 'wheel', 'scrollend'].forEach(function (type) {
        parts.stage.addEventListener(type, function () {
            if (gallery.dataset.galleryTarget === undefined) return
            delete gallery.dataset.galleryTarget
            if (type === 'scrollend') wiseGalleryMark(parts, wiseGalleryCurrent(parts))
        }, {passive: true})
    })
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-gallery]').forEach(wiseInitGallery)
})

document.addEventListener('click', function (e) {
    const thumb = e.target.closest('[data-gallery] .gallery-thumb')
    if (!thumb) return
    e.preventDefault()
    wiseGalleryGo(thumb.closest('[data-gallery]'), parseInt(thumb.dataset.galleryIndex, 10) || 0)
})

document.addEventListener('keydown', function (e) {
    const stage = e.target.closest && e.target.closest('[data-gallery] .gallery-stage')
    if (!stage || e.altKey || e.ctrlKey || e.metaKey) return
    const gallery = stage.closest('[data-gallery]')
    const parts = wiseGalleryParts(gallery)
    const current = wiseGalleryCurrent(parts)
    const rtl = getComputedStyle(stage).direction === 'rtl'
    const next = {
        ArrowRight: rtl ? current - 1 : current + 1,
        ArrowLeft: rtl ? current + 1 : current - 1,
        Home: 0,
        End: parts.slides.length - 1,
    }[e.key]
    if (next === undefined) return
    e.preventDefault()
    wiseGalleryGo(gallery, next)
})
