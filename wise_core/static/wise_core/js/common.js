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
// ── Theme / palette / density switching ────────────────────────────────────
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
}

function wiseSetTheme(theme) {
    wiseSetPreference('wise-theme', theme)
}

function wiseSetPalette(palette) {
    wiseSetPreference('wise-palette', palette)
}

function wiseSetDensity(density) {
    wiseSetPreference('wise-density', density)
}

function wiseToggleTheme() {
    var current = document.documentElement.getAttribute('data-theme')
    wiseSetTheme(current === 'dark' ? 'light' : 'dark')
}

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
