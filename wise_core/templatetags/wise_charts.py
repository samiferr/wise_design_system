"""
Template tags over wise_core.charts.

    {% load wise_charts %}
    <canvas class="chart-canvas" style="height:220px"
            data-chart="{% chart_json revenue_chart %}"></canvas>

`revenue_chart` is a Chart.js config dict, usually built in the view with
`wise_core.charts.line_chart()` and friends - see the Data Viz docs.
"""
import json

from django.template import Library
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .. import charts

register = Library()


@register.simple_tag
def chart_json(config):
    """A Chart.js config dict as JSON, HTML-escaped for a `data-chart` attribute."""
    return mark_safe(escape(json.dumps(config)))


@register.simple_tag
def chart_progress_ring(percent, radius=28, stroke=6):
    return charts.progress_ring(percent, float(radius), float(stroke))
