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
