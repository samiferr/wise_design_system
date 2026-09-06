from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from wise_core import charts
from wise_core.mixins import (
    ChildTab,
    WiseCreateView,
    WiseDeleteView,
    WiseDetailView,
    WiseListView,
    WiseParentDetailChildCreateView,
    WiseParentDetailChildDeleteView,
    WiseParentDetailChildDetailView,
    WiseParentDetailChildListView,
    WiseParentDetailChildUpdateView,
    WiseParentDetailView,
    WiseUpdateView,
)

from . import navigation
from .filters import (
    CategoryFilter,
    ProductFilter,
    ProductReviewFilter,
    ProductVariantFilter,
)
from .forms import (
    CategoryForm,
    CategoryProductForm,
    KitchenSinkForm,
    ProductForm,
    ProductReviewForm,
    ProductVariantForm,
)
from .models import Category, Department, Product, ProductReview, ProductVariant


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
STOCK_TREND = [96, 80, 84, 64, 56, 48]
PRICE_VS_UNITS = [(1, 12), (2, 30), (3, 22), (4, 48), (5, 41), (6, 66), (7, 58)]
PRICE_VS_UNITS_BY_REVENUE = [(1, 12, 3), (2, 30, 9), (3, 22, 5), (4, 48, 14), (5, 41, 7), (6, 66, 20)]


def _chart_context():
    """
    Chart.js configs computed in the view.

    This is the pattern the Data Viz pages recommend over building a config
    inline in the template: the config is one plain dict, easiest to shape
    where the rest of the page's data already lives.
    """
    return {
        'months': MONTHS,
        'revenue': REVENUE,
        'revenue_bar': charts.bar_chart(MONTHS, [charts.dataset('Revenue', REVENUE)]),
        'revenue_bar_warning': charts.bar_chart(
            MONTHS, [charts.dataset('Revenue', REVENUE, color='var(--color-warning-400)')],
        ),
        'revenue_line': charts.line_chart(MONTHS, [charts.dataset('Revenue', REVENUE, fill=True)]),
        'revenue_sparkline': charts.sparkline_chart(REVENUE),
        'orders_sparkline': charts.sparkline_chart(REVENUE, color='var(--color-warning-400)'),
        'stock_sparkline': charts.sparkline_chart(STOCK_TREND, color='var(--color-accent-500)'),
        'revenue_pie': charts.pie_chart(MONTHS[:4], REVENUE[:4]),
        'revenue_doughnut': charts.doughnut_chart(MONTHS[:4], REVENUE[:4]),
        'revenue_total': sum(REVENUE[:4]),
        'revenue_polar': charts.polar_area_chart(MONTHS, REVENUE),
        'revenue_radar': charts.radar_chart(MONTHS, [charts.dataset('Revenue', REVENUE, fill=True)]),
        'price_scatter': charts.scatter_chart(
            [charts.dataset('Price vs units sold', charts.scatter_points(PRICE_VS_UNITS))],
        ),
        'price_bubble': charts.bubble_chart(
            [charts.dataset(
                'Price vs units, sized by revenue',
                charts.bubble_points(PRICE_VS_UNITS_BY_REVENUE, max_radius=18),
                fill=True, fill_alpha=0.55,
            )],
        ),
        'ring': charts.progress_ring(68),
    }


