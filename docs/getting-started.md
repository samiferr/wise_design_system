# Getting started

The Wise Design System is a set of plain Django apps, distributed as one `pip`-installable package
(`wise-design-system`, providing the `wise_core`/`wise_autocomplete`/`wise_richtext` top-level
packages) rather than published to PyPI — install it straight from this repository:

```bash
pip install "wise-design-system @ git+https://github.com/samiferr/wise_design_system.git"
```

Pin to a commit or tag for reproducible installs
(`...wise_design_system.git@<sha-or-tag>`) rather than tracking a branch in a real project's
`requirements.txt`. `wise_autocomplete`'s `AutocompleteInputWidget` needs Django REST Framework —
pull it in with the `autocomplete` extra (`wise-design-system[autocomplete] @ git+...`).

Vendoring a copy (or a git submodule) still works if you'd rather patch the design system in place
alongside your project — nothing here depends on it being pip-installed specifically.

## What's in the box

| App | What it gives you |
|---|---|
| [`wise_core`](../wise_core) | Design tokens (Tailwind v4 `@theme`), the component CSS layer, `base.html` + generic CRUD templates, the `{% lucide %}` icon tag, generic template tags/filters, and the `WiseListView`/`WiseDetailView`/`WiseCreateView`/... view mixins (the "datatable" + CRUD system). |
| [`wise_autocomplete`](../wise_autocomplete) | `AutocompleteInputWidget` (DRF-backed search) and `AutoSuggestInputWidget` (client-side filter). See [autocomplete-widget.md](autocomplete-widget.md). |
| [`wise_richtext`](../wise_richtext) | `RichTextInputWidget`, a Quill-backed rich text editor. See [rich-text-widget.md](rich-text-widget.md). |
| [`demo/`](../demo) | A runnable Django project — the design system's own docs/demo website. Read its templates as worked examples. |

## 1. Install the apps

`pip install wise-design-system @ git+...` (see above) pulls in `Django` and `django-filter`
automatically — `djangorestframework` is only needed for `wise_autocomplete`'s
`AutocompleteInputWidget` (the `autocomplete` extra installs it for you).

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

Your project's own entry CSS file does both. `@source`/`@import` paths are resolved relative to the
CSS file, which works differently depending on how you got `wise_core` onto disk:

**Vendored / git submodule** (wise_core sits at a fixed path relative to your project — this is what
`demo/static_src/input.css` in this repo does, since `wise_core` is right there in the same
checkout):

```css
/* your_project/static_src/input.css */
@import "tailwindcss";

@source "../your_app/templates";
@source "../../wise_core/templates";
@source "../../wise_autocomplete/templates";   /* if installed */
@source "../../wise_richtext/templates";       /* if installed */

@import "../../wise_core/static/wise_core/css/tokens.css";
```

**Installed via `pip`** (the default per "Install the apps" above): `wise_core` lives wherever your
virtualenv put it, not at a fixed path relative to your project, so the `@source`/`@import` paths
above have to be resolved at build time instead of hardcoded. Generate a small partial before every
build and `@import` it from your entry file:

```python
# your_project/static_src/generate_wise_sources.py
# Run before every Tailwind build - see the "prebuild:css"/"prewatch:css"
# npm hooks below. Writes absolute @source/@import lines for whichever
# wise_* packages are actually installed, so input.css itself stays a
# portable, checked-in file with no environment-specific paths in it.
import importlib.util
from pathlib import Path

OUT = Path(__file__).parent / "_wise_sources.css"

lines = []
for package in ["wise_core", "wise_autocomplete", "wise_richtext"]:
    spec = importlib.util.find_spec(package)
    if spec is None or not spec.submodule_search_locations:
        continue
    package_dir = Path(spec.submodule_search_locations[0])
    lines.append(f'@source "{package_dir / "templates"}";')

tokens_css = importlib.util.find_spec("wise_core")
if tokens_css and tokens_css.submodule_search_locations:
    tokens_path = Path(tokens_css.submodule_search_locations[0]) / "static/wise_core/css/tokens.css"
    lines.append(f'@import "{tokens_path}";')

OUT.write_text("\n".join(lines) + "\n")
```

```css
/* your_project/static_src/input.css - checked in, no absolute paths */
@import "tailwindcss";
@import "./_wise_sources.css";   /* generated - gitignore it */

@source "../your_app/templates";
```

```json
{
  "scripts": {
    "prebuild:css": "python static_src/generate_wise_sources.py",
    "build:css": "tailwindcss -i ./static_src/input.css -o ./your_app/static/your_app/css/tailwind.css --minify",
    "prewatch:css": "python static_src/generate_wise_sources.py",
    "watch:css": "tailwindcss -i ./static_src/input.css -o ./your_app/static/your_app/css/tailwind.css --watch"
  }
}
```

Either way, build it with the Tailwind CLI (see this repo's root `package.json` for the vendored-case command):

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
- `match` marks the item `.selected` when `request.resolver_match.url_name` starts with it. Anchored at
  the start, so a nested child route (`category_product_list_view`) highlights Categories rather than
  both Categories and Products.

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
full mixin reference (tabbed parent/child pages, the confirm-action pattern, `ValidationError`
handling, own-records scoping).

A record with children of its own gets a tabbed page instead — the parent's overview, then one tab
per child model — since a parent usually has more than one (a product has variants *and* reviews).
Declare the bar once as a list of `ChildTab`s, hand it to `WiseParentDetailView` and to each
`WiseParentDetailChild*View` under it, and extend the matching `parent_*_generic.html` template.
See [generic-views-and-mixins.md](generic-views-and-mixins.md#master-detail-a-tabbed-parent-page--wiseparentdetailchildview).

## 5. Full worked example

`demo/showcase/` is a complete, runnable app built entirely on the pieces above — a `Category`
model with full datatable+CRUD, a `Product` model whose form uses both `AutocompleteInputWidget`
and `RichTextInputWidget`, and two child models under it (`ProductVariant`, `ProductReview`) that
turn a product's page into a tabbed one. Run it:

```bash
cd demo
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # creates superuser demo / wise-demo-2026 + sample rows
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` for the docs/demo home page, or sign in and browse
`/categories/` and `/products/` for the CRUD pages.
