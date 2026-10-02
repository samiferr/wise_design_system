import itertools
import re
from functools import lru_cache
from pathlib import Path

from django.template import Library
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = Library()

# Resolved relative to this file (wise_core/templatetags/wise_icons.py), not
# settings.BASE_DIR: BASE_DIR is the *host* project's root, which is not
# necessarily wise_core's parent directory (e.g. the demo project's BASE_DIR
# is demo/, one level below the repo root where wise_core actually lives).
_ICON_DIR = Path(__file__).resolve().parent.parent / 'static' / 'wise_core' / 'icons' / 'lucide'

# Lumen draws Lucide's 24-unit grid at five sizes tied to the control an icon
# sits in (16 in a small button, 20 in a medium one, 22 in a large one, 26 in
# an extra-large one) with a 2.4 stroke: 2px at 20px, scaling with the size.
ICON_SIZES = {'xs': 14, 's': 16, 'm': 20, 'l': 22, 'xl': 26}
DEFAULT_SIZE = 'm'
DEFAULT_STROKE_WIDTH = '2.4'

# Lumen's own icon names, for the Lucide icons whose names differ. Every other
# Lumen name is the Lucide name, so `{% lucide "add" %}` and `{% lucide "plus" %}`
# draw the same icon.
LUMEN_NAMES = {
    'add': 'plus',
    'remove': 'minus',
    'close': 'x',
    'home': 'house',
    'delete': 'trash-2',
    'edit': 'pencil',
    'sort': 'arrow-up-down',
    'more': 'ellipsis',
    'grid': 'layout-grid',
    'chat': 'message-square',
    'sliders': 'sliders-horizontal',
    'alert': 'alert-triangle',
    'error': 'circle-alert',
    'success': 'circle-check',
    'help': 'circle-question-mark',
    'unlock': 'lock-open',
    'refresh': 'refresh-cw',
}


def _icon_dir():
    return _ICON_DIR


@lru_cache(maxsize=None)
def _load_icon(name):
    path = _icon_dir() / f'{name}.svg'
    with open(path, encoding='utf-8') as f:
        return f.read()


def _pixels(size):
    """`size` is a Lumen step (`xs`..`xl`) or a number of pixels."""
    return ICON_SIZES.get(str(size), size)


@register.simple_tag
def lucide(name, size=DEFAULT_SIZE, cls='', stroke_width=DEFAULT_STROKE_WIDTH, label='', **kwargs):
    """
    Render a vendored Lucide icon inline (not <img>) so it sizes itself via
    its own width/height/viewBox and inherits color from Tailwind text-*
    utilities via currentColor.

    Usage: {% lucide "search" size="s" cls="text-gray-500" %}

    `size` is one of Lumen's steps - xs (14), s (16), m (20, the default),
    l (22), xl (26) - or a number of pixels. `stroke_width` is in Lucide's
    24-unit grid: the default 2.4 is 2px at 20px and the stroke scales with
    the size; only set it for a glyph inside a small control (a sort arrow or
    chevron is 2.6, a checkbox tick 3.6). Without `label` the icon is hidden
    from assistive technology; with it, it is an image with that name.
    """
    if 'class' in kwargs:
        cls = f"{cls} {kwargs['class']}".strip()
    if 'aria-label' in kwargs and not label:
        label = kwargs['aria-label']

    try:
        svg = _load_icon(LUMEN_NAMES.get(name, name))
    except FileNotFoundError:
        return mark_safe(f'<!-- unknown lucide icon: {name} -->')

    px = _pixels(size)
    svg = re.sub(r'<!--.*?-->\s*', '', svg, count=1, flags=re.S)
    svg = re.sub(r'\bwidth="24"', f'width="{px}"', svg, count=1)
    svg = re.sub(r'\bheight="24"', f'height="{px}"', svg, count=1)
    svg = re.sub(r'\bstroke-width="2"', f'stroke-width="{stroke_width}"', svg, count=1)
    extra = f' {cls}' if cls else ''
    svg = re.sub(r'class="lucide lucide-([\w-]+)"', rf'class="lucide lucide-\1{extra}"', svg, count=1)
    if label:
        a11y = format_html('role="img" aria-label="{}"', label)
    else:
        a11y = 'aria-hidden="true" focusable="false"'
    return mark_safe(svg.strip().replace('<svg', f'<svg {a11y}', 1))


# ── Status glyphs ───────────────────────────────────────────────────────
# Lumen's four status glyphs are filled - a disc (a triangle for "notice") with
# the Lucide glyph cut out of it - because Lucide has no filled set. They carry
# a status in an alert, a toast or a field message, always next to a word.
_STATUS_GLYPHS = {
    'info': ('<circle cx="12" cy="12" r="10"/>', '<path d="M12 16v-4"/><path d="M12 8h.01"/>'),
    'positive': ('<circle cx="12" cy="12" r="10"/>', '<path d="m9 12 2 2 4-4"/>'),
    'negative': ('<circle cx="12" cy="12" r="10"/>', '<path d="M12 8v4"/><path d="M12 16h.01"/>'),
    'notice': (
        '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>',
        '<path d="M12 9v4"/><path d="M12 17h.01"/>',
    ),
}
_STATUS_ALIASES = {
    'informative': 'info', 'neutral': 'info',
    'success': 'positive',
    'warning': 'notice',
    'error': 'negative', 'danger': 'negative',
}
_glyph_ids = itertools.count(1)


@register.simple_tag
def status_glyph(status, size=18, cls=''):
    """
    Render one of Lumen's filled status glyphs: info, positive, notice or
    negative (also informative / neutral, success, warning, error / danger).
    Colored by `currentColor`, so wrap it in the status family's content color
    (`.callout-*` and `.toast-*` already do). Decorative: the message beside it
    names the status.

    Usage: {% status_glyph "positive" size=18 cls="callout-icon" %}
    """
    status = _STATUS_ALIASES.get(status, status)
    try:
        shape, glyph = _STATUS_GLYPHS[status]
    except KeyError:
        return mark_safe(f'<!-- unknown status glyph: {status} -->')
    # Every glyph owns its mask: a shared id would break once the first copy sits
    # inside a hidden dialog or drawer (a display:none mask is not applied).
    mask_id = f'wise-glyph-{next(_glyph_ids)}'
    classes = f'status-glyph {cls}'.strip()
    return format_html(
        '<svg class="{}" width="{}" height="{}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
        '<mask id="{}"><rect width="24" height="24" fill="#fff"/>'
        '<g fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{}</g>'
        '</mask>'
        '<g fill="currentColor" mask="url(#{})">{}</g></svg>',
        classes, _pixels(size), _pixels(size), mask_id, mark_safe(glyph), mask_id, mark_safe(shape),
    )
