from django.contrib import admin

from .models import Category, Product, ProductImage, ProductReview, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]


admin.site.register(Category)
admin.site.register(ProductVariant)
admin.site.register(ProductReview)
