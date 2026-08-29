"""
QR code and barcode template tags.

Both delegate to a small, pure-Python third-party library rather than
reimplementing the encodings here - QR in particular is a spec big enough that
a hand-rolled encoder would be a liability, not a feature. Neither library is a
hard dependency of wise_core: the tags degrade to an HTML comment explaining
what to install, so a project that never renders a code never has to install
anything.

    pip install segno           # {% qr_code %}
    pip install python-barcode  # {% barcode %}
"""
import io
import re

from django.template import Library
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = Library()

try:  # pragma: no cover - exercised by whether the extra is installed
    import segno
except ImportError:
    segno = None

try:  # pragma: no cover
    import barcode as python_barcode
    from barcode.writer import SVGWriter
except ImportError:
    python_barcode = None


def _missing(package, tag):
    return mark_safe(
        f'<!-- wise_core: {{% {tag} %}} needs the "{package}" package '
        f'(pip install {package}) -->'
    )


@register.simple_tag
def qr_code(data, scale=4, border=2, dark='currentColor'):
    """
    Render `data` as an inline SVG QR code.

    Defaults to `currentColor` for the dark modules, so the code inherits the
    surrounding text color and stays legible when the theme flips - a QR code
    hardcoded to black disappears on a dark panel.

    Usage::

        {% load wise_codes %}
        <div class="qr-code">{% qr_code product.get_absolute_url scale=4 %}</div>
    """
    if segno is None:
        return _missing('segno', 'qr_code')

    # segno validates `dark` as a real color and rejects CSS keywords, so the
    # code is generated in black and the stroke swapped afterwards. That is
    # also why `dark` is substituted rather than interpolated into the call.
    svg = segno.make(str(data), micro=False).svg_inline(
        scale=scale, border=border, dark='#000',
    )
    return mark_safe(svg.replace('stroke="#000"', f'stroke="{escape(dark)}"'))


@register.simple_tag
def barcode(data, symbology='code128', write_text=True):
    """
    Render `data` as an inline SVG barcode (Code 128 by default).

    python-barcode emits a full standalone SVG document; the XML declaration
    and DOCTYPE are stripped here so the result can be embedded inline in an
    HTML page.
    """
    if python_barcode is None:
        return _missing('python-barcode', 'barcode')

    buffer = io.BytesIO()
    python_barcode.get(symbology, str(data), writer=SVGWriter()).write(
        buffer, options={'write_text': bool(write_text)},
    )
    svg = buffer.getvalue().decode('utf-8')
    # Strip the XML prolog/DOCTYPE - valid for a standalone file, invalid
    # inside an HTML body.
    svg = re.sub(r'<\?xml.*?\?>', '', svg, flags=re.S)
    svg = re.sub(r'<!DOCTYPE.*?>', '', svg, flags=re.S)
    return mark_safe(svg.strip())


@register.simple_tag
def qr_code_available():
    """True when `segno` is importable - lets a template offer a fallback."""
    return segno is not None


@register.simple_tag
def barcode_available():
    """True when `python-barcode` is importable."""
    return python_barcode is not None
