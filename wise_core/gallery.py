"""
The image gallery: a record's photos as one large, swipeable image with a
strip of clickable thumbnails beneath it on tablet and desktop, and the
carousel's page-indicator dots on a phone.

`build_image_gallery()` turns any iterable of images - model instances,
dicts, plain URL strings - into the one dict that
`wise_core/components/_image_gallery.html` renders, so the template never
has to know which field holds the file, which holds the alt text, or which
image the visitor asked to see first. `WiseImageGalleryMixin` (in
`wise_core.mixins`) is the class-based-view front end to it; call this
function directly when the images do not hang off a view's object (a docs
page, a dashboard tile).
"""
import re
from collections.abc import Mapping

from django.core.exceptions import ImproperlyConfigured
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

FITS = ('contain', 'cover')
THUMBNAIL_POSITIONS = ('bottom', 'start')

# `1 / 1`, `4/3`, `16 / 9`, `1.5 / 1`. The ratio is written into a `style`
# attribute, so anything else is refused rather than escaped.
_ASPECT_RATIO = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$')


def _resolve(item, name):
    """`name` read off `item`: a callable taking the item, a dict key, or an attribute."""
    if name is None:
        return None
    if callable(name):
        return name(item)
    if isinstance(item, Mapping):
        return item.get(name)
    return getattr(item, name, None)


def image_url(value):
    """
    A URL for whatever an image field holds: a `FieldFile` (an `ImageField`
    or `FileField` value), a plain URL string, or nothing. An empty file
    field is falsy and has no URL - it returns None, so the image is skipped
    rather than rendered as a broken `<img>`.
    """
    if not value:
        return None
    if isinstance(value, str):
        return value
    try:
        return value.url
    except (AttributeError, ValueError):
        return None


def normalize_aspect_ratio(ratio):
    """`(4, 3)` / `'4/3'` / `'4 / 3'` -> `'4 / 3'`; anything else is an ImproperlyConfigured."""
    if isinstance(ratio, (tuple, list)) and len(ratio) == 2:
        ratio = '{} / {}'.format(*ratio)
    match = _ASPECT_RATIO.match(str(ratio))
    if not match or not float(match.group(1)) or not float(match.group(2)):
        raise ImproperlyConfigured(
            'Image gallery aspect_ratio must look like "1 / 1" or (4, 3), not %r.' % (ratio,)
        )
    return '{} / {}'.format(match.group(1), match.group(2))


def _selected_number(selected, count):
    """The 1-based image to show first: `selected` if it is a valid position, else 1."""
    try:
        number = int(selected)
    except (TypeError, ValueError):
        return 1
    return number if 1 <= number <= count else 1


def build_image_gallery(images, *, gallery_id='gallery', label=_('Images'),
                        image_field='image', thumbnail_field=None, alt_field=None,
                        default_alt='', selected=1, aspect_ratio='1 / 1', fit='contain',
                        thumbnail_position='bottom', empty_label=_('No images yet')):
    """
    Resolve `images` into the context `_image_gallery.html` renders.

    `images`
        Any iterable: model instances, dicts, or plain URL strings (a string
        is its own image, alt text and thumbnail).
    `gallery_id`
        The gallery's DOM id; each slide is `<gallery_id>-<number>`, which
        is what the thumbnails link to. Must be unique on the page.
    `label`
        The gallery's accessible name ("Product images").
    `image_field`, `thumbnail_field`, `alt_field`
        Where to read the full-size image, its thumbnail and its alt text
        from: an attribute name, a dict key, or a callable taking the image.
        No thumbnail falls back to the full-size image; no alt text falls
        back to `default_alt` (usually the record's name). Images with no
        file are skipped.
    `selected`
        The 1-based image shown first - typically `?image=3` - clamped to
        the first image when it is missing or out of range.
    `aspect_ratio`
        The stage's (and every thumbnail's) shape, e.g. `'1 / 1'`, `'4 / 3'`
        or `(16, 9)`. Fixed up front, so the page doesn't jump as photos load.
    `fit`
        `'contain'` (the default: the whole photo, letterboxed on the
        surface - right for product shots) or `'cover'` (fill and crop).
    `thumbnail_position`
        `'bottom'` (the default) or `'start'`: a vertical rail beside the
        stage on large screens. Either way phones get dots instead.
    """
    if fit not in FITS:
        raise ImproperlyConfigured('Image gallery fit must be one of %s, not %r.' % (FITS, fit))
    if thumbnail_position not in THUMBNAIL_POSITIONS:
        raise ImproperlyConfigured(
            'Image gallery thumbnail_position must be one of %s, not %r.'
            % (THUMBNAIL_POSITIONS, thumbnail_position)
        )
    gallery_id = slugify(str(gallery_id)) or 'gallery'

    resolved = []
    for image in images:
        if isinstance(image, str):
            src, thumbnail, alt = image, image, None
        else:
            src = image_url(_resolve(image, image_field))
            thumbnail = image_url(_resolve(image, thumbnail_field)) or src
            alt = _resolve(image, alt_field)
        if src:
            resolved.append((src, thumbnail, alt or default_alt))

    count = len(resolved)
    selected_number = _selected_number(selected, count)
    items = [
        {
            'number': number,
            'dom_id': '{}-{}'.format(gallery_id, number),
            'src': src,
            'thumbnail_src': thumbnail,
            'alt': alt,
            'selected': number == selected_number,
        }
        for number, (src, thumbnail, alt) in enumerate(resolved, start=1)
    ]
    return {
        'id': gallery_id,
        'label': label,
        'images': items,
        'count': count,
        'selected': items[selected_number - 1] if items else None,
        'selected_number': selected_number if items else 0,
        'aspect_ratio': normalize_aspect_ratio(aspect_ratio),
        'fit': fit,
        'thumbnail_position': thumbnail_position,
        'empty_label': empty_label,
    }
