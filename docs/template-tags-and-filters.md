# Template tags & filters

Two libraries, both in `wise_core/templatetags/`, generalized from DCMS7's `core/templatetags/icons.py`
and `core/templatetags/extra_tags.py` (the app-specific bits — patient age display, audit-log action
labels — were dropped; everything kept here is generic to any Django model).

## `wise_icons` — `{% load wise_icons %}`

### `{% lucide name size="m" cls="" stroke_width="2.4" label="" %}`

Renders a vendored [Lucide](https://lucide.dev) icon **inline as SVG** (not `<img>`), so it sizes
itself from its own `viewBox` and inherits color from Tailwind `text-*` utilities via `currentColor`.
It is drawn like Lumen's `Icon`: a 2.4 stroke on Lucide's 24-unit grid (2px at 20px, scaling with the
size) and five sizes tied to the control the icon sits in.

```django
{% lucide "search" %}                                      {# 20px (m), the default #}
{% lucide "search" size="s" cls="text-gray-500" %}         {# a step: xs 14, s 16, m 20, l 22, xl 26 #}
{% lucide "trash-2" size=16 class="text-accent-600" %}     {# or px; 'class' also works, for parity with HTML #}
{% lucide "search" size="l" label="Search" %}              {# role="img" with that name #}
```

| `size` | px | sits in |
| --- | --- | --- |
| `xs` | 14 | dense inline text, sort arrows |
| `s` | 16 | small buttons, field adornments, menu items |
| `m` | 20 (default) | medium buttons, navigation |
| `l` | 22 | large buttons |
| `xl` | 26 | extra-large buttons |

Never scale an icon with CSS. `stroke_width` is only for a glyph inside a small control (2.6 for a
chevron or sort arrow, which `tokens.css` already applies to the built-in ones). Without `label` the
icon is `aria-hidden`; on an icon-only control put `aria-label` on the button.

Lumen's own names are accepted as aliases (`add` → `plus`, `remove` → `minus`, `close` → `x`,
`home` → `house`, `delete` → `trash-2`, `edit` → `pencil`, `sort` → `arrow-up-down`,
`more` → `ellipsis`, `grid` → `layout-grid`, `chat` → `message-square`, `sliders` →
`sliders-horizontal`, `alert` → `alert-triangle`, `error` → `circle-alert`, `success` →
`circle-check`, `help` → `circle-question-mark`, `unlock` → `lock-open`, `refresh` →
`refresh-cw`); every other Lumen name is the Lucide name. All 56 Lumen icons are vendored.

Icons are read from `wise_core/static/wise_core/icons/lucide/<name>.svg` and cached in-process
(`functools.lru_cache`) after first load. An unknown name renders an HTML comment
(`<!-- unknown lucide icon: name -->`) instead of raising, so a typo doesn't 500 a page — check your
browser's dev tools if an icon silently doesn't show up. Run `/icons/` on the demo site for the full
vendored set.

### `{% status_glyph status size=18 cls="" %}`

Lumen's four filled status glyphs — a disc (a triangle for `notice`) with the Lucide glyph cut out,
since Lucide has no filled set. `status` is `info`, `positive`, `notice` or `negative` (aliases:
`informative`/`neutral`, `success`, `warning`, `error`/`danger`). Colored by `currentColor`, so
callouts, toasts and form alerts get the status family's content color from their own classes.
Decorative (`aria-hidden`): the message next to it names the status.

```django
{% status_glyph "positive" size=18 cls="callout-icon" %}
```

Each glyph carries its own `<mask id="wise-glyph-N">` so it still renders once the first copy sits in
a hidden dialog or drawer.

## `wise_tags` — `{% load wise_tags %}`

Generic lookups for templates that render fields by name from Python-side config (a datatable
column list, a detail-panel row list) rather than hardcoding field access per template.

### `{% empty_state title="…" description="…" illustration="empty" heading_level=2 %}…{% endempty_state %}`

Lumen's EmptyState: a message with a simple illustration for when there is nothing to show. The tag's
body is the next step (usually one button); `title` is required.

```django
{% load wise_tags %}
{% empty_state title="No projects yet" description="Projects you create will appear here." %}
    <a class="btn btn-primary" href="{% url 'project_create' %}">Create project</a>
{% endempty_state %}

{% empty_state illustration="search" title="No results for “invoice”" description="Check the spelling or try a broader search." %}
    <a class="btn btn-secondary" href="?">Clear search</a>
{% endempty_state %}
```

`illustration` is `"empty"` (the default; nothing exists yet), `"search"` (a search or filter matched
nothing), `None` / `"none"` for no picture, or your own markup (a string that is already safe and starts
with `<`). `heading_level` is 2 unless the empty state sits under a deeper heading. First-run copy says
what the space is for and how to start; no-results copy says what was searched and how to widen it;
keep the title under eight words. It is not for errors - use a callout. The markup is
`wise_core/components/_empty_state.html` (+ `_empty_illustration.html`); `_no_data.html` wraps the tag
for list views.

### `{{ object|get_value:"field_name" }}` (filter)

`getattr()` by string, following `__`-joined relation lookups the way the ORM does:

```django
{{ invoice|get_value:"customer__company_name" }}
```

### `{{ record.color|on_color }}` (filter)

`#000000` or `#ffffff`, whichever has the higher WCAG contrast on the CSS hex color (`#rgb` /
`#rrggbb`; anything else falls back to white, which is always at least 4.58:1). For text on a color
the *user* chose - a category swatch, a tag color - where a fixed token like `on-accent` can't be
right because the background isn't a token:

```django
<span class="avatar" style="background-color: {{ category.color }}; color: {{ category.color|on_color }}">
    {{ category.name|slice:":1" }}
</span>
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

### `{% page_url number %}` (simple_tag) and `{{ page_obj|page_window }}` (filter)

The two helpers behind `wise_core/components/_pagination.html`, Lumen's Pagination. `page_url` builds a
`?page=N` URL that keeps every other query parameter (`?view=table`, the sort, the filters), so paging
never drops them. `page_window` returns the numbers to show as a list: every page when there are at most
`5 + 2 * siblings` (default `siblings=1`), otherwise the first, last and current page with `siblings`
pages either side, and `None` wherever an ellipsis goes.

```django
{% for item in page_obj|page_window %}
    {% if item is None %}…{% else %}<a href="{% page_url item %}">{{ item }}</a>{% endif %}
{% endfor %}
```

### `{% get_url_for_model "product" "detail_view" pk=object.pk %}` (simple_tag)

Builds a CRUD URL from a model name and action string, joined as `{model_name}_{action}` —
matching the URL-naming convention the demo site's `showcase/urls.py` uses throughout
(`product_list_view`, `product_detail_view`, `product_create_view`, `product_update_view`,
`product_delete_view`). Equivalent to `reverse("product_detail_view", kwargs={"pk": object.pk})`
but with the model name as a runtime string, for a genuinely model-agnostic generic template that
doesn't know which model it's rendering ahead of time.
