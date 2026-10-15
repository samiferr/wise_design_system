from django import forms
from django.contrib import admin

from .forms import product_specs_field
from .models import Category, Product, ProductImage, ProductReview, ProductVariant


class ProductAdminForm(forms.ModelForm):
    """The admin edits `specs` with the same PropertiesField as the demo app."""

    specs = product_specs_field()

    class Meta:
        model = Product
        fields = '__all__'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductImageInline]


admin.site.register(Category)
admin.site.register(ProductVariant)
admin.site.register(ProductReview)
