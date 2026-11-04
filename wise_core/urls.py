"""
wise_core's own endpoints. Include them once, under any prefix::

    path('wise/', include('wise_core.urls')),

which gives ``{% url 'wise_set_appearance' %}`` -> ``/wise/appearance/``.
"""
from django.urls import path

from . import views

urlpatterns = [
    path('appearance/', views.set_appearance, name='wise_set_appearance'),
]
