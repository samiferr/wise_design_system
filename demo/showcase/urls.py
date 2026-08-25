from django.urls import include, path

from . import api, views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('tokens/', views.TokensView.as_view(), name='tokens'),
    path('components/', views.ComponentsView.as_view(), name='components'),
    path('icons/', views.IconsView.as_view(), name='icons'),

    path('categories/', views.CategoryListView.as_view(), name='category_list_view'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create_view'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail_view'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update_view'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete_view'),

    path('products/', views.ProductListView.as_view(), name='product_list_view'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create_view'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail_view'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update_view'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete_view'),

    path('api/', include(api.router.urls)),
]
