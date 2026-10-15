# Properties widget (JSONField key/value editor)

`wise_core.widgets.PropertiesField` + `PropertiesWidget`: edit a model's `JSONField` as rows of
**key : value**. Each known key is an ordinary `django.forms` field, so it gets that field's
widget and is validated by that field's `clean()`. Free-form keys can be added and removed.
`cleaned_data[name]` is a plain JSON-native `dict`, ready to save.

Live example: `/docs/forms/properties-input/` on the demo site, and the **Specifications** field
on `/demo/products/<pk>/update/`.

```
wise_core/
├── properties.py                                   # PropertiesField, PropertiesWidget, JSONValueField
├── widgets.py                                      # re-exports them: from wise_core.widgets import PropertiesField
├── templates/wise_core/widgets/
│   ├── properties.html                             # container, <template> row, add/remove script (inline)
│   └── _property_row.html                          # one key | value | remove row
└── static/wise_core/css/tokens.css                 # .property-list, .property-row, .property-key, .property-value
```

No new app and no `{{ form.media }}`: it ships with `wise_core`, and its script (add and remove
rows, nothing else) is inline in the widget template, like the OTP input's.

## Quick start

### 1. The model

```python
# products/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=150)
    specs = models.JSONField("specifications", default=dict, blank=True)
```

