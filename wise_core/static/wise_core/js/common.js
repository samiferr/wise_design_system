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