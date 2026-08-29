from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from wise_core import charts
from wise_core.mixins import (
    WiseCreateView,
    WiseDeleteView,
    WiseDetailView,
    WiseListView,
    WiseUpdateView,
)

from . import navigation
from .filters import CategoryFilter, ProductFilter
from .forms import CategoryForm, KitchenSinkForm, ProductForm
from .models import Category, Department, Product


class HomeView(TemplateView):
    template_name = 'showcase/home.html'


# ── The documentation site ────────────────────────────────────────────────
#
# Every page under /docs/ is served by the one generic view below. It resolves
# its template by convention from the section + page slug, so adding a page is
# a matter of adding an entry to navigation.DOCS_NAV and dropping the template
# in - no new view class, no new URL pattern.


def _icons_context():
    icon_dir = settings.REPO_ROOT / 'wise_core' / 'static' / 'wise_core' / 'icons' / 'lucide'
    return {'icon_names': sorted(p.stem for p in icon_dir.glob('*.svg'))}


def _kitchen_sink_context():
    """Every Forms page renders its control off this one unbound form."""
    return {'sink_form': KitchenSinkForm()}


def _tree_context():
    """Real recursive data for the Tree page, instead of a hand-written nest."""
    return {
        'departments': Department.objects.filter(parent=None).prefetch_related('children'),
    }


# One shared sample series, so every chart page is visibly plotting the same
# numbers and the reader can compare how each chart type reads them.
MONTHS = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
REVENUE = [42, 58, 35, 74, 91, 66]


def _chart_context():
    """
    Chart geometry computed in the view.

    This is the pattern the Data Viz pages recommend over the template tags:
    the same series feeds several elements (a line, its area fill, its points
    and its axis labels), so it is worth computing once.
    """
    return {
        'months': MONTHS,
        'revenue': REVENUE,
        'revenue_pairs': list(zip(MONTHS, charts.percentages(REVENUE))),
        'revenue_line': charts.polyline(REVENUE, 300, 120, padding=6),
        'revenue_area': charts.area_path(REVENUE, 300, 120, padding=6),
        'revenue_points': charts.points(REVENUE, 300, 120, padding=6),
        'grid_lines': charts.grid_lines(4, 300, 120, 6),
        'pie_slices': charts.pie(REVENUE[:4], MONTHS[:4]),
        'doughnut_slices': charts.doughnut(REVENUE[:4], MONTHS[:4]),
        'polar_slices': charts.polar_area(REVENUE, MONTHS),
        'radar_points': charts.radar(REVENUE),
        'radar_axes': charts.radar_axes(len(REVENUE)),
        'radar_rings': charts.radar_rings(3, spokes=len(REVENUE)),
        'scatter_points': charts.scatter(
            [(1, 12), (2, 30), (3, 22), (4, 48), (5, 41), (6, 66), (7, 58)], 300, 140,
        ),
        'bubble_points': charts.bubbles(
            [(1, 12, 3), (2, 30, 9), (3, 22, 5), (4, 48, 14), (5, 41, 7), (6, 66, 20)],
            300, 140, max_radius=18,
        ),
        'sparkline': charts.polyline(REVENUE, 100, 30, padding=3),
        'ring': charts.progress_ring(68),
    }


# Pages that need more than the static template. Keyed by (section, page).
_FORM_PAGES = [
    'input', 'textarea', 'number-input', 'select', 'checkbox', 'radio', 'switch',
    'rating', 'otp-input', 'file-input', 'color-picker', 'date-input', 'date-picker',
    'split-date', 'time-input', 'combobox', 'autocomplete-input', 'auto-suggest-input',
    'rich-text-input', 'form-layout',
]
_CHART_PAGES = [
    'bar-chart', 'line-chart', 'sparkline', 'pie-chart', 'doughnut-chart',
    'polar-area-chart', 'radar-chart', 'scatter-chart', 'bubble-chart',
]

EXTRA_CONTEXT = {
    ('media', 'icons'): _icons_context,
    ('navigation', 'tree'): _tree_context,
    ('feedback', 'progress-ring'): _chart_context,
    ('patterns', 'simple-data-page'): _chart_context,
}
EXTRA_CONTEXT.update({('forms', page): _kitchen_sink_context for page in _FORM_PAGES})
EXTRA_CONTEXT.update({('data-viz', page): _chart_context for page in _CHART_PAGES})


class DocPageView(TemplateView):
    """Serves one documentation page, resolved by section/page slug."""

    section_slug = None
    page_slug = None

    def get_template_names(self):
        return [f'showcase/docs/{self.section_slug}/{self.page_slug}.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_page, next_page = navigation.neighbours(self.section_slug, self.page_slug)
        context.update({
            'current_section_slug': self.section_slug,
            'current_page_slug': self.page_slug,
            'previous_page': previous_page,
            'next_page': next_page,
        })
        extra = EXTRA_CONTEXT.get((self.section_slug, self.page_slug))
        if extra is not None:
            context.update(extra())
        return context


class DocsIndexView(TemplateView):
    template_name = 'showcase/docs/index.html'


# ── Playground: the live Django CRUD demo the docs link out to ────────────

class CategoryListView(WiseListView):
    model = Category
    filterset_class = CategoryFilter
    template_name = 'showcase/category/list.html'
    paginate_by = 10


class CategoryDetailView(WiseDetailView):
    model = Category
    template_name = 'showcase/category/detail.html'


class CategoryCreateView(WiseCreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'showcase/category/form.html'
    success_url = reverse_lazy('category_list_view')
    success_message = 'Category "%(name)s" created.'


class CategoryUpdateView(WiseUpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'showcase/category/form.html'
    success_message = 'Category "%(name)s" updated.'

    def get_success_url(self):
        return reverse_lazy('category_detail_view', args=[self.object.pk])


class CategoryDeleteView(WiseDeleteView):
    model = Category
    template_name = 'showcase/category/confirm_delete.html'
    success_url = reverse_lazy('category_list_view')
    success_message = 'Category deleted.'


class ProductListView(WiseListView):
    model = Product
    filterset_class = ProductFilter
    template_name = 'showcase/product/list.html'
    paginate_by = 10


class ProductDetailView(WiseDetailView):
    model = Product
    template_name = 'showcase/product/detail.html'


class ProductCreateView(WiseCreateView):
    model = Product
    form_class = ProductForm
    template_name = 'showcase/product/form.html'
    success_url = reverse_lazy('product_list_view')
    success_message = 'Product "%(name)s" created.'


class ProductUpdateView(WiseUpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'showcase/product/form.html'
    success_message = 'Product "%(name)s" updated.'

    def get_success_url(self):
        return reverse_lazy('product_detail_view', args=[self.object.pk])


class ProductDeleteView(WiseDeleteView):
    model = Product
    template_name = 'showcase/product/confirm_delete.html'
    success_url = reverse_lazy('product_list_view')
    success_message = 'Product deleted.'
