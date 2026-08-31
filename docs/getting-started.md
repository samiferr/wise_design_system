# Getting started

The Wise Design System is a set of plain Django apps, not a package you `pip install` yet — vendor
the ones you need into your project (as a git submodule, a copy, or by pointing your `sys.path` at
this repo, the way `demo/manage.py` does for the demo site).

## What's in the box

| App | What it gives you |
|---|---|
| [`wise_core`](../wise_core) | Design tokens (Tailwind v4 `@theme`), the component CSS layer, `base.html` + generic CRUD templates, the `{% lucide %}` icon tag, generic template tags/filters, and the `WiseListView`/`WiseDetailView`/`WiseCreateView`/... view mixins (the "datatable" + CRUD system). |
| [`wise_autocomplete`](../wise_autocomplete) | `AutocompleteInputWidget` (DRF-backed search) and `AutoSuggestInputWidget` (client-side filter). See [autocomplete-widget.md](autocomplete-widget.md). |
| [`wise_richtext`](../wise_richtext) | `RichTextInputWidget`, a Quill-backed rich text editor. See [rich-text-widget.md](rich-text-widget.md). |
| [`demo/`](../demo) | A runnable Django project — the design system's own docs/demo website. Read its templates as worked examples. |

## 1. Install the apps

```bash
pip install django django-filter djangorestframework
```

Add the ones you use to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "django_filters",
    "rest_framework",       # only if you use wise_autocomplete's AutocompleteInputWidget
    "wise_core",
    "wise_autocomplete",    # optional
    "wise_richtext",        # optional
    "your_app",
]
```

Wire `wise_core`'s nav context processor and (for `LoginRequiredMixin`) a login URL:

```python
TEMPLATES = [{
    ...,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "wise_core.context_processors.nav",
    ]},
}]

LOGIN_URL = "login"
```

## 2. Build the CSS

Tailwind v4 needs to scan your templates (`@source`) to know which utility classes to generate, so
**every project builds its own `tailwind.css`** — there's no universal precompiled stylesheet to
just link to. `wise_core/static/wise_core/css/tokens.css` is a *partial*: the `@theme` tokens and
`@layer components` rules, with no `@import "tailwindcss"` and no `@source` of its own.

Your project's own entry CSS file does both:

```css
/* your_project/static_src/input.css */
@import "tailwindcss";

@source "../your_app/templates";
@source "../../wise_core/templates";
@source "../../wise_autocomplete/templates";   /* if installed */
@source "../../wise_richtext/templates";       /* if installed */

@import "../../wise_core/static/wise_core/css/tokens.css";
```

Then build it with the Tailwind CLI (see this repo's root `package.json` for the exact command):

```bash
npm install
npm run build:css     # -> wise_core/static/wise_core/css/tailwind.css
npm run watch:css      # during development
```

Link the built file in your base template — `wise_core/templates/wise_core/base.html` already does
this for you if you `{% extends "wise_core/base.html" %}`:

```django
<link rel="stylesheet" href="{% static 'wise_core/css/tailwind.css' %}">
```

Swap the design system's own brand for yours by overriding `--color-brand-*`/`--color-action-*` in
your own `@theme` block, imported *after* `tokens.css` — Tailwind's cascading `@theme` merges by
variable name, last one wins.

## 3. Extend the base template

```django
{% extends "wise_core/base.html" %}
{% block body %}
  <div class="page-panel">
    <h2>Hello</h2>
  </div>
{% endblock %}
```

`base.html` renders flash messages, a responsive sidebar (desktop) / top bar + slide-out sidebar
(mobile), and a `#modal_1` filter-panel slot. The sidebar's nav is driven entirely by a setting —
no project-specific links live in `wise_core`'s own templates:

```python
WISE_NAV_SECTIONS = [
    {
        "title": "Catalog",
        "items": [
            {"label": "Products", "url_name": "product_list_view", "icon": "pill", "match": "product_"},
        ],
    },
]
```

- `url_name` is reversed with no arguments (`{% url item.url_name %}`).
- `icon` is a vendored Lucide icon name (see `/docs/media/icons/` on the demo site, or
  `wise_core/static/wise_core/icons/lucide/`).
- `match` marks the item `.selected` when it's a substring of `request.resolver_match.url_name`.

## 4. Build a CRUD page (the "datatable" pattern)

```python
# views.py
from wise_core.mixins import WiseListView, WiseDetailView, WiseCreateView, WiseUpdateView, WiseDeleteView
from .models import Product
from .filters import ProductFilter

class ProductListView(WiseListView):
    model = Product
    filterset_class = ProductFilter          # or filterset_fields = [...]
    template_name = "catalog/product/list.html"
    paginate_by = 20

class ProductDetailView(WiseDetailView):
    model = Product
    template_name = "catalog/product/detail.html"

class ProductCreateView(WiseCreateView):
    model = Product
    fields = ["name", "category"]
    template_name = "catalog/product/form.html"
    success_url = reverse_lazy("product_list_view")
```

```django
{# catalog/product/list.html #}
{% extends "wise_core/generic/list_generic.html" %}
{% block list_title %}Products{% endblock %}
{% block card_item %}
  <a class="card" href="{{ item.get_absolute_url }}">{{ item.name }}</a>
{% endblock %}
```

Every `Wise*View` derives its `django.contrib.auth` permission automatically
(`<app_label>.<action>_<model_name>`) via `PermissionRequiredMixin` — grant users/groups the
standard Django `add`/`change`/`delete`/`view` permissions for the model and these views enforce
them with no extra config. See [generic-views-and-mixins.md](generic-views-and-mixins.md) for the
full mixin reference (master-detail views, the confirm-action pattern, `ValidationError` handling,
own-records scoping).

## 5. Full worked example

`demo/showcase/` is a complete, runnable app built entirely on the pieces above — a `Category`
model with full datatable+CRUD, and a `Product` model whose form uses both
`AutocompleteInputWidget` and `RichTextInputWidget`. Run it:

```bash
cd demo
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # creates superuser demo / wise-demo-2026 + sample rows
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` for the docs/demo home page, or sign in and browse
`/categories/` and `/products/` for the CRUD pages.
