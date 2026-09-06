# Generic views & mixins (the "datatable" / CRUD system)

Source: [`wise_core/mixins.py`](../wise_core/mixins.py) — generalized from DCMS7's `core/generic.py`
(its `W2*` views). The permission-driven CRUD pattern is kept; the multi-tenant/SaaS-specific bits
(membership roles, tenant-scoped querysets) are stripped out and left as override points, since
those depend on a project's own tenancy model rather than being something a reusable design system
can assume.

Every view below requires `LoginRequiredMixin`'s login and derives its
`django.contrib.auth` permission automatically as `<app_label>.<action>_<model_name>` — you never
write `get_permission_required()` yourself for a plain model.

## The five CRUD views

| View | Django base | Permission | Notes |
|---|---|---|---|
| `WiseListView` | `django_filters.views.FilterView` | `view` | Paginated (`paginate_by`), filtered (`filterset_class`/`filterset_fields`), sortable (`sortable_fields`). This *is* the "datatable": pair it with `wise_core/generic/list_generic.html` and the `.data-table`/`.card` CSS. Context also gets `filter_kwargs_count` and `filter_kwarg` (the active filters as `{label: value}`, for the filter-panel badge) and `current_sort` (the active `?sort=` value, or `None`). |
| `WiseDetailView` | `DetailView` | `view` | Pair with `wise_core/generic/detail_generic.html`. |
| `WiseCreateView` | `CreateView` | `add` | Auto-populates `instance.created_by` from `request.user` if the model has that field (`AutoCreatedByMixin`). Catches a `ValidationError` raised from `form_valid()`/model `clean()`/`save()` and turns it into a form error instead of a 500 (`ValidationErrorFormMixin`) — on the field named in `error.params["field"]` if the model raised one with that param, else as a non-field error. |
| `WiseUpdateView` | `UpdateView` | `change` | Same `ValidationError` handling as `WiseCreateView`. |
| `WiseDeleteView` | `DeleteView` | `delete` | |

