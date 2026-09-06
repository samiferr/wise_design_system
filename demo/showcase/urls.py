from django.urls import include, path

from . import api, navigation, views

# One route per entry in the documentation tree. Expanding DOCS_NAV here (rather
# than listing ~70 paths by hand) keeps the site's structure defined in exactly
# one place - see navigation.py.
docs_urlpatterns = [
    path(
        f"{page['section_slug']}/{page['slug']}/",
        views.DocPageView.as_view(
            section_slug=page['section_slug'],
            page_slug=page['slug'],
        ),
        name=page['url_name'],
    )
    for page in navigation.flat_pages()
]

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('docs/', views.DocsIndexView.as_view(), name='docs'),
    path('docs/', include(docs_urlpatterns)),

    # The demo app: a small, real Django CRUD app built entirely from this
    # design system, kept under its own /demo/ prefix and its own chrome
    # (showcase/context_processors.site_chrome, WISE_NAV_SECTIONS in
    # settings.py) so it reads as a separate product from the docs site
    # above, not a page mixed into it.
    path('demo/', views.DemoIndexView.as_view(), name='demo'),

    path('demo/categories/', views.CategoryListView.as_view(), name='category_list_view'),
    path('demo/categories/create/', views.CategoryCreateView.as_view(), name='category_create_view'),
    path('demo/categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail_view'),
    path('demo/categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update_view'),
    path('demo/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete_view'),

    # A category's children, nested under it. The parent's pk in the URL is
    # what scopes the queryset and lets the pages share one tab bar - see
    # views.CATEGORY_TABS.
    path('demo/categories/<int:parent_pk>/products/',
         views.CategoryProductListView.as_view(), name='category_product_list_view'),
    path('demo/categories/<int:parent_pk>/products/create/',
         views.CategoryProductCreateView.as_view(), name='category_product_create_view'),

    path('demo/products/', views.ProductListView.as_view(), name='product_list_view'),
    path('demo/products/create/', views.ProductCreateView.as_view(), name='product_create_view'),
    path('demo/products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail_view'),
    path('demo/products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update_view'),
    path('demo/products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete_view'),

    # A product has two child models, which is why its page is tabbed
    # (views.PRODUCT_TABS). Each child gets the full five routes under the
    # product it belongs to.
    path('demo/products/<int:parent_pk>/variants/',
         views.ProductVariantListView.as_view(), name='product_variant_list_view'),
    path('demo/products/<int:parent_pk>/variants/create/',
         views.ProductVariantCreateView.as_view(), name='product_variant_create_view'),
    path('demo/products/<int:parent_pk>/variants/<int:pk>/',
         views.ProductVariantDetailView.as_view(), name='product_variant_detail_view'),
    path('demo/products/<int:parent_pk>/variants/<int:pk>/update/',
         views.ProductVariantUpdateView.as_view(), name='product_variant_update_view'),
    path('demo/products/<int:parent_pk>/variants/<int:pk>/delete/',
         views.ProductVariantDeleteView.as_view(), name='product_variant_delete_view'),

    path('demo/products/<int:parent_pk>/reviews/',
         views.ProductReviewListView.as_view(), name='product_review_list_view'),
    path('demo/products/<int:parent_pk>/reviews/create/',
         views.ProductReviewCreateView.as_view(), name='product_review_create_view'),
    path('demo/products/<int:parent_pk>/reviews/<int:pk>/',
         views.ProductReviewDetailView.as_view(), name='product_review_detail_view'),
    path('demo/products/<int:parent_pk>/reviews/<int:pk>/update/',
         views.ProductReviewUpdateView.as_view(), name='product_review_update_view'),
    path('demo/products/<int:parent_pk>/reviews/<int:pk>/delete/',
         views.ProductReviewDeleteView.as_view(), name='product_review_delete_view'),

    path('api/', include(api.router.urls)),
]
