# Rich text widget

`wise_richtext.widgets.RichTextInputWidget` — a `forms.Textarea` drop-in that renders as a
[Quill](https://quilljs.com) editor, extracted from DCMS7's `core.widgets.RichTextInputWidget` +
`core/templates/core/widgets/rich_html.html`.

## What's included

```
wise_richtext/
├── widgets.py                                  # RichTextInputWidget
├── templates/wise_richtext/widgets/
│   ├── rich_html.html                          # markup + JS that boots Quill
│   └── attrs.html                               # renders arbitrary widget.attrs onto the hidden textarea
└── static/wise_richtext/
    ├── js/quill.js                               # vendored Quill build (the same one DCMS7 ships)
    └── css/quill_snow.css                        # Quill's "snow" theme stylesheet
```

## How it works

The real form field is a `<textarea>` that stays in the DOM but hidden (`class="hidden"`); Quill
mounts on a sibling `<div>` and mirrors its content into the textarea (as HTML, via
`quill.getSemanticHTML()`) on every `text-change` event. On the server, `field.value` /
`form.cleaned_data[...]` is therefore **plain HTML** — sanitize it before rendering it back out
unescaped (the demo site does `{{ object.notes|safe }}` in a detail template only because it's a
throwaway demo; a real project should run it through `bleach` or similar before trusting it).

## Usage

```python
from django import forms
from wise_richtext.widgets import RichTextInputWidget

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body"]
        widgets = {"body": RichTextInputWidget()}
```

`RichTextInputWidget` declares a `Media` class (`quill_snow.css` + `quill.js`), so
`{{ form.media }}` in your template's `<head>` (or an `{% block extra_head %}` in
`wise_core/templates/wise_core/base.html`) is enough to load its assets — no manual `<script src>`
needed. See `demo/showcase/templates/showcase/product/form.html` for a working example (the
`Product.notes` field).

The toolbar is fixed (not configurable via widget `attrs`, matching the DCMS7 original): bold/
italic/underline, ordered/bullet lists, indent, RTL direction, headings 1–6, text color, alignment.
To change it, override `wise_richtext/templates/wise_richtext/widgets/rich_html.html` in your own
project's template directory (Django's app-directories loader lets a same-path template earlier in
`TEMPLATES` override this one) and edit `toolbarOptions`.

## Differences from the DCMS7 original

Two small, deliberate fixes made during extraction (unlike `wise_autocomplete`, which promises a
byte-for-byte port — this widget doesn't carry that promise):

- The initial-content script now runs the same way every other widget in this design system does,
  wrapped in `DOMContentLoaded`, instead of relying on execution order alone.
- The widget's initial value is interpolated into the boot script through Django's `escapejs` filter
  instead of being dropped into a JS string literal unescaped — the DCMS7 original could emit a
  broken (or, with adversarial content, injectable) inline `<script>` if the field's existing HTML
  contained an unescaped `'` or newline.
