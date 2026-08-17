# Autocomplete widget — reference for AI agents

Read this before wiring `wise_autocomplete` into a form. It assumes you've already read
`docs/autocomplete-widget.md` for the prose version; this file is the compressed fact sheet plus a
list of things that look like bugs but are intentional/inherited behavior — do not "fix" them as a
side effect of an unrelated task unless the user explicitly asks you to change this widget's behavior.

## Origin and fidelity

Extracted verbatim from DCMS7 (`samiferr/DCMS7`, `core/widgets.py` +
`core/templates/core/widgets/{autocomplete_input,autosuggest_input,attrs}.html` +
`core/templatetags/icons.py` + `core/static/core/{js/axios.min.js,icons/lucide/*.svg}` + the
autocomplete-related rules in `core/static/core/css/input.css`). Only two files were adapted, both
mechanically, both documented inline with a comment where the change was made:

1. `templatetags/wise_autocomplete_icons.py` — icon directory resolved relative to the file
   (`Path(__file__)`) instead of `settings.BASE_DIR`, because this app no longer lives inside a
   fixed, known project root.
2. Templates' `{% load %}` / `{% include %}` paths — repointed at the new `wise_autocomplete/...`
   namespace instead of `core/...`.

Everything else — Python widget classes, JS state machines, CSS rules, id-naming scheme, French UI
strings — is byte-identical to DCMS7. If you diff this against DCMS7's `core` app, the only
diffs should be the two items above plus path renames.

## File map

| File | Role |
|---|---|
| `wise_autocomplete/widgets.py` | `AutocompleteInputWidget`, `AutoSuggestInputWidget` — both `forms.TextInput` subclasses, differ only in `template_name`. |
| `wise_autocomplete/templates/wise_autocomplete/widgets/autocomplete_input.html` | DRF-backed widget: markup + the `Autocomplete` JS class (paginated search, headers, create-link). |
| `wise_autocomplete/templates/wise_autocomplete/widgets/autosuggest_input.html` | Client-array widget: markup + the `Autosuggest` JS class (substring filter over `input.arr`). |
| `wise_autocomplete/templates/wise_autocomplete/widgets/attrs.html` | One-line include: dumps `widget.attrs` onto the real hidden `<input>` as raw HTML attrs. |
| `wise_autocomplete/templatetags/wise_autocomplete_icons.py` | `{% lucide name size=N %}` — inlines a vendored SVG (`chevron-down`/`chevron-left`/`chevron-right`/`plus` only — that's the full vendored set, don't reference other icon names without adding the `.svg` file). |
| `wise_autocomplete/static/wise_autocomplete/js/axios.min.js` | Vendored axios build. The widget scripts call `axios` as a bare global — no import, no bundler. Must be `<script>`-loaded on the page before/along with the widget field renders. |
| `wise_autocomplete/static/wise_autocomplete/css/autocomplete.css` | Tailwind v4 `@layer` partial — must be pulled in via `@import` in the host project's Tailwind entry file, not linked as standalone CSS (it uses `@apply`). |

## Hard prerequisites before this widget will render/work at all

- `wise_autocomplete` in `INSTALLED_APPS` (template + templatetag discovery).
- `axios.min.js` loaded globally, before the widget's inline `<script>` executes.
- DRF installed, and a `ViewSet` + router route wired for every `AutocompleteInputWidget`'s
  `data-url` — `AutoSuggestInputWidget` needs none of this.
- Tailwind v4 build importing `autocomplete.css`, in a project whose `@theme` defines
  `--color-action-500`, `--color-action-600`, `--color-divider`, `--color-surface`,
  `--shadow-blueprint-lg` (or the widget's inline utility classes like `border-divider`,
  `bg-surface`, `focus:border-action-500` resolve to nothing).

If any of these is missing, the widget will silently render broken/unstyled rather than error loudly
— check for these first if a user reports "the autocomplete looks wrong" or "nothing shows up when I
type".

