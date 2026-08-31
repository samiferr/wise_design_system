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

    path('demo/products/', views.ProductListView.as_view(), name='product_list_view'),
    path('demo/products/create/', views.ProductCreateView.as_view(), name='product_create_view'),
    path('demo/products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail_view'),
    path('demo/products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update_view'),
    path('demo/products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete_view'),

    path('api/', include(api.router.urls)),
]
