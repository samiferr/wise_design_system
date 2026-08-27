from django.urls import include, path

from . import api, views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('tokens/', views.TokensView.as_view(), name='tokens'),
    path('components/', views.ComponentsView.as_view(), name='components'),
    # Basic
    path('components/buttons/', views.ButtonsComponentView.as_view(), name='component_buttons'),
    path('components/badges/', views.BadgesComponentView.as_view(), name='component_badges'),
    path('components/inputs/', views.InputsComponentView.as_view(), name='component_inputs'),
    path('components/cards/', views.CardsComponentView.as_view(), name='component_cards'),
    # Compound
    path('components/tabs/', views.TabsComponentView.as_view(), name='component_tabs'),
    path('components/forms/', views.FormsComponentView.as_view(), name='component_forms'),
    path('components/topbar/', views.TopbarComponentView.as_view(), name='component_topbar'),
    path('components/sidebar/', views.SidebarComponentView.as_view(), name='component_sidebar'),
    path('components/pagination/', views.PaginationComponentView.as_view(), name='component_pagination'),
    path('components/filter-panel/', views.FilterPanelComponentView.as_view(), name='component_filter_panel'),
    path('components/flash-messages/', views.FlashMessagesComponentView.as_view(), name='component_flash_messages'),
    # Complex
    path('components/data-table/', views.DataTableComponentView.as_view(), name='component_data_table'),
    path('components/calendar/', views.CalendarComponentView.as_view(), name='component_calendar'),
    # Charts
    path('components/charts/', views.ChartsComponentView.as_view(), name='component_charts'),
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
