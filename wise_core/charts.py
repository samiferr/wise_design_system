"""
Chart.js configuration builders for the Data Viz components.

Charts render client-side, on a `<canvas>`, via Chart.js. These functions
build the same `config` object (`type`, `data`, `options`) Chart.js expects,
ready to hand to the `chart_json` template tag:

    {% load wise_charts %}
    <canvas class="chart-canvas" style="height:220px"
            data-chart="{% chart_json revenue_chart %}"></canvas>

`wise_core/static/wise_core/js/charts.js` finds every such canvas on page
load and instantiates it. Colors are emitted as `var(--color-*)` references
rather than resolved values - canvas can't read CSS custom properties
itself, so charts.js resolves them from the page's live computed style right
before creating the chart. That keeps charts re-themed along with everything
else (see the Theming & Utilities section of the docs), with no server
round-trip.
"""
import math

# Series colors, in the order a multi-series/multi-slice chart should
# consume them. Every entry is a CSS custom property reference, so a
# palette or theme switch recolors live charts with no re-render.
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


def color_alpha(color, alpha):
    """
    A `var(--color-*)` reference with translucency baked in - for an area
    fill under a line, say, where the flat series color would be too strong.

    Canvas can resolve neither the variable nor an alpha channel on its own,
    so this just tags the string; charts.js does the actual color math once
    it has the page's live computed style.
    """
    return f'{color}@{alpha}'


def _merge(base, extra):
    """Recursively merge `extra` into `base` in place, and return it."""
    for key, value in extra.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


def _options(overrides=None):
    base = {
        'responsive': True,
        'maintainAspectRatio': False,
        'plugins': {'legend': {'display': False}},
    }
    return _merge(base, overrides or {})


def _legend(position='bottom'):
    return {
        'plugins': {
            'legend': {
                'display': True,
                'position': position,
                'labels': {'color': 'var(--color-gray-700)', 'usePointStyle': True},
            },
        },
    }


def _cartesian_scales(**overrides):
    scales = {
        'x': {'grid': {'color': 'var(--color-divider)'}, 'ticks': {'color': 'var(--color-gray-600)'}},
        'y': {
            'beginAtZero': True,
            'grid': {'color': 'var(--color-divider)'},
            'ticks': {'color': 'var(--color-gray-600)'},
        },
    }
    return _merge(scales, overrides)


def _radial_scale():
    return {
        'r': {
            'beginAtZero': True,
            'grid': {'color': 'var(--color-divider)'},
            'angleLines': {'color': 'var(--color-divider)'},
            'pointLabels': {'color': 'var(--color-gray-700)'},
            'ticks': {'display': False},
        },
    }


# ── Datasets ─────────────────────────────────────────────────────────────

def dataset(label, data, index=0, color=None, fill=False, fill_alpha=0.15, **overrides):
    """
    One Chart.js dataset: `label`/`data` plus a color from the shared series
    palette (unless `color` is given). `fill=True` also gives the dataset a
    translucent area fill in the same color - the line/radar look.
    """
    color = color or series_color(index)
    built = {
        'label': label,
        'data': data,
        'borderColor': color,
        'backgroundColor': color_alpha(color, fill_alpha) if fill else color,
        'fill': fill,
    }
    return _merge(built, overrides)


def scatter_points(pairs):
    """`[(x, y), ...]` as the `{x, y}` dicts a scatter/line dataset's `data` wants."""
    return [{'x': x, 'y': y} for x, y in pairs]


def bubble_points(triples, max_radius=18.0):
    """
    `[(x, y, size), ...]` as `{x, y, r}` dicts for a bubble dataset.

    `r` is scaled by area (the square root of the ratio to the largest
    value), not by length, so a value twice as large draws a bubble that
    *looks* twice as big instead of four times as big - Chart.js takes `r`
    as a literal pixel radius and won't do this normalization itself.
    """
    if not triples:
        return []
    top = max(t[2] for t in triples) or 1
    return [
        {'x': x, 'y': y, 'r': round(math.sqrt(max(size, 0) / top) * max_radius, 2)}
        for x, y, size in triples
    ]


