# Autocomplete widget

A Django form widget pair — `AutocompleteInputWidget` (server-side search against a DRF endpoint)
and `AutoSuggestInputWidget` (client-side filter over a plain JS array) — extracted verbatim from
[DCMS7](https://github.com/samiferr/DCMS7)'s `core` app (`core/widgets.py` +
`core/templates/core/widgets/*.html`).

This started as a **straight extraction** of DCMS7's `core/widgets.py` +
`core/templates/core/widgets/*.html`, byte-for-byte identical down to its quirks. A follow-up pass
then fixed a set of those inherited quirks explicitly flagged as bugs — see "Fixes applied on top of
the extraction" below for what changed and why; "What changed during extraction" still covers the
purely mechanical renames from the original extraction.

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
| `data-url` | yes | DRF list endpoint, **with or without a trailing slash** — the per-item detail lookup joins `data-url` and the pk itself (`build_detail_url()`), normalizing the slash rather than requiring the caller to get it exactly right. |
| `data-text_field` | yes | key in the serialized object to show in the input once an item is selected (e.g. `'name'`, `'designation'`). |
| `data-headers` | no | literal string `'on'` to render a header row (desktop/table view only — headers are skipped on the mobile card view and skipped entirely if this attr is anything else/absent). |
| `data-create_object_url` | no | if set (and not `False`), the panel's "Nouveau" link points here (opens in a new tab). If omitted/`False`, the link is hidden. |
| `data-hidden_fields` | no | a Python list literal, e.g. `['dosages', 'quantities']` — columns to exclude from the header/table even though DRF's OPTIONS metadata includes them. |
| `data-parent` | no | the DOM `id` of another field's real (non-`_fake`) input to scope this widget's requests to — its current `.value` is read live and sent as `parent_id` on every list/search and detail-lookup call. Omit for unscoped lookups (`parent_id` is sent as `false`). |

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
input's `.arr` property at runtime, then re-renders by calling `.autosuggest.get_data()`. The JS
instance is stored on the hidden input under two properties: `.autocsuggest` (the original typo'd
name, kept so existing call sites don't break) and `.autosuggest` (a correctly-spelled alias to the
same instance — prefer this one in new code).

```python
'drug_usage': AutoSuggestInputWidget(attrs={'list': 'drug_dosages'}),
```

```html
<datalist id="drug_dosages">
    <option value="1 comprimé matin et soir">
    <option value="2 comprimés le soir">
</datalist>
```

```js
// populate/refresh suggestions in response to some other event, e.g. a related
// AutocompleteInputWidget's item_selected:
let usageInput = document.getElementById('id_drug_usage')
usageInput.arr = ['1 comprimé matin et soir', '2 comprimés le soir', ...]
usageInput.autosuggest.get_data()
```

`attrs={'list': '<datalist id>'}` is the other way to seed `.arr`: on init, if `.arr` hasn't already
been set by page JS, the widget looks up the `<datalist>` with that id and populates `.arr` from its
`<option value="...">` list. Page JS assigning `.arr` directly always takes priority.

If `.arr` is never set (no `list` attr, and no page JS assignment), the widget renders an (empty,
functional) input and dropdown shell that never shows suggestions — this is the widget's intended
idle state, not a bug.

## Backend contract for `AutocompleteInputWidget`

`data-url` must point at a DRF `ViewSet` registered on a router (`rest_framework.routers`), because
the widget relies on DRF's default behavior for three different calls to that same URL:

1. **List/search** — `GET <data-url>?q=<query>&page=<n>&parent_id=<...>`, expected to return DRF's
   default `PageNumberPagination` shape: `{"count": N, "next": url|null, "previous": url|null,
   "results": [...]}`. Your `ViewSet.get_queryset()` should filter on `request.query_params.get('q')`
   (treat `None`/`'all'` as "no filter" — that's what DCMS7's own viewsets do).
2. **Detail lookup** (to resolve an initial/pre-filled value) — `GET <data-url><pk>/?parent_id=<...>`.
   The widget builds this URL itself (`build_detail_url()`): it normalizes `data-url` to end in
   exactly one `/` before appending the (URL-encoded) pk and a trailing `/`, so it lands directly on
   the real DRF detail route without depending on Django's `APPEND_SLASH` redirect.
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

## Fixes applied on top of the extraction

The items below were genuine bugs inherited from the DCMS7 original, not intentional behavior, and
were corrected (both `AutocompleteInputWidget` and `AutoSuggestInputWidget`, since the two templates
share the same JS patterns):

- **Namespaced the `progress-bar` id.** Both templates used the literal id `progress-bar` (unlike
  every other id, which *is* namespaced with `{{ widget.name }}`), so two widget instances on the
  same page collided and only the first got a working progress indicator. The element is now
  `id="{{ widget.name }}_progress_bar"` in both templates.
- **`parent_id` scoping now actually works.** The widgets used to look for a page-global
  `document.getElementById('parent')` that no template ever defined, so `parent_id` was always sent
  as the literal string `false`. It's now a per-field `data-parent` attribute on the widget's own
  hidden input, naming the DOM id of another field to scope against; its live `.value` is read on
  every request via a `parent_id` getter. See the `data-parent` row in the attrs table above.
- **`AutoSuggestInputWidget`'s `list` attr now does something.** `attrs={'list': 'drug_dosages'}` used
  to render an inert `list="drug_dosages"` HTML attribute. The widget now reads `data-list` on init
  and, if `.arr` hasn't already been set by page JS, seeds it from the named `<datalist>`'s `<option>`
  values.
- **Detail-lookup URL building is now robust to the trailing slash**, via `build_detail_url()`
  (normalizes `data-url` to end in exactly one `/`, URL-encodes the pk, and appends a trailing `/`)
  instead of raw `url + pk` string concatenation. There's still no `reverse()` involved — this is
  client-side JS with no access to Django's URL resolver — but the previous footgun (get the trailing
  slash on `data-url` wrong and the detail call breaks) is gone.
- **Mobile card click handler in `AutoSuggestInputWidget` fixed.** `populate_cards()`'s click handler
  read `self.selected_item.id` / `self.selected_item[self.text_field]`, treating `.arr` entries as
  objects — but `AutoSuggestInputWidget`'s results are plain strings (unlike
  `AutocompleteInputWidget`, whose results are DRF-serialized objects). It now assigns the string
  directly, matching the desktop table handler (`populate_lines()`).

## Known limitations (still preserved as-is)

- **`.selected`/`.autocomplete-table tr.selected` styling is hardcoded**, not themeable through attrs.
- **`.autocsuggest` typo is still the primary property name** on `AutoSuggestInputWidget`'s hidden
  input, for backward compatibility with existing call sites (`usageInput.autocsuggest.get_data()`
  still works). A correctly-spelled `.autosuggest` alias to the same instance was added — prefer it in
  new code.
- **`AutoSuggestInputWidget.set_fake_input_value()` still calls the same `data-url` detail endpoint as
  `AutocompleteInputWidget`**, even though the "Dependencies" section above describes
  `AutoSuggestInputWidget` as having no backend dependency. In practice, if you rely on
  `AutoSuggestInputWidget` resolving an initial value from a pre-filled hidden input, `data-url` still
  needs to point at a working detail endpoint — this wasn't part of the requested fix set and is
  called out here rather than silently changed.

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
