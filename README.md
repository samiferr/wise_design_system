# Wise Design System

A Tailwind CSS v4 design system for Django projects, extracted from the
[DCMS7](https://github.com/samiferr/DCMS7) application. Complex components — datatables,
autocomplete widgets, rich text editing — are backed by Django itself and its ecosystem
(`django-filter`, Django REST Framework), not a JS framework: the JS each widget ships is a thin
layer over a real Django form field / class-based view, not a client-side app.

Start here: **[docs/getting-started.md](docs/getting-started.md)**.

## What's in the box

| App | What it gives you | Docs |
|---|---|---|
| [`wise_core`](wise_core) | Design tokens, the component CSS layer (buttons, cards, badges, forms, datatable, ...), `base.html` + generic CRUD templates, the `{% lucide %}` icon tag, generic template tags/filters, and the `Wise*View` class-based view mixins. | [design-tokens.md](docs/design-tokens.md), [template-tags-and-filters.md](docs/template-tags-and-filters.md), [generic-views-and-mixins.md](docs/generic-views-and-mixins.md) |
| [`wise_autocomplete`](wise_autocomplete) | `AutocompleteInputWidget` (DRF-backed search-as-you-type) and `AutoSuggestInputWidget` (client-side filter over a JS array). | [autocomplete-widget.md](docs/autocomplete-widget.md), [autocomplete-widget-for-ai.md](docs/autocomplete-widget-for-ai.md) |
| [`wise_richtext`](wise_richtext) | `RichTextInputWidget`, a Quill-backed rich text editor form widget. | [rich-text-widget.md](docs/rich-text-widget.md) |
| [`demo/`](demo) | A runnable Django project — the design system's own marketing site, docs site and demo app, built entirely from the pieces above. | see below |

## Run the site

```bash
npm install && npm run build:css       # compiles wise_core/static/wise_core/css/tailwind.css

cd demo
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo             # superuser demo / wise-demo-2026 + sample rows
python manage.py runserver
```

`http://127.0.0.1:8000/` is one Django project serving three deliberately separate surfaces:

| Path | What it is | Login |
|---|---|---|
| `/` | The marketing landing page — hero, feature grid, a live "try the design tokens" panel, code samples. | No |
| `/docs/` | The documentation site — every component, pattern and theming page, each with a live, running example next to its source. | No |
| `/demo/` | The demo app — a real `WiseListView`+`django-filter` datatable with full CRUD (`/demo/categories/`) and a form exercising the autocomplete/rich-text/rating/date/file widgets (`/demo/products/`), both with a card-list ⇄ data-table toggle, and tabbed parent/child pages (a product's Variants and Reviews, a category's Products). | `demo` / `wise-demo-2026` |

Every page — marketing, docs and demo alike — carries a settings icon (sidebar on desktop, topbar on
mobile) that opens a live panel for trying the six switchable design tokens: theme, palette,
density, corner radius, card shadow and background. See
[Switchable axes](docs/design-tokens.md#switchable-axes).

## Repo layout

```
wise_core/          design tokens, base templates, template tags/filters, CRUD view mixins
wise_autocomplete/  AutocompleteInputWidget, AutoSuggestInputWidget
wise_richtext/      RichTextInputWidget (Quill)
demo/                the marketing/docs/demo Django site (showcase app: marketing/, docs/, demo/, category/, product/)
docs/                design docs (this table's right-hand column)
package.json         Tailwind CLI build for the demo site (see docs/getting-started.md §2)
```