All five mix in `SuccessMessageMixin` (set `success_message = "..."` , with `%(field)s`
interpolation from the saved instance's `__dict__`, same as vanilla Django).

## Column sorting: `WiseListView.sortable_fields`

Off by default (an empty tuple). Set `sortable_fields` to the field names — or `__`-joined relation
lookups — a visitor may pass as `?sort=<field>`/`?sort=-<field>`:

```python
class ProductListView(WiseListView):
    model = Product
    sortable_fields = {"name", "category__name", "rating"}
```

Anything outside the allowlist is ignored and the view falls back to `ordering` — never read
`request.GET["sort"]` straight into `order_by()` yourself, since that lets a visitor order by any
field, or traverse relations, as a slow-query and information-disclosure hazard. A deterministic `pk`
tiebreak is always appended, so pagination can't repeat or skip rows across pages. Render header cells
with `wise_core/components/_sortable_th.html` (`{% include ... with field="name" label="Name" %}`),
which reads `current_sort` back out of the context and renders the right icon — see
`docs/data-viz/data-table.html`'s "Column ordering" section.

## `OwnRecordsMixin` — opt-in "my records only" scoping

Off by default. Set `own_records_only = True` on a `WiseListView`/`WiseDetailView`/`WiseUpdateView`/
`WiseDeleteView` subclass (or override `is_own_records_only()` for a runtime check, e.g. based on
the user's role) to restrict the queryset to `created_by=request.user`. Requires the model to have a
`created_by` field.

## Master-detail: a tabbed parent page + `WiseParentDetailChild*View`

A record with children of its own is rendered as a **tabbed page**, not one long scroll: the
parent's overview is the first tab and each child model gets its own. That is the shape because a
parent usually has more than one child model — a product has variants *and* reviews, the way a
patient has payments, prescriptions and appointments — and the tab bar is what keeps them all one
record instead of five unrelated pages.

Nest the child routes under the parent. The parent's pk in the URL is what scopes every child
queryset, and what lets every page in the group render the same bar:

```python
urlpatterns = [
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_detail_view"),

    path("products/<int:parent_pk>/variants/",
         ProductVariantListView.as_view(), name="product_variant_list_view"),
    path("products/<int:parent_pk>/variants/create/",
         ProductVariantCreateView.as_view(), name="product_variant_create_view"),
    path("products/<int:parent_pk>/variants/<int:pk>/",
         ProductVariantDetailView.as_view(), name="product_variant_detail_view"),
    path("products/<int:parent_pk>/variants/<int:pk>/update/",
         ProductVariantUpdateView.as_view(), name="product_variant_update_view"),
    path("products/<int:parent_pk>/variants/<int:pk>/delete/",
         ProductVariantDeleteView.as_view(), name="product_variant_delete_view"),

    # ... the same five for reviews
]
```

### The tab bar: `ChildTab`

Declare the bar once and hand it to every view in the group, so none of them can drift:

```python
PRODUCT_TABS = [
    ChildTab.overview(_("Overview"), "product_detail_view", icon="info"),
    ChildTab(_("Variants"), "product_variant_list_view",
             model=ProductVariant, icon="tag", count="variants"),
    ChildTab(_("Reviews"), "product_review_list_view",
             model=ProductReview, icon="star", count="reviews"),
]
```

| Argument | What it does |
|---|---|
| `label` | The tab's text. |
| `url_name` | The child's list view, reversed with the parent's pk. |
| `model` | The child model — the tab is hidden from a user without `<app_label>.view_<model>`. |
| `permission` | An explicit codename (or several) instead of the one derived from `model`. Neither set ⇒ always visible. |
| `icon` | A Lucide icon rendered before the label. |
| `count` | A badge: the name of a related manager on the parent (`"variants"` → `parent.variants.count()`), of a plain attribute/annotation, or a callable taking the parent. |
| `match` | The URL-name prefix that lights the tab up. Defaults to `url_name` minus a trailing `_list`/`_list_view`, so the child's create/update/delete/detail pages keep their own tab selected. Longest match wins. |
| `url_kwarg` | The URL kwarg carrying the parent's pk — `"parent_pk"` by default, `"pk"` for `ChildTab.overview()`. |

`ChildTabsMixin` resolves that list per request into `child_tabs` (and `selected_tab`) in the
context; `wise_core/components/_child_tabs.html` renders it, and the generic templates below
already include it.

### The views

```python
class ProductDetailView(WiseParentDetailView):        # the Overview tab
    model = Product
    child_tabs = PRODUCT_TABS
    template_name = "shop/product/detail.html"


class ProductVariantListView(WiseParentDetailChildListView):
    model = ProductVariant
    parent_model = Product
    parent_field = "product_id"                       # the FK back to the parent
    child_tabs = PRODUCT_TABS
    template_name = "shop/product/variant/list.html"


class ProductVariantCreateView(WiseParentDetailChildCreateView):
    model = ProductVariant
    parent_model = Product
    parent_field = "product_id"
    child_tabs = PRODUCT_TABS
    child_list_url_name = "product_variant_list_view"
    form_class = ProductVariantForm                   # no `product` field on it
    template_name = "shop/product/variant/form.html"
```

- `WiseParentDetailView` is `WiseDetailView` plus the tab bar. It also puts the record in the
  context as `parent_object` (the same object as `object`), so one chrome renders the header on the
  overview and on every child page alike.
- `WiseParentDetailChildListView`/`CreateView`/`UpdateView`/`DeleteView`/`DetailView` resolve
  `get_parent_object()` from `parent_pk_url_kwarg` (default `"parent_pk"`, fetched once per request
  and cached), scope `get_queryset()` to it, and merge `parent_object` and `child_list_url` into the
  context. `Create` sets `parent_field` on the instance before saving, so the parent is never a form
  field a visitor could point somewhere else.
- `child_list_url_name` names the tab the view lives in: `Create`/`Update`/`Delete` redirect there
  after saving, and the generic templates point their back link and Cancel button at it.

### The templates

| Template | For |
|---|---|
| `wise_core/generic/parent_base_generic.html` | The shared chrome: parent action bar, parent title, tab bar, `parent_body`. Everything below extends it. |
| `wise_core/generic/parent_detail_generic.html` | The parent's own overview tab (`WiseParentDetailView`). |
| `wise_core/generic/parent_child_list_generic.html` | One child model's rows (`...ChildListView`). |
| `wise_core/generic/parent_child_form_generic.html` | Add/edit a child (`...ChildCreateView`/`...ChildUpdateView`). |
| `wise_core/generic/parent_child_confirm_generic.html` | Delete a child (`...ChildDeleteView`). |
| `wise_core/generic/parent_child_detail_generic.html` | One child record (`...ChildDetailView`). |

They use the same block names as their flat counterparts (`detail_rows`, `list_body`/`card_item`,
`form_fields`, `confirm_rows`), so moving a page into a tabbed group is a matter of changing which
template it extends.

The parent's own header — where "back" goes, what can be done to the parent, its name — is one
`parent_header` block. Put it in a partial and override the block with a one-line include, rather
than repeating the markup in every page of the group:

```django
{% extends 'wise_core/generic/parent_child_list_generic.html' %}

{% block parent_header %}{% include 'shop/product/_header.html' %}{% endblock %}

{% block list_actions %}
    <a class="btn btn-primary" href="{% url 'product_variant_create_view' parent_pk=parent_object.pk %}">
        {% lucide "plus" size=16 %}<span>New variant</span>
    </a>
{% endblock %}
```

The list heading, the record count, the empty state and the pagination all come from the generic
template; `list_title` defaults to the selected tab's own label.

## Confirm-and-act: `ConfirmActionMixin` / `WiseConfirmActionView`

For a POST-only "do this one thing to the object" action that isn't create/update/delete — cancel,
approve, archive:

```python
class CancelOrderView(WiseConfirmActionView):
    model = Order
    action = "cancel"                    # calls object.cancel(request.user)
    action_name = "Cancel order"
    success_url = reverse_lazy("order_list_view")
```

Permission is derived as `<app_label>.<action>_<model_name>` (`orders.cancel_order` above) — add a
matching entry to the model's `Meta.permissions` for actions that aren't the default
add/change/delete/view four. If `object.cancel(user)` raises `ValidationError`, its messages are
shown via `django.contrib.messages` and the confirm template re-renders instead of redirecting.

## Composing your own

Everything is built from small mixins (`AutoCreatedByMixin`, `ValidationErrorFormMixin`,
`OwnRecordsMixin`, `ParentObjectMixin`, `ConfirmActionMixin`) — reuse them directly if `WiseListView`
et al. don't fit. `permission_codename(model, action)` is the one helper the permission-derivation
logic is built on, if you need the same convention somewhere else.