`default=dict, blank=True` is the usual pairing: an empty object is a valid value, and the form
field is optional (`required=False` is `PropertiesField`'s default).

### 2. The form

Declare the field on the form. Listing `specs` in `Meta.fields` alone would give Django's raw JSON
textarea, and `Meta.widgets` can't carry a schema.

```python
# products/forms.py
from django import forms
from wise_core.widgets import PropertiesField, SwitchInput

from .models import Product


class ProductForm(forms.ModelForm):
    specs = PropertiesField(
        label="Specifications",
        schema={
            "weight_kg": forms.DecimalField(label="Weight (kg)", min_value=0, decimal_places=3),
            "color": forms.ChoiceField(choices=[("black", "Black"), ("white", "White"), ("steel", "Steel")]),
            "warranty_years": forms.IntegerField(label="Warranty (years)", min_value=0, max_value=10, required=False),
            "website": forms.URLField(required=False),
            "released": forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"})),
            "fragile": forms.BooleanField(required=False, widget=SwitchInput),
        },
        allow_extra=True,   # let users add keys the schema doesn't name
        max_extra=10,
        help_text="Known keys are validated; add any other key below.",
    )

    class Meta:
        model = Product
        fields = ["name", "specs"]
```

### 3. The view and template

Nothing special. Any `CreateView` / `UpdateView` (or `WiseCreateView` / `WiseUpdateView`) with
`form_class = ProductForm` works, and `wise_core/components/_form_fields.html` (used by
`form_generic.html`) renders the label, rows, help text and errors:

```python
# products/views.py
from wise_core.mixins import WiseCreateView, WiseUpdateView

class ProductUpdateView(WiseUpdateView):
    model = Product
    form_class = ProductForm
    template_name = "wise_core/generic/form_generic.html"
```

Rendering it by hand, keep it inside a `.form-field` so the inputs pick up the text-field styles:

```django
<div class="form-field{% if form.specs.errors %} form-field-error{% endif %}">
    <label class="form-label" for="{{ form.specs.id_for_label }}">{{ form.specs.label }}</label>
    {{ form.specs }}
    {% if form.specs.help_text %}<span class="helptext">{{ form.specs.help_text }}</span>{% endif %}
    {% if form.specs.errors %}<ul class="errorlist">{% for e in form.specs.errors %}<li>{{ e }}</li>{% endfor %}</ul>{% endif %}
</div>
```

Saving `{"weight_kg": "1.250", "color": "steel", "fragile": true, "origin": "FR"}` renders the
four schema rows filled in, then `origin` as a free row with a remove button.

## Arguments

| Argument | Default | What it does |
|---|---|---|
| `schema` | `{}` | `{key: forms.Field}`. One row per key, in this order, rendered by the field's widget and cleaned by the field. The row label is the field's `label` (or the key, prettified); its `help_text` shows under the row. |
| `allow_extra` | `False` | Allow keys outside the schema (an **Add property** button and a remove button per free row). With `False`, stored keys the schema doesn't name are **not shown and are dropped on save**. |
| `extra_field` | `JSONValueField()` | Cleans the value of every free row. Any form field works: `forms.CharField(required=False)` (text only), `forms.IntegerField()`, `forms.JSONField()`... |
| `key_field` | `CharField(max_length=100)` | Cleans the key of every free row: `forms.SlugField()`, `forms.CharField(max_length=40, validators=[...])`... |
| `max_extra` | `None` | Most free rows allowed. The Add button disables at the cap and the server rejects more. |
| `drop_empty` | `True` | Leave a key out when its cleaned value is empty (`""`, `None`, `[]`, `{}`) instead of storing it. `False` and `0` are values, not empty. |
| `encoder` | `DjangoJSONEncoder` | Turns cleaned values into JSON-native data. |
| `required` | `False` | With `True`, the dict must end up with at least one key. (Individual keys use their own field's `required`.) |
| `label`, `help_text`, `disabled`, `validators`, ... | | The usual `forms.Field` arguments. `validators` run on the final dict. |

## Validation

Every row goes through its own field, so validation is Django's, not the widget's:

| Posted | Error |
|---|---|
| `weight_kg` = `-1` | `Weight (kg): Ensure this value is greater than or equal to 0.` |
| `weight_kg` left empty (required) | `Weight (kg): This field is required.` |
| `color` = `purple` | `Color: Select a valid choice. purple is not one of the available choices.` |
| free key `color` (a schema key) or a key used twice | `The key “color” is used more than once.` |
| a free value with no key | `Enter a key for the value “…”.` |
| free key `bad key` with `key_field=forms.SlugField()` | `bad key: Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.` |
| more free rows than `max_extra` | `Add at most 10 custom properties.` |

All errors are collected (one bad row doesn't hide the next) and raised together on the one form
field, each prefixed with the property's label, so `form.errors["specs"]` reads well on its own and
in an API response. When the form re-renders, only the controls that failed get
`aria-invalid="true"` and turn red; the rest keep their normal border. A row that is entirely blank
(no key, no value) is ignored.

Validation that spans keys goes where it always does, in `clean_<field>()` or `clean()`:

```python
class ProductForm(forms.ModelForm):
    specs = PropertiesField(schema={...})

    def clean_specs(self):
        specs = self.cleaned_data["specs"]
        if specs.get("fragile") and not specs.get("weight_kg"):
            raise forms.ValidationError("A fragile product needs a weight.")
        return specs
```

## What gets saved

Cleaned values are made JSON-native with the `encoder` (`DjangoJSONEncoder` by default):

| Schema field | Posted | Stored |
|---|---|---|
| `CharField`, `EmailField`, `URLField`, `SlugField`, `ChoiceField` | `steel` | `"steel"` |
| `IntegerField` | `2` | `2` |
| `FloatField` | `0.5` | `0.5` |
| `DecimalField` | `1.250` | `"1.250"` (a string, so no precision is lost) |
| `BooleanField` | checked / unchecked | `true` / `false` |
| `NullBooleanField` | unknown | left out (`None` is empty) |
| `DateField` / `DateTimeField` / `TimeField` | `2026-03-04` | `"2026-03-04"` (ISO 8601) |
| `DurationField` | `1 02:00:00` | `"P1DT02H00M00S"` |
| `UUIDField` | | `"…"` (string) |
| `MultipleChoiceField` | two options | `["a", "b"]` |
| `ModelChoiceField` | a category | its primary key, `3` |
| `ModelMultipleChoiceField` | two tags | `[3, 7]` |
| `forms.JSONField` | `{"w": 1}` | `{"w": 1}` (a nested value) |

Want a JSON number rather than a string for a decimal? Use `FloatField`, or pass your own
`encoder`. A `FileField` can't be stored in JSON; putting one in the schema raises
`ImproperlyConfigured`.

Stored values come back through the same field: an edit form passes `"2026-03-04"` to the
`DateField`'s widget, the category pk to the `ModelChoiceField`'s select, and so on.

### Free-form values: `JSONValueField`

The default `extra_field` stores what the user typed with its natural JSON type:

| Typed | Stored |
|---|---|
| `FR`, `hello world`, `01234` | `"FR"`, `"hello world"`, `"01234"` (text) |
| `4`, `1.5` | `4`, `1.5` |
| `true`, `false`, `null` | `true`, `false`, `null` (`null` is then dropped by `drop_empty`) |
| `[1, 2]`, `{"a": 1}` | the list / object |
| `"42"` (quoted) | `"42"` (forced text) |

It round-trips: a stored string that would read back as something else is shown quoted, and a
stored list or object is shown as JSON, so saving a record without touching a row never changes a
value's type. To store text only, pass `extra_field=forms.CharField(required=False)`.

## Backend recipes

### Free-form only (no schema)

A plain "custom attributes" bag, keys restricted to slugs, values to text up to 200 characters:

```python
class Device(models.Model):
    attributes = models.JSONField(default=dict, blank=True)

class DeviceForm(forms.ModelForm):
    attributes = PropertiesField(
        allow_extra=True,
        key_field=forms.SlugField(max_length=40),
        extra_field=forms.CharField(max_length=200, required=False),
        max_extra=20,
    )

    class Meta:
        model = Device
        fields = ["name", "attributes"]
```

### Typed values for free keys

Every free value an integer (a stock count per warehouse, say):

```python
stock = PropertiesField(
    allow_extra=True,
    key_field=forms.SlugField(label="Warehouse"),
    extra_field=forms.IntegerField(min_value=0),
)
# cleaned_data["stock"] == {"paris": 12, "lyon": 0}
```

### A fixed schema (settings object)

No free keys; every key is known and required ones must be filled:

```python
class NotificationSettingsForm(forms.ModelForm):
    settings = PropertiesField(
        schema={
            "digest": forms.ChoiceField(choices=[("off", "Off"), ("daily", "Daily"), ("weekly", "Weekly")]),
            "quiet_from": forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"})),
            "quiet_to": forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"})),
            "mentions_only": forms.BooleanField(required=False, widget=SwitchInput),
        },
        required=True,
    )

    class Meta:
        model = Profile
        fields = ["settings"]
```

Remember that with `allow_extra=False` keys the schema doesn't name are dropped on save; if other
code writes extra keys to the same column, either turn `allow_extra` on or merge them back in
`clean_settings()` from `self.instance.settings`.

### A schema that depends on the record

The schema is just a dict, so build it per form, e.g. from attribute definitions stored in the
database. Replace the whole field in `__init__` (the field configures its widget when it's
created):

```python
class Attribute(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="attributes")
    key = models.SlugField()
    label = models.CharField(max_length=80)
    kind = models.CharField(max_length=10, choices=[("text", "Text"), ("int", "Integer"),
                                                    ("decimal", "Decimal"), ("bool", "Yes/no"),
                                                    ("date", "Date")])
    required = models.BooleanField(default=False)


FIELD_FOR_KIND = {
    "text": lambda a: forms.CharField(label=a.label, required=a.required, max_length=200),
    "int": lambda a: forms.IntegerField(label=a.label, required=a.required),
    "decimal": lambda a: forms.DecimalField(label=a.label, required=a.required),
    "bool": lambda a: forms.BooleanField(label=a.label, required=False, widget=SwitchInput),
    "date": lambda a: forms.DateField(label=a.label, required=a.required,
                                      widget=forms.DateInput(attrs={"type": "date"})),
}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "specs"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category = self.instance.category if self.instance.pk else None
        attributes = category.attributes.all() if category else []
        self.fields["specs"] = PropertiesField(
            label="Specifications",
            schema={a.key: FIELD_FOR_KIND[a.kind](a) for a in attributes},
            allow_extra=True,
        )
```

### The Django admin

`PropertiesField` is a form field, so give the `ModelAdmin` a form that declares it:

```python
# products/admin.py
from django.contrib import admin

from .forms import ProductForm
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
```

Validation, saving and adding/removing rows all work there. The admin doesn't load the design
system's stylesheet (and shouldn't: Tailwind's base layer would restyle the whole admin), so the
rows stack with the admin's own input styles instead of the key | value grid.

### Validating the same payload in an API

`PropertiesField.clean()` also accepts a dict (or a JSON string), so an API can enforce the very
same schema as the HTML form:

```python
# products/serializers.py
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .forms import ProductForm


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "specs"]

    def validate_specs(self, value):
        field = ProductForm.base_fields["specs"]
        try:
            return field.clean(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)
```

`field.clean({"weight_kg": -1})` raises `["Weight (kg): Ensure this value is greater than or
equal to 0."]`; `field.clean([1])` raises `["Enter a valid JSON object."]`.

### Querying the stored data

It's a regular `JSONField`:

```python
Product.objects.filter(specs__color="steel")
Product.objects.filter(specs__fragile=True)
Product.objects.filter(specs__warranty_years__gte=2)
Product.objects.filter(specs__has_key="origin")
```

Decimals are stored as strings (see above), so compare them as strings, or cast them with
`Cast(KeyTextTransform("weight_kg", "specs"), DecimalField())` for numeric comparisons. If you
filter on a key all the time, it probably deserves its own column.

### Showing it on a detail page

```django
{% if object.specs %}
    <ul class="m-0 flex list-none flex-col gap-1 p-0">
        {% for key, value in object.specs.items %}
            <li><span class="text-content-subdued">{{ key }}</span> {{ value }}</li>
        {% endfor %}
    </ul>
{% else %}—{% endif %}
```

## How it works

The widget posts ordinary inputs, so it validates and re-renders like any Django widget and the
existing rows edit and post with JavaScript disabled (only adding and removing rows needs it):

| Input name | What |
|---|---|
| `specs` | an empty hidden marker, so a form without the widget on the page counts as "omitted" |
| `specs__s0`, `specs__s1`, ... | the value of the 1st, 2nd, ... schema key, as posted by that field's own widget |
| `specs__x<n>__key`, `specs__x<n>__value` | key and value of free row `n` (numbered by the script, gaps allowed, posted order kept) |

`PropertiesWidget.value_from_datadict()` collects these into rows; `PropertiesField.clean()` cleans
each row with its field and returns the dict. The field hands its `schema`, `allow_extra`,
`extra_field`, `key_field` and `max_extra` to the widget the same way `ChoiceField` hands its
choices to a `Select`.

Accessibility: a schema row's key is a `<label>` for its control; a free row's inputs are labelled
"Key" and "Value" and the remove button "Remove property". Adding a row focuses its key input;
removing one moves focus to the next row's remove button (or **Add property**).

## Limits

- **One level deep.** Values can be lists or objects (via `forms.JSONField`, `MultipleChoiceField`,
  or typed JSON in a free row), but they're edited as one value, not as nested rows.
- **Plain widgets in free rows.** The free row's value widget is cloned from a `<template>`, so it
  should be one that works without its own start-up script (text, number, select, textarea,
  checkbox). Schema rows can use any widget.
- **No files.** A `FileField` in the schema raises `ImproperlyConfigured`.
- **`allow_extra=False` drops unknown keys** on save (see the fixed-schema recipe above).
