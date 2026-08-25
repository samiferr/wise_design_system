import django_filters

from .models import Category, Product


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