## Wiring a new `AutocompleteInputWidget` field — checklist

1. Backend: DRF `ViewSet.get_queryset()` must branch on `self.request.query_params.get('q')`
   (`None`/`'all'` → unfiltered; else filter). Register via `router.register(<path>, ViewSet,
   basename=...)` with a **trailing-slash** path.
2. `urls.py`: include `router.urls`.
3. Form: `SomeField: AutocompleteInputWidget(attrs={'data-url': reverse_lazy(<list-route-name>),
   'data-text_field': <serializer field to display>, 'data-headers': 'on'})` — `data-headers` and
   `data-create_object_url` are optional, everything else in the table in
   `docs/autocomplete-widget.md` is optional too except `data-url`/`data-text_field`.
4. If you need the selected object's other fields client-side, listen for `item_selected` on the
   real (non-`_fake`) input — `event.detail` is the whole serialized object, not just the id.

## Wiring a new `AutoSuggestInputWidget` field — checklist

1. No backend route needed.
2. Form: `SomeField: AutoSuggestInputWidget()`.
3. In page JS (not in this widget), set `document.getElementById('id_<field>').arr = [...]` and call
   `.autocsuggest.get_data()` whenever the array should change (typically inside another field's
   `item_selected` handler — see DCMS7's `transactions/templates/transactions/patient/
   patient__prescription/detail.html` for the canonical two-field pairing: a `drug`
   `AutocompleteInputWidget` whose `item_selected` populates a `drug_usage`/`drug_quantity` pair of
   `AutoSuggestInputWidget`s from `event.detail.dosages`/`event.detail.quantities`).
4. Property name is **`.autocsuggest`** (typo preserved from source), not `.autosuggest`. Getting
   this wrong fails silently (`undefined.get_data()` throws, swallowed by nothing — check the
   browser console, not a Django error page).

## Things that look like bugs — do not silently "fix" these

- `id="progress-bar"` is unnamespaced (unlike every other id in the template) — a second widget
  instance on the same page shares/steals the first one's progress bar element. Real limitation, not
  something to patch as a drive-by fix.
- `parent_id` is always sent as the literal string `"false"` in every real DCMS7 usage today, because
  the widget's "parent scoping" only activates if the page defines an element with `id="parent"`
  carrying a `data-parent` value, and no current template does. The mechanism is intentionally kept
  (it's dead-but-wired, not removed) — don't delete it under the assumption it's unused cruft, and
  don't assume a backend `q`/`page` param without also handling an incoming `parent_id` param it may
  send.
- `AutoSuggestInputWidget`'s `list` HTML attribute is inert — the JS never reads it. Suggestion data
  only ever comes from the runtime `.arr` assignment. If a user's `attrs={'list': '...'}` doesn't seem
  to do anything, that's expected; point them at the `.arr` pattern instead.
- Detail-lookup requests concatenate `data-url + pk` with no separator logic beyond what's already in
  `data-url` (must end in `/`) and no `reverse()` call — this is deliberate (matches DCMS7's router
  URL shape), not a missed `reverse()`.
- `hide_autocomplete_container()` in `autosuggest_input.html` sets `data_container_is_visible = true`
  (not `false`) — inconsistent with `AutocompleteInputWidget`'s version of the same method, and with
  the variable's own name. This is inherited from the DCMS7 source verbatim; the variable isn't read
  anywhere that would make the inconsistency externally observable today, but don't use
  `AutoSuggestInputWidget`'s `data_container_is_visible` as a reliable visibility check if you extend
  this widget later.

## Extending this widget

If a task asks you to add a feature (multi-select, a different pagination shape, namespaced
`progress-bar` ids, etc.), that is new work, not part of this extraction — implement it as a change on
top of this baseline and say so, rather than blending it silently into "the extraction." Keep this
file and `docs/autocomplete-widget.md` in sync with any such change so the "verbatim from DCMS7"
framing above stays accurate (or gets explicitly revised once this package's widget diverges from the
DCMS7 original).
