import re
from functools import lru_cache
from pathlib import Path

from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

# Resolved relative to this file (wise_core/templatetags/wise_icons.py), not
# settings.BASE_DIR: BASE_DIR is the *host* project's root, which is not
# necessarily wise_core's parent directory (e.g. the demo project's BASE_DIR
# is demo/, one level below the repo root where wise_core actually lives).
_ICON_DIR = Path(__file__).resolve().parent.parent / 'static' / 'wise_core' / 'icons' / 'lucide'


def _icon_dir():
    return _ICON_DIR


@lru_cache(maxsize=None)
def _load_icon(name):
    path = _icon_dir() / f'{name}.svg'
    with open(path, encoding='utf-8') as f:
        return f.read()


@register.simple_tag
def lucide(name, size=18, cls='', stroke_width='1.5', **kwargs):
    """
    Render a vendored Lucide icon inline (not <img>) so it sizes itself via
    its own width/height/viewBox and inherits color from Tailwind text-*
    utilities via currentColor.

    Usage: {% lucide "search" size=16 cls="text-gray-500" %}
    """
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
