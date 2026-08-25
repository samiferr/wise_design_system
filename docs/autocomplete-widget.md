# Autocomplete widget

A Django form widget pair — `AutocompleteInputWidget` (server-side search against a DRF endpoint)
and `AutoSuggestInputWidget` (client-side filter over a plain JS array) — extracted verbatim from
[DCMS7](https://github.com/samiferr/DCMS7)'s `core` app (`core/widgets.py` +
`core/templates/core/widgets/*.html`).

This is a **straight extraction**, not a rewrite: the Python, the templates, and the vendored JS/CSS
are byte-for-byte the same behavior as the DCMS7 original, down to its quirks (see "Known
limitations" below). The only changes made were the ones required for the code to work outside of
DCMS7's own file layout — see "What changed during extraction".

## What's included

```
wise_autocomplete/
├── apps.py                                  # AppConfig — app label "wise_autocomplete"
├── widgets.py                                # AutocompleteInputWidget, AutoSuggestInputWidget
├── templatetags/
│   └── wise_autocomplete_icons.py            # {% lucide %} tag used by the widget templates
├── templates/wise_autocomplete/widgets/
│   ├── autocomplete_input.html               # markup + JS for AutocompleteInputWidget
│   ├── autosuggest_input.html                # markup + JS for AutoSuggestInputWidget
│   └── attrs.html                            # renders arbitrary widget.attrs onto the hidden input
└── static/wise_autocomplete/
    ├── js/axios.min.js                       # vendored axios build the widget calls directly
    ├── icons/{chevron-down,chevron-left,chevron-right,plus}.svg
    └── css/autocomplete.css                  # Tailwind v4 partial, see header comment in the file
```

## Dependencies

This widget is **not** a drop-in, dependency-free component. It brings its DCMS7 dependencies with it:

- **Django** form widgets (`forms.TextInput` subclasses with a custom `template_name`).
- **`axios`** — the widget templates call `axios.get(...)` / `axios.options(...)` directly as a
  global; there is no `import`/bundler step. The exact build DCMS7 uses is vendored at
  `static/wise_autocomplete/js/axios.min.js` — load it on any page that renders this widget,
  *before* the widget's own inline `<script>` runs (i.e. before the field renders, or via a
  `<script>` tag placed earlier in `<head>`/`<body>`).
