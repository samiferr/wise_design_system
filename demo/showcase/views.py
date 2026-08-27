from django.urls import reverse_lazy
from django.views.generic import TemplateView

from wise_core.mixins import (
    WiseCreateView,
    WiseDeleteView,
    WiseDetailView,
    WiseListView,
    WiseUpdateView,
)

from .filters import CategoryFilter, ProductFilter
from .forms import CategoryForm, ProductForm
from .models import Category, Product


class HomeView(TemplateView):
    template_name = 'showcase/home.html'


class TokensView(TemplateView):
    template_name = 'showcase/tokens.html'


class ComponentsView(TemplateView):
    template_name = 'showcase/components.html'


class ButtonsComponentView(TemplateView):
    template_name = 'showcase/components/buttons.html'


class BadgesComponentView(TemplateView):
    template_name = 'showcase/components/badges.html'


class InputsComponentView(TemplateView):
    template_name = 'showcase/components/inputs.html'


class CardsComponentView(TemplateView):
    template_name = 'showcase/components/cards.html'


class TabsComponentView(TemplateView):
    template_name = 'showcase/components/tabs.html'


class FormsComponentView(TemplateView):
    template_name = 'showcase/components/forms.html'


class TopbarComponentView(TemplateView):
    template_name = 'showcase/components/topbar.html'


class SidebarComponentView(TemplateView):
    template_name = 'showcase/components/sidebar.html'


class DataTableComponentView(TemplateView):
    template_name = 'showcase/components/data-table.html'


class PaginationComponentView(TemplateView):
    template_name = 'showcase/components/pagination.html'


class FilterPanelComponentView(TemplateView):
    template_name = 'showcase/components/filter-panel.html'


class FlashMessagesComponentView(TemplateView):
    template_name = 'showcase/components/flash-messages.html'


class CalendarComponentView(TemplateView):
    template_name = 'showcase/components/calendar.html'


class ChartsComponentView(TemplateView):
    template_name = 'showcase/components/charts.html'


class IconsView(TemplateView):
    template_name = 'showcase/icons.html'

    def get_context_data(self, **kwargs):
        from django.conf import settings
        icon_dir = settings.BASE_DIR.parent / 'wise_core' / 'static' / 'wise_core' / 'icons' / 'lucide'
        context = super().get_context_data(**kwargs)
        context['icon_names'] = sorted(p.stem for p in icon_dir.glob('*.svg'))
        return context


# ── Categories: the "datatable" (WiseListView + django-filter) + full CRUD ──

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


# ── Products: demonstrates AutocompleteInputWidget + RichTextInputWidget ──

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