def _parent_child_context():
    """
    The Patterns -> Tabbed Parent / Child page previews the *real* tab bar
    component against real data, rather than a hand-written copy of its
    markup that could drift from it. PRODUCT_TABS is the demo app's own tab
    list, defined further down this module; this function runs per request,
    so the forward reference resolves fine.
    """
    product = Product.objects.prefetch_related('variants', 'reviews').first()
    if product is None:  # an unseeded database - the page skips the preview
        return {}
    return {
        'demo_product': product,
        'child_tabs': [
            {
                'label': tab.label,
                'url': tab.get_url(product),
                'icon': tab.icon,
                'count': tab.get_count(product),
                'selected': index == 1,
            }
            for index, tab in enumerate(PRODUCT_TABS)
        ],
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
    ('patterns', 'parent-child-crud'): _parent_child_context,
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


# ── The demo app: a live Django CRUD app the docs link out to ─────────────
# Kept under its own /demo/ prefix and chrome (see urls.py and
# showcase/context_processors.site_chrome) so it reads as its own product
# rather than a page mixed into the documentation site above.

class DemoIndexView(TemplateView):
    template_name = 'showcase/demo/index.html'


class CategoryListView(WiseListView):
    model = Category
    filterset_class = CategoryFilter
    template_name = 'showcase/category/list.html'
    paginate_by = 10
    sortable_fields = {'name'}


# ── Tabbed parent pages ───────────────────────────────────────────────────
#
# A record with children of its own is a tabbed page, not one long scroll:
# the parent's overview is the first tab and each child model gets its own,
# because a parent usually has more than one (a product has variants *and*
# reviews, the way a patient has payments, prescriptions and appointments).
#
# The bar is declared once, in Python, and handed to the parent's detail
# view and to every child view underneath it, so all of them render the
# identical tabs - permissions checked, URLs reversed against the parent,
# counts read off its related managers. See wise_core.mixins.ChildTab.

CATEGORY_TABS = [
    ChildTab.overview('Overview', 'category_detail_view', icon='info'),
    ChildTab('Products', 'category_product_list_view', model=Product, icon='pill', count='products'),
]

PRODUCT_TABS = [
    ChildTab.overview('Overview', 'product_detail_view', icon='info'),
    ChildTab('Variants', 'product_variant_list_view', model=ProductVariant, icon='tag', count='variants'),
    ChildTab('Reviews', 'product_review_list_view', model=ProductReview, icon='star', count='reviews'),
]


class CategoryDetailView(WiseParentDetailView):
    model = Category
    child_tabs = CATEGORY_TABS
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
    sortable_fields = {'name', 'category__name', 'rating'}


class ProductDetailView(WiseParentDetailView):
    model = Product
    child_tabs = PRODUCT_TABS
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


# ── The children ──────────────────────────────────────────────────────────
#
# Every one of these is scoped to its parent by the URL: /demo/products/3/
# variants/ can only ever read or write variants of product 3, so guessing
# another product's variant id gets a 404 rather than someone else's record.
#
# `child_list_url_name` is the tab the view lives in: the create/update/
# delete views redirect there after saving, and the generic templates point
# their back link and Cancel button at it.

class CategoryProductListView(WiseParentDetailChildListView):
    """A category's products. Each row links on to that product's own tabbed
    page - a child can be a parent in its own right."""
    model = Product
    parent_model = Category
    parent_field = 'category_id'
    child_tabs = CATEGORY_TABS
    filterset_class = ProductFilter
    template_name = 'showcase/category/product_list.html'
    paginate_by = 10
    sortable_fields = {'name', 'rating'}
    ordering = ['name']


class CategoryProductCreateView(WiseParentDetailChildCreateView):
    model = Product
    parent_model = Category
    parent_field = 'category_id'
    child_tabs = CATEGORY_TABS
    child_list_url_name = 'category_product_list_view'
    # CategoryProductForm is ProductForm without the category field: the
    # parent comes from the URL, so it cannot be reassigned by posting a
    # different value.
    form_class = CategoryProductForm
    template_name = 'showcase/category/product_form.html'
    success_message = 'Product "%(name)s" created.'


class ProductVariantListView(WiseParentDetailChildListView):
    model = ProductVariant
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    filterset_class = ProductVariantFilter
    template_name = 'showcase/product/variant/list.html'
    paginate_by = 10
    sortable_fields = {'label', 'sku', 'price', 'stock'}
    ordering = ['label']


class ProductVariantDetailView(WiseParentDetailChildDetailView):
    model = ProductVariant
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_variant_list_view'
    template_name = 'showcase/product/variant/detail.html'


class ProductVariantCreateView(WiseParentDetailChildCreateView):
    model = ProductVariant
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_variant_list_view'
    form_class = ProductVariantForm
    template_name = 'showcase/product/variant/form.html'
    success_message = 'Variant "%(label)s" added.'


class ProductVariantUpdateView(WiseParentDetailChildUpdateView):
    model = ProductVariant
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_variant_list_view'
    form_class = ProductVariantForm
    template_name = 'showcase/product/variant/form.html'
    success_message = 'Variant "%(label)s" updated.'


class ProductVariantDeleteView(WiseParentDetailChildDeleteView):
    model = ProductVariant
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_variant_list_view'
    template_name = 'showcase/product/variant/confirm_delete.html'
    success_message = 'Variant deleted.'


class ProductReviewListView(WiseParentDetailChildListView):
    model = ProductReview
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    filterset_class = ProductReviewFilter
    template_name = 'showcase/product/review/list.html'
    paginate_by = 10
    sortable_fields = {'author', 'rating', 'submitted_on'}
    ordering = ['-submitted_on', '-pk']


class ProductReviewDetailView(WiseParentDetailChildDetailView):
    model = ProductReview
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_review_list_view'
    template_name = 'showcase/product/review/detail.html'


class ProductReviewCreateView(WiseParentDetailChildCreateView):
    model = ProductReview
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_review_list_view'
    form_class = ProductReviewForm
    template_name = 'showcase/product/review/form.html'
    success_message = 'Review by %(author)s added.'


class ProductReviewUpdateView(WiseParentDetailChildUpdateView):
    model = ProductReview
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_review_list_view'
    form_class = ProductReviewForm
    template_name = 'showcase/product/review/form.html'
    success_message = 'Review by %(author)s updated.'


class ProductReviewDeleteView(WiseParentDetailChildDeleteView):
    model = ProductReview
    parent_model = Product
    parent_field = 'product_id'
    child_tabs = PRODUCT_TABS
    child_list_url_name = 'product_review_list_view'
    template_name = 'showcase/product/review/confirm_delete.html'
    success_message = 'Review deleted.'
