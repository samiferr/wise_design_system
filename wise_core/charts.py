"""
Server-side SVG geometry for the Data Viz components.

The design system deliberately ships no charting library: a chart here is
ordinary SVG in an ordinary Django template, with the geometry computed up
front by the functions below. That keeps charts inside the same
render-once-on-the-server model as the rest of the system - they work with
JavaScript disabled, they print, and they need no client bundle.

Everything returns plain floats/strings/dicts ready to drop into an SVG
attribute. Colors are emitted as `var(--color-*)` references rather than hex
literals so that charts re-theme along with everything else (see the
Theming & Utilities section of the docs).

Coordinates follow SVG convention: y grows *downward*, so a larger data value
produces a smaller y.
"""
import math

# Series colors, in the order a multi-series chart should consume them. Every
# entry is a CSS custom property reference, so a palette or theme switch
# recolors live charts with no re-render.
SERIES_COLORS = [
    'var(--color-action-600)',
    'var(--color-brand-400)',
    'var(--color-warning-400)',
    'var(--color-accent-400)',
    'var(--color-brand-800)',
    'var(--color-gray-500)',
]


def series_color(index):
    """The series color at `index`, wrapping if there are more series than colors."""
    return SERIES_COLORS[index % len(SERIES_COLORS)]


def _bounds(values, minimum=None, maximum=None):
    """
    Resolve the value range to plot over, guarding the degenerate cases.

    A flat series (every value identical) would otherwise give a zero span and
    divide-by-zero; it gets a span of 1 so it renders as a straight line
    through the middle rather than blowing up.
    """
    lo = minimum if minimum is not None else min(values)
    hi = maximum if maximum is not None else max(values)
    if hi == lo:
        hi = lo + 1
    return lo, hi


def normalize(values, minimum=None, maximum=None):
    """Scale `values` to 0..1 against their own range (or an explicit one)."""
    lo, hi = _bounds(values, minimum, maximum)
    return [(v - lo) / (hi - lo) for v in values]


def percentages(values):
    """
    Scale `values` to 0..100 against the series maximum.

    This is what the CSS-only `.bar-chart` wants for its `--value`, where each
    bar's height is a percentage of the tallest.
    """
    if not values:
        return []
    top = max(values)
    if top <= 0:
        return [0.0 for _ in values]
    return [round(v / top * 100, 2) for v in values]


# ── Cartesian charts (line, area, sparkline, scatter, bubble) ──────────────

def points(values, width=100.0, height=30.0, padding=0.0, minimum=None, maximum=None):
    """
    Evenly-spaced (x, y) pairs for a series, as a list of tuples.

    `padding` insets the plot on the y axis so a stroked line's cap isn't
    clipped at the very top or bottom of the viewBox.
    """
    if not values:
        return []
    if len(values) == 1:
        return [(width / 2, height / 2)]

    inner = height - 2 * padding
    step = width / (len(values) - 1)
    scaled = normalize(values, minimum, maximum)
    return [
        (i * step, padding + (1 - t) * inner)
        for i, t in enumerate(scaled)
    ]


def polyline(values, width=100.0, height=30.0, padding=0.0, minimum=None, maximum=None):
    """
    A series as an SVG `points` attribute string: ``"0,24 16,20 33,22 ..."``.

    Drop straight into ``<polyline points="{{ ... }}">`` - this is the
    sparkline and line-chart workhorse.
    """
    return ' '.join(
        f'{x:.2f},{y:.2f}'
        for x, y in points(values, width, height, padding, minimum, maximum)
    )


def area_path(values, width=100.0, height=30.0, padding=0.0, minimum=None, maximum=None):
    """
    The same series closed down to the baseline, as a `d` path.

    Used for the tinted fill under a line chart; pair it with `polyline` for
    the stroke on top.
    """
    pts = points(values, width, height, padding, minimum, maximum)
    if not pts:
        return ''
    head = f'M {pts[0][0]:.2f} {pts[0][1]:.2f}'
    body = ' '.join(f'L {x:.2f} {y:.2f}' for x, y in pts[1:])
    return f'{head} {body} L {pts[-1][0]:.2f} {height:.2f} L {pts[0][0]:.2f} {height:.2f} Z'


