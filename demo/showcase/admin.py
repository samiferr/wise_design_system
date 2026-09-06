from django.contrib import admin

from .models import Category, Product, ProductReview, ProductVariant

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductReview)
