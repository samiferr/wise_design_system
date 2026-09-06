import django_filters

from .models import Category, Product, ProductReview, ProductVariant


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')

    class Meta:
        model = Category
        fields = ['name']


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Category')

    class Meta:
        model = Product
        fields = ['name', 'category']


# Child lists get their own small filtersets rather than django-filter's
# `filterset_fields = "__all__"` default: a child list is already scoped to
# one parent, so the only filter worth offering is a search over the one
# column a visitor scans.
class ProductVariantFilter(django_filters.FilterSet):
    label = django_filters.CharFilter(lookup_expr='icontains', label='Label')

    class Meta:
        model = ProductVariant
        fields = ['label']


class ProductReviewFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(lookup_expr='icontains', label='Author')

    class Meta:
        model = ProductReview
        fields = ['author']