def scatter(pairs, width=100.0, height=60.0, padding=3.0):
    """
    Map raw ``(x, y)`` data onto the viewBox, returning dicts with `cx`/`cy`.

    Both axes are scaled independently to their own range, so the cloud fills
    the plot regardless of the units involved.
    """
    if not pairs:
        return []
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    x_lo, x_hi = _bounds(xs)
    y_lo, y_hi = _bounds(ys)
    inner_w = width - 2 * padding
    inner_h = height - 2 * padding
    return [
        {
            'cx': round(padding + (x - x_lo) / (x_hi - x_lo) * inner_w, 2),
            'cy': round(padding + (1 - (y - y_lo) / (y_hi - y_lo)) * inner_h, 2),
        }
        for x, y in pairs
    ]


def bubbles(triples, width=100.0, height=60.0, padding=6.0, max_radius=10.0):
    """
    Like `scatter`, but each item is ``(x, y, size)`` and carries a radius.

    Radius is scaled by area rather than by length (``sqrt`` of the ratio), so
    a value twice as large draws a bubble that *looks* twice as big instead of
    four times as big.
    """
    if not triples:
        return []
    sized = scatter([(t[0], t[1]) for t in triples], width, height, padding)
    sizes = [t[2] for t in triples]
    top = max(sizes) or 1
    for item, size in zip(sized, sizes):
        item['r'] = round(math.sqrt(max(size, 0) / top) * max_radius, 2)
    return sized


def grid_lines(count=4, width=100.0, height=60.0, padding=3.0):
    """Horizontal gridline y positions, evenly spread across the plot area."""
    inner = height - 2 * padding
    return [round(padding + inner * i / count, 2) for i in range(count + 1)]


# ── Radial charts (pie, doughnut, polar area) ──────────────────────────────

def _polar(cx, cy, radius, angle_deg):
    """Point on a circle. Angles start at 12 o'clock and run clockwise."""
    rad = math.radians(angle_deg - 90)
    return cx + radius * math.cos(rad), cy + radius * math.sin(rad)


def _arc_path(cx, cy, radius, start_deg, end_deg, inner_radius=0.0):
    """
    One wedge (or ring segment when `inner_radius` > 0) as an SVG `d`.

    A slice covering the full circle can't be drawn as a single arc - start and
    end land on the same point and the browser renders nothing - so a
    full-circle slice is emitted as two half arcs instead.
    """
    sweep = end_deg - start_deg
    if sweep >= 359.999:
        # Two stacked half-circles; works for both the disc and the ring case.
        mid = start_deg + 180
        return ' '.join([
            _arc_path(cx, cy, radius, start_deg, mid, inner_radius),
            _arc_path(cx, cy, radius, mid, end_deg, inner_radius),
        ])

    large = 1 if sweep > 180 else 0
    x1, y1 = _polar(cx, cy, radius, start_deg)
    x2, y2 = _polar(cx, cy, radius, end_deg)

    if inner_radius <= 0:
        return (
            f'M {cx:.2f} {cy:.2f} L {x1:.2f} {y1:.2f} '
            f'A {radius:.2f} {radius:.2f} 0 {large} 1 {x2:.2f} {y2:.2f} Z'
        )

    ix1, iy1 = _polar(cx, cy, inner_radius, end_deg)
    ix2, iy2 = _polar(cx, cy, inner_radius, start_deg)
    return (
        f'M {x1:.2f} {y1:.2f} '
        f'A {radius:.2f} {radius:.2f} 0 {large} 1 {x2:.2f} {y2:.2f} '
        f'L {ix1:.2f} {iy1:.2f} '
        f'A {inner_radius:.2f} {inner_radius:.2f} 0 {large} 0 {ix2:.2f} {iy2:.2f} Z'
    )


