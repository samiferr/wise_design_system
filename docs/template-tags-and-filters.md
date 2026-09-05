# Template tags & filters

Two libraries, both in `wise_core/templatetags/`, generalized from DCMS7's `core/templatetags/icons.py`
and `core/templatetags/extra_tags.py` (the app-specific bits — patient age display, audit-log action
labels — were dropped; everything kept here is generic to any Django model).

## `wise_icons` — `{% load wise_icons %}`

### `{% lucide name size=18 cls="" stroke_width="1.5" %}`

Renders a vendored [Lucide](https://lucide.dev) icon **inline as SVG** (not `<img>`), so it sizes
itself from its own `viewBox` and inherits color from Tailwind `text-*` utilities via `currentColor`.

```django
{% lucide "search" size=16 cls="text-gray-500" %}
{% lucide "trash-2" size=14 class="text-accent-600" %}  {# 'class' also works, for parity with HTML #}
```

Icons are read from `wise_core/static/wise_core/icons/lucide/<name>.svg` and cached in-process
(`functools.lru_cache`) after first load. An unknown name renders an HTML comment
(`<!-- unknown lucide icon: name -->`) instead of raising, so a typo doesn't 500 a page — check your
browser's dev tools if an icon silently doesn't show up. Run `/icons/` on the demo site for the full
vendored set.

## `wise_tags` — `{% load wise_tags %}`

Generic lookups for templates that render fields by name from Python-side config (a datatable
column list, a detail-panel row list) rather than hardcoding field access per template.

### `{{ object|get_value:"field_name" }}` (filter)

`getattr()` by string, following `__`-joined relation lookups the way the ORM does:

```django
{{ invoice|get_value:"customer__company_name" }}
```

### `{{ url_name|startswith:"invoice_" }}` (filter)

`str.startswith()` for templates. Used by `nav_menu.html` to decide which sidebar item is selected
(`request.resolver_match.url_name|startswith:item.match`) — a prefix rather than a substring,
because with children nested under a parent an `order_line_list_view` URL contains both `line_` and
`order_` and a substring test would light up two sections at once.

### `{{ some_dict|get_dict_value:"key" }}` (filter)

`dict[key]` — for when your context value is a plain dict, not a model instance (templates can't
spell `dict[key]` directly).

### `{{ order|get_absolute_url:"customer" }}` (filter)

Resolves a `__`-joined field path down to its last relation and calls `.get_absolute_url()` on it —
`order|get_absolute_url:"customer__account"` calls `order.customer.get_absolute_url()`.

### `{% get_field_verbose_name object "field_name" %}` / `{% get_field_help_text object "field_name" %}`

Model-driven labels: reads `Model._meta.get_field(name).verbose_name` (or `.help_text`), walking
through `__`-joined relation paths via each field's `remote_field.model` along the way. Lets a
generic detail template label a row from the model's own `Meta` instead of a hardcoded string per
template — see `demo/showcase/templates/showcase/category/detail.html` for a live example.

### `{% get_model_verbose_name object %}` / `{% get_model_verbose_name_plural object %}`

`Model._meta.verbose_name` / `.verbose_name_plural`.

### `{% get_url_for_model "product" "detail_view" pk=object.pk %}` (simple_tag)

Builds a CRUD URL from a model name and action string, joined as `{model_name}_{action}` —
matching the URL-naming convention the demo site's `showcase/urls.py` uses throughout
(`product_list_view`, `product_detail_view`, `product_create_view`, `product_update_view`,
`product_delete_view`). Equivalent to `reverse("product_detail_view", kwargs={"pk": object.pk})`
but with the model name as a runtime string, for a genuinely model-agnostic generic template that
doesn't know which model it's rendering ahead of time.
