from django import forms
from django.urls import reverse_lazy

from wise_autocomplete.widgets import AutocompleteInputWidget
from wise_richtext.widgets import RichTextInputWidget

from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'notes']
        widgets = {
            # Backed by CategoryViewSet (showcase/api.py), registered as
            # 'category-api' on the demo's DRF router - see
            # docs/autocomplete-widget.md's "Backend contract".
            'category': AutocompleteInputWidget(attrs={
                'data-headers': 'on',
                'data-url': reverse_lazy('category-api-list'),
                'data-text_field': 'name',
            }),
            'notes': RichTextInputWidget(),
        }