- **Django REST Framework** — `AutocompleteInputWidget` talks to a DRF `ViewSet` (see "Backend
  contract" below). `AutoSuggestInputWidget` has no backend dependency at all — it filters an
  in-memory JS array (see "AutoSuggestInputWidget" below).
- **Tailwind CSS v4**, with the widget's own component classes and DCMS7's custom color tokens
  (`--color-action-500/600`, `--color-divider`, `--color-surface`, `--shadow-blueprint-lg`).
  The widget markup uses these as plain Tailwind utility classes inline (`border-divider`,
  `bg-surface`, `focus:border-action-500`, `bg-action-600`, …) — they are not optional cosmetics,
  the widget will render unstyled/broken without them. See the comment header in
  `static/wise_autocomplete/css/autocomplete.css` for the exact token values DCMS7 uses.
- The `{% lucide %}` template tag (vendored here as `wise_autocomplete_icons`), which inlines one of
  four vendored SVG icons (`chevron-down`, `chevron-left`, `chevron-right`, `plus`).

If your project doesn't already have DRF + a Tailwind v4 build + these design tokens, you're taking
all of that on by using this widget, not just the widget itself.

## Installation

1. Copy/vendor this `wise_autocomplete/` directory into your Django project (as a git submodule, a
   `pip install`-able package once this repo grows a `pyproject.toml`, or a plain copy — nothing here
   assumes a particular install mechanism yet).
2. Add `"wise_autocomplete"` to `INSTALLED_APPS` (needed for the app's templates and
   `{% load wise_autocomplete_icons %}` tag to be discoverable).
3. Make sure `static/wise_autocomplete/js/axios.min.js` is loaded on every page that uses the widget,
   *before* the widget's own inline `<script>` runs. Both widgets now declare a Django form
   `Media` class listing this file, so `{{ form.media }}` in your template's `<head>` is enough —
   or add `<script src="{% static 'wise_autocomplete/js/axios.min.js' %}"></script>` to your base
   template directly, the same way DCMS7's `templates/base.html` loads it globally.
4. Pull `static/wise_autocomplete/css/autocomplete.css` into your Tailwind entry file with
   `@import`, **and** make sure your `@theme` defines the color tokens listed above (or already has
   your own equivalents — adjust the widget's utility classes if your token names differ, since
   they're hardcoded in the templates).
5. Add a DRF `ViewSet` + router route for anything you want `AutocompleteInputWidget` to search — see
   "Backend contract" below.

## The two widgets

### `AutocompleteInputWidget`

Renders a text input backed by a dropdown panel that queries a DRF list endpoint as the user types
(debounced 500ms), with pagination (prev/next), optional column headers, keyboard navigation
(Arrow Up/Down, Enter, Escape, Space), and an optional "create new" link.

```python
from django import forms
from django.urls import reverse_lazy
from wise_autocomplete.widgets import AutocompleteInputWidget

class PatientSessionForm(forms.ModelForm):
    class Meta:
        model = PatientSession
        widgets = {
            'patient': AutocompleteInputWidget(attrs={
                'data-headers': 'on',
                'data-url': reverse_lazy('patient-api-list'),
                'data-create_object_url': reverse_lazy('patient_create_view'),
                'data-text_field': 'name',
            })
        }
```

`attrs` reference (all read via `element.dataset.*` in JS, so use `data-*` keys):

| attr | required | meaning |
|---|---|---|
| `data-url` | yes | DRF list endpoint, **with trailing slash** (e.g. `/api/patients/`). Also used for the per-item detail lookup by string concatenation: `url + pk` — see "Known limitations". |
| `data-text_field` | yes | key in the serialized object to show in the input once an item is selected (e.g. `'name'`, `'designation'`). |
| `data-headers` | no | literal string `'on'` to render a header row (desktop/table view only — headers are skipped on the mobile card view and skipped entirely if this attr is anything else/absent). |
| `data-create_object_url` | no | if set (and not `False`), the panel's "Nouveau" link points here (opens in a new tab). If omitted/`False`, the link is hidden. |
| `data-hidden_fields` | no | a Python list literal, e.g. `['dosages', 'quantities']` — columns to exclude from the header/table even though DRF's OPTIONS metadata includes them. |

The widget fires a `item_selected` `CustomEvent` on the **real** (hidden) input whenever an item is
picked (by click or Enter) or when the field's initial value is resolved on page load — `event.detail`
is the full serialized object DRF returned, not just the id. Listen for it to react to a selection:

```js
document.getElementById('id_patient').addEventListener('item_selected', function (e) {
    console.log(e.detail.name, e.detail.telephone)
})
```

### `AutoSuggestInputWidget`

A lighter widget with **no backend call** — it filters a plain JS array you assign to the hidden
input's `.arr` property at runtime, then re-renders by calling `.autocsuggest.get_data()` (note: the
JS instance is stored as `.autocsuggest`, not `.autosuggest` — this typo is preserved from the
original and is load-bearing, don't "fix" it without updating every call site).

```python
'drug_usage': AutoSuggestInputWidget(attrs={'list': 'drug_dosages'}),
```

```js
// populate/refresh suggestions in response to some other event, e.g. a related
// AutocompleteInputWidget's item_selected:
let usageInput = document.getElementById('id_drug_usage')
usageInput.arr = ['1 comprimé matin et soir', '2 comprimés le soir', ...]
usageInput.autocsuggest.get_data()
```

If `.arr` is never set, the widget renders an (empty, functional) input and dropdown shell that never
shows suggestions — this is the widget's actual, intended idle state, not a bug.

## Backend contract for `AutocompleteInputWidget`

`data-url` must point at a DRF `ViewSet` registered on a router (`rest_framework.routers`), because
the widget relies on DRF's default behavior for three different calls to that same URL:

1. **List/search** — `GET <data-url>?q=<query>&page=<n>&parent_id=<...>`, expected to return DRF's
   default `PageNumberPagination` shape: `{"count": N, "next": url|null, "previous": url|null,
   "results": [...]}`. Your `ViewSet.get_queryset()` should filter on `request.query_params.get('q')`
   (treat `None`/`'all'` as "no filter" — that's what DCMS7's own viewsets do).
2. **Detail lookup** (to resolve an initial/pre-filled value) — `GET <data-url><pk>?parent_id=<...>`
   (string concatenation of the URL and the field's current value, not a reversed URL — depends on
   Django's `APPEND_SLASH` redirect behavior to land on the real `<data-url><pk>/` route).
3. **Column headers** (only when `data-headers="on"`) — `OPTIONS <data-url>`, reading
   `response.data.actions.POST` for `{field_name: {label: "..."}}` — this is DRF's built-in
   `OPTIONS` metadata response for any writable `ModelViewSet`/`ModelSerializer`, nothing custom to
   implement.

Minimal example:

```python
# api.py
from rest_framework import viewsets, routers
from .models import Drug
from .serializers import DrugSerializer

class DrugViewSet(viewsets.ModelViewSet):
    serializer_class = DrugSerializer

    def get_queryset(self):
        qs = Drug.objects.all()
        q = self.request.query_params.get('q')
        if not q or q == 'all':
            return qs
        return qs.filter(designation__icontains=q)

router = routers.SimpleRouter()
router.register('api/drugs', DrugViewSet, basename='drug-api')
```

```python
# urls.py
urlpatterns += router.urls
```

## Known limitations (preserved as-is, not bugs to fix here)

These are genuine, observed behaviors of the DCMS7 original. They were kept intact because the task
was a faithful extraction, not a redesign:

- **Duplicate DOM ids across multiple widget instances.** Both templates render an element with the
  literal id `progress-bar` (not namespaced by field name, unlike every other id in the template,
  which *is* namespaced with `{{ widget.name }}`). Two `AutocompleteInputWidget`/`AutoSuggestInputWidget`
  fields on the same page will collide on this id — only the first one in the DOM gets a working
  progress indicator. If you need more than one instance per page, this is the one spot you may need
  to patch locally.
- **The "parent" scoping feature is effectively dead code.** Both widgets look for `document.
  getElementById('parent')` and, if found, read a `data-parent` attribute off it to send as
  `parent_id` on every request. No template in DCMS7 actually defines an element with `id="parent"`,
  so in practice `parent_id` is always sent as the literal string `false`. The mechanism exists (for
  nested/scoped lookups, e.g. "cities in this department") but nothing wires it up today.
- **`AutoSuggestInputWidget`'s `list` attr does nothing.** `attrs={'list': 'drug_dosages'}` renders a
  plain HTML `list="drug_dosages"` attribute (via `attrs.html`) but the widget's JS never reads it —
  suggestion data only ever comes from the `.arr` property set by page-specific JS. This looks like a
  leftover from an earlier `<datalist>`-based implementation.
- **`data-url` needs a trailing slash**, and the detail-lookup URL is built by raw string
  concatenation (`url + pk`), not `reverse()`. Get the trailing slash on `data-url` wrong and both the
  list call and (especially) the detail call will misbehave.
- **`.selected`/`.autocomplete-table tr.selected` styling is hardcoded**, not themeable through attrs.

## What changed during extraction

Only what was structurally unavoidable when moving from "an app that lives inside one specific
project's `BASE_DIR`" to "a standalone, reusable app":

- **Template/static namespacing**: `core/widgets/*.html` → `wise_autocomplete/widgets/*.html`,
  `core/icons/lucide/*.svg` → `wise_autocomplete/icons/*.svg`, to avoid clobbering a consuming
  project's own `core` app if one exists.
- **Icon tag library renamed** `icons` → `wise_autocomplete_icons` (same `{% lucide %}` tag name
  inside it) so `{% load icons %}` in a consuming project's own templates doesn't collide with this
  package's tag library.
- **Icon directory resolution**: DCMS7's `core/templatetags/icons.py` resolves icons via `settings.
  BASE_DIR / 'core' / 'static' / ...` — i.e. relative to the *host project's* root, which only works
  because `core` is physically inside DCMS7's own `BASE_DIR`. This extracted copy
  (`templatetags/wise_autocomplete_icons.py`) resolves the icon directory relative to the file itself
  (`Path(__file__).resolve().parent.parent / 'static' / ...`) instead, so it keeps working regardless
  of where the consuming project's `BASE_DIR` points. This is the one functional code change made
  during extraction, and it was necessary for the widget to work outside of DCMS7 at all.

Nothing else — not the widget classes' behavior, not the JS state machine, not the CSS rules, not the
French copy (`"Aucun objet trouvé !"`, `"Nouveau"`, `"Page N"`) — was touched.

## See also

`docs/autocomplete-widget-for-ai.md` — a denser reference aimed at an AI coding agent wiring this
widget into a new form, covering the same ground with less prose and more "don't do X" flags.
