from django import forms
from django.urls import reverse_lazy

from wise_autocomplete.widgets import AutocompleteInputWidget, AutoSuggestInputWidget
from wise_core.widgets import (
    ColorInput,
    ComboboxInput,
    OTPField,
    RatingInput,
    SwitchInput,
)
from wise_richtext.widgets import RichTextInputWidget

from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'color': ColorInput(),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'rating', 'available_from', 'datasheet', 'notes']
        widgets = {
            # Backed by CategoryViewSet (showcase/api.py), registered as
            # 'category-api' on the demo's DRF router - see
            # docs/autocomplete-widget.md's "Backend contract".
            'category': AutocompleteInputWidget(attrs={
                'data-headers': 'on',
                'data-url': reverse_lazy('category-api-list'),
                'data-text_field': 'name',
            }),
            'rating': RatingInput(),
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'notes': RichTextInputWidget(),
        }


COUNTRY_SUGGESTIONS = [
    'Belgium', 'Brazil', 'Canada', 'Denmark', 'France', 'Germany',
    'Japan', 'Morocco', 'Netherlands', 'Portugal', 'Spain', 'Tunisia',
]


class KitchenSinkForm(forms.Form):
    """
    Every form control the design system ships, in one unbound form.

    The Forms doc pages render individual fields off this so the examples show
    real Django-rendered widgets - the same HTML a project would get - instead
    of hand-written markup that could drift from what the widgets emit. It is
    never saved; it exists purely to be rendered.
    """

    # ── Text-ish ──────────────────────────────────────────────────────────
    full_name = forms.CharField(
        label='Full name',
        widget=forms.TextInput(attrs={'placeholder': 'Ada Lovelace'}),
        help_text='Shown to other members of your team.',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'ada@example.com'}),
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'type': 'tel', 'placeholder': '+1 555 0100'}),
    )
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    website = forms.URLField(required=False, widget=forms.URLInput)
    bio = forms.CharField(required=False, widget=forms.Textarea)

    # ── Numeric ───────────────────────────────────────────────────────────
    quantity = forms.IntegerField(
        required=False, min_value=0, max_value=999, initial=1,
        widget=forms.NumberInput(attrs={'step': 1}),
    )

    # ── Choice ────────────────────────────────────────────────────────────
    category = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('electronics', 'Electronics'), ('kitchen', 'Kitchenware')],
    )
    country = forms.CharField(
        required=False,
        widget=ComboboxInput(choices=COUNTRY_SUGGESTIONS),
        help_text='Pick a suggestion or type your own.',
    )
    plan = forms.ChoiceField(
        required=False,
        choices=[('free', 'Free'), ('pro', 'Pro'), ('team', 'Team')],
        widget=forms.RadioSelect,
        initial='pro',
    )
    interests = forms.MultipleChoiceField(
        required=False,
        choices=[('design', 'Design'), ('code', 'Code'), ('ops', 'Ops')],
        widget=forms.CheckboxSelectMultiple,
    )

    # ── Toggles ───────────────────────────────────────────────────────────
    subscribe = forms.BooleanField(required=False, initial=True, label='Subscribe to updates')
    notifications = forms.BooleanField(
        required=False, initial=True, label='Email notifications', widget=SwitchInput,
    )

    # ── Specialised ───────────────────────────────────────────────────────
    rating = forms.ChoiceField(
        required=False,
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=RatingInput(),
        initial=4,
    )
    brand_color = forms.CharField(required=False, initial='#16a34a', widget=ColorInput)
    verification_code = OTPField(
        required=False, length=6,
        help_text='Paste the whole code and it spreads across the boxes.',
    )
    attachment = forms.FileField(required=False)
    starts_on = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    starts_at = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    scheduled_for = forms.DateTimeField(
        required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    # Django's own three-select date widget - the "Split Date" component.
    birthday = forms.DateField(required=False, widget=forms.SelectDateWidget(years=range(1950, 2031)))

    # ── App-provided widgets ──────────────────────────────────────────────
    linked_category = forms.CharField(
        required=False,
        label='Linked category (autocomplete)',
        widget=AutocompleteInputWidget(attrs={
            'data-headers': 'on',
            'data-url': reverse_lazy('category-api-list'),
            'data-text_field': 'name',
        }),
    )
    # AutoSuggestInputWidget reads its options from a <datalist> named by
    # data-list (see set_arr_from_list_attr in the widget's template); the
    # doc page renders that <datalist> alongside the field.
    tag = forms.CharField(
        required=False,
        label='Tag (auto suggest)',
        widget=AutoSuggestInputWidget(attrs={'data-list': 'tag_suggestions'}),
    )
    description = forms.CharField(
        required=False, label='Description (rich text)', widget=RichTextInputWidget,
    )