def pie(values, labels=None, cx=50.0, cy=50.0, radius=45.0, inner_radius=0.0):
    """
    Pie (or doughnut, with `inner_radius`) slices.

    Returns one dict per slice with `path`, `color`, `label`, `value` and
    `percent` - everything a template needs to draw the wedge and its legend
    entry in one pass.
    """
    total = sum(v for v in values if v > 0)
    if total <= 0:
        return []

    slices = []
    angle = 0.0
    for i, value in enumerate(values):
        if value <= 0:
            continue
        sweep = value / total * 360
        slices.append({
            'path': _arc_path(cx, cy, radius, angle, angle + sweep, inner_radius),
            'color': series_color(i),
            'label': labels[i] if labels and i < len(labels) else '',
            'value': value,
            'percent': round(value / total * 100, 1),
        })
        angle += sweep
    return slices


def doughnut(values, labels=None, cx=50.0, cy=50.0, radius=45.0, thickness=18.0):
    """Convenience wrapper: a pie with the middle punched out."""
    return pie(values, labels, cx, cy, radius, inner_radius=max(radius - thickness, 0))


def polar_area(values, labels=None, cx=50.0, cy=50.0, radius=45.0):
    """
    Polar area chart: every slice takes an equal angle, and encodes its value
    as radius instead. Radius is scaled by area (``sqrt``) for the same reason
    bubbles are - so the eye reads the proportion correctly.
    """
    if not values:
        return []
    top = max(values) or 1
    sweep = 360 / len(values)
    return [
        {
            'path': _arc_path(cx, cy, math.sqrt(max(v, 0) / top) * radius,
                              i * sweep, (i + 1) * sweep),
            'color': series_color(i),
            'label': labels[i] if labels and i < len(labels) else '',
            'value': v,
        }
        for i, v in enumerate(values)
    ]


def radar(values, cx=50.0, cy=50.0, radius=40.0, minimum=0, maximum=None):
    """
    Radar/spider polygon as an SVG `points` string.

    Defaults to a zero baseline (rather than the series minimum) because a
    radar chart is read as "how full is each spoke" - anchoring to the
    smallest value would make the weakest axis look empty at any scale.
    """
    if not values:
        return ''
    scaled = normalize(values, minimum, maximum)
    step = 360 / len(values)
    return ' '.join(
        '{:.2f},{:.2f}'.format(*_polar(cx, cy, t * radius, i * step))
        for i, t in enumerate(scaled)
    )


def radar_axes(count, cx=50.0, cy=50.0, radius=40.0):
    """Spoke end points for a radar chart's axis lines and labels."""
    step = 360 / count
    out = []
    for i in range(count):
        x, y = _polar(cx, cy, radius, i * step)
        lx, ly = _polar(cx, cy, radius + 7, i * step)
        out.append({'x': round(x, 2), 'y': round(y, 2),
                    'label_x': round(lx, 2), 'label_y': round(ly, 2)})
    return out


def radar_rings(count=3, cx=50.0, cy=50.0, radius=40.0, spokes=6):
    """Concentric guide polygons behind a radar chart."""
    rings = []
    step = 360 / spokes
    for r in range(1, count + 1):
        ring_radius = radius * r / count
        rings.append(' '.join(
            '{:.2f},{:.2f}'.format(*_polar(cx, cy, ring_radius, i * step))
            for i in range(spokes)
        ))
    return rings


# ── Progress ring ──────────────────────────────────────────────────────────

def progress_ring(percent, radius=28.0, stroke=6.0):
    """
    Geometry for `.progress-ring`.

    An SVG circle is stroked from its 3 o'clock position, so the CSS rotates it
    -90deg to start at the top; `dasharray`/`dashoffset` then reveal exactly
    `percent` of the circumference.
    """
    percent = max(0.0, min(100.0, float(percent)))
    circumference = 2 * math.pi * radius
    return {
        'radius': radius,
        'stroke': stroke,
        'size': round((radius + stroke) * 2, 2),
        'center': round(radius + stroke, 2),
        'dasharray': round(circumference, 2),
        'dashoffset': round(circumference * (1 - percent / 100), 2),
        'percent': round(percent, 1),
    }