# ── Chart configs ────────────────────────────────────────────────────────

def line_chart(labels, datasets, **options):
    """A line chart. `datasets` is a list built with `dataset()` (pass `fill=True` for an area chart)."""
    defaults = {
        'scales': _cartesian_scales(),
        'elements': {'line': {'tension': 0.35}, 'point': {'radius': 3}},
    }
    _merge(defaults, options)
    return {
        'type': 'line',
        'data': {'labels': labels, 'datasets': datasets},
        'options': _options(defaults),
    }


def bar_chart(labels, datasets, **options):
    """A bar chart. `datasets` is a list built with `dataset()` - several make it a grouped bar chart."""
    defaults = {'scales': _cartesian_scales()}
    _merge(defaults, options)
    return {
        'type': 'bar',
        'data': {'labels': labels, 'datasets': datasets},
        'options': _options(defaults),
    }


def _radial_chart(kind, labels, values, **options):
    defaults = _legend('right')
    _merge(defaults, options)
    return {
        'type': kind,
        'data': {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': [series_color(i) for i in range(len(values))],
                'borderColor': 'var(--color-panel)',
                'borderWidth': 1.5,
            }],
        },
        'options': _options(defaults),
    }


def pie_chart(labels, values, **options):
    """Parts of a whole. One slice per value, colored from the shared series palette."""
    return _radial_chart('pie', labels, values, **options)


def doughnut_chart(labels, values, cutout='60%', **options):
    """A pie with the middle punched out - `cutout` is how much of the radius that hole takes."""
    config = _radial_chart('doughnut', labels, values, **options)
    config['data']['datasets'][0]['cutout'] = cutout
    return config


def polar_area_chart(labels, values, **options):
    """Every slice takes an equal angle and encodes its value as radius instead."""
    config = _radial_chart('polarArea', labels, values, **options)
    config['options']['scales'] = _radial_scale()
    return config


def radar_chart(labels, datasets, **options):
    """
    A profile across several axes at once. `datasets` is a list built with
    `dataset(..., fill=True)` - one or two overlaid shapes is the practical
    limit before it stops being readable.
    """
    defaults = {'scales': _radial_scale()}
    _merge(defaults, options)
    return {
        'type': 'radar',
        'data': {'labels': labels, 'datasets': datasets},
        'options': _options(defaults),
    }


def scatter_chart(datasets, **options):
    """
    The relationship between two numeric variables. `datasets` is a list
    built with `dataset(label, scatter_points(pairs), ...)`.
    """
    defaults = {'scales': _cartesian_scales(y={'beginAtZero': False})}
    _merge(defaults, options)
    return {
        'type': 'scatter',
        'data': {'datasets': datasets},
        'options': _options(defaults),
    }


def bubble_chart(datasets, **options):
    """
    A scatter chart with a third variable encoded as point size. `datasets`
    is a list built with `dataset(label, bubble_points(triples), fill=True)`.
    """
    defaults = {'scales': _cartesian_scales(y={'beginAtZero': False})}
    _merge(defaults, options)
    return {
        'type': 'bubble',
        'data': {'datasets': datasets},
        'options': _options(defaults),
    }


def sparkline_chart(values, color=None):
    """
    A word-sized trend line with no axes, legend or tooltip - meant to sit
    inline, in a table cell or beside a number, where a full chart would be
    too much.
    """
    return {
        'type': 'line',
        'data': {
            'labels': list(range(len(values))),
            'datasets': [dataset('', values, color=color, fill=True, fill_alpha=0.12)],
        },
        'options': _options({
            'elements': {'line': {'tension': 0.35, 'borderWidth': 2}, 'point': {'radius': 0}},
            'scales': {'x': {'display': False}, 'y': {'display': False}},
            'plugins': {'tooltip': {'enabled': False}},
        }),
    }


# ── Progress ring ────────────────────────────────────────────────────────
# A single labeled value against a maximum - a Feedback primitive, not a
# chart type, so unlike the rest of this module it stays plain server-side
# SVG: no canvas, no JS, no client bundle for what is one <circle>.

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
