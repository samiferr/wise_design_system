"""
Template tags over wise_core.charts, so a chart can be drawn straight from a
template when the geometry doesn't need to be prepared in the view.

    {% load wise_charts %}
    <svg viewBox="0 0 100 30" class="chart-svg">
        <polyline class="chart-series-line" points="{% chart_polyline values %}"/>
    </svg>

Prefer computing in the view when the same series feeds several elements
(a line plus its area fill, say) - these tags are for the one-liner case.
"""
from django.template import Library

from .. import charts

register = Library()


@register.simple_tag
def chart_polyline(values, width=100, height=30, padding=0):
    """A series as an SVG `points` string."""
    return charts.polyline(list(values), float(width), float(height), float(padding))


@register.simple_tag
def chart_area_path(values, width=100, height=30, padding=0):
    """The same series closed to the baseline, as a `d` path."""
    return charts.area_path(list(values), float(width), float(height), float(padding))


@register.simple_tag
def chart_percentages(values):
    """Values scaled 0-100 against the series max, for the CSS-only bar chart."""
    return charts.percentages(list(values))


@register.simple_tag
def chart_pie(values, labels=None, cx=50, cy=50, radius=45, inner_radius=0):
    return charts.pie(list(values), list(labels) if labels else None,
                      float(cx), float(cy), float(radius), float(inner_radius))


@register.simple_tag
def chart_doughnut(values, labels=None, cx=50, cy=50, radius=45, thickness=18):
    return charts.doughnut(list(values), list(labels) if labels else None,
                           float(cx), float(cy), float(radius), float(thickness))


@register.simple_tag
def chart_polar_area(values, labels=None, cx=50, cy=50, radius=45):
    return charts.polar_area(list(values), list(labels) if labels else None,
                             float(cx), float(cy), float(radius))


@register.simple_tag
def chart_radar(values, cx=50, cy=50, radius=40):
    return charts.radar(list(values), float(cx), float(cy), float(radius))


@register.simple_tag
def chart_radar_axes(count, cx=50, cy=50, radius=40):
    return charts.radar_axes(int(count), float(cx), float(cy), float(radius))


@register.simple_tag
def chart_radar_rings(count=3, cx=50, cy=50, radius=40, spokes=6):
    return charts.radar_rings(int(count), float(cx), float(cy), float(radius), int(spokes))


@register.simple_tag
def chart_scatter(pairs, width=100, height=60, padding=3):
    return charts.scatter(list(pairs), float(width), float(height), float(padding))


@register.simple_tag
def chart_bubbles(triples, width=100, height=60, padding=6, max_radius=10):
    return charts.bubbles(list(triples), float(width), float(height),
                          float(padding), float(max_radius))


@register.simple_tag
def chart_grid_lines(count=4, width=100, height=60, padding=3):
    return charts.grid_lines(int(count), float(width), float(height), float(padding))


@register.simple_tag
def chart_progress_ring(percent, radius=28, stroke=6):
    return charts.progress_ring(percent, float(radius), float(stroke))


@register.simple_tag
def chart_series_color(index):
    return charts.series_color(int(index))
