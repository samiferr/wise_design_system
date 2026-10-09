import django_filters
from django import forms
from django.db.models import Q

from .models import Category, Product, ProductReview, ProductVariant


# `q` is the list's free-text search box (wise_core/components/_search_bar.html):
# a hidden filter, so it stays out of the filter drawer's fields and the
# applied-filter count, wired to a method that ORs the columns worth searching.
class CategoryFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='search', label='Search', widget=forms.HiddenInput())
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')

    class Meta:
        model = Category
        fields = ['name']

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))


class ProductFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='search', label='Search', widget=forms.HiddenInput())
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Category')

    class Meta:
        model = Product
        fields = ['name', 'category']

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(category__name__icontains=value))


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
