import re
from functools import lru_cache
from pathlib import Path

from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

# NOTE: the DCMS7 original (core/templatetags/icons.py) resolves this directory as
# `settings.BASE_DIR / 'core' / 'static' / 'core' / 'icons' / 'lucide'` — i.e. relative to the
# *host project's* BASE_DIR, because `core` is only ever vendored directly inside DCMS7 itself.
# That assumption doesn't hold for a package meant to be dropped into arbitrary projects, so this
# extracted copy resolves the icon directory relative to this file instead. This is the one
# behavioral adaptation made during extraction — see docs/autocomplete-widget.md.
_ICON_DIR = Path(__file__).resolve().parent.parent / 'static' / 'wise_autocomplete' / 'icons'


@lru_cache(maxsize=None)
def _load_icon(name):
    path = _ICON_DIR / f'{name}.svg'
    with open(path, encoding='utf-8') as f:
        return f.read()


@register.simple_tag
def lucide(name, size=18, cls='', stroke_width='1.5', **kwargs):
    """
    Render a vendored Lucide icon inline (not <img>) so it sizes itself via its own
    width/height/viewBox and inherits color from Tailwind text-* utilities via currentColor.
    """
    # Handle 'class' keyword argument which is common in Django templates
    if 'class' in kwargs:
        cls = f"{cls} {kwargs['class']}".strip()

    try:
        svg = _load_icon(name)
    except FileNotFoundError:
        return mark_safe(f'<!-- unknown lucide icon: {name} -->')

    svg = re.sub(r'<!--.*?-->\s*', '', svg, count=1, flags=re.S)
    svg = re.sub(r'\bwidth="24"', f'width="{size}"', svg, count=1)
    svg = re.sub(r'\bheight="24"', f'height="{size}"', svg, count=1)
    svg = re.sub(r'\bstroke-width="2"', f'stroke-width="{stroke_width}"', svg, count=1)
    extra = f' {cls}' if cls else ''
    svg = re.sub(r'class="lucide lucide-([\w-]+)"', rf'class="lucide lucide-\1{extra}"', svg, count=1)
    return mark_safe(svg.strip())
