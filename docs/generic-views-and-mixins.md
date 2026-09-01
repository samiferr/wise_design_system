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

## Master-detail: `ParentObjectMixin` + `WiseParentDetailChild*View`

For a child resource nested under a parent in the URL, e.g. `/orders/<parent_pk>/lines/`:

```python
urlpatterns = [
    path("orders/<int:parent_pk>/lines/", OrderLineListView.as_view(), name="orderline_list_view"),
]

class OrderLineListView(WiseParentDetailChildListView):
    model = OrderLine
    parent_model = Order
    parent_field = "order_id"   # FK on OrderLine pointing back to Order
    filterset_fields = ["description"]
```

`WiseParentDetailChildListView`/`CreateView`/`UpdateView`/`DeleteView`/`DetailView` all resolve
`self.get_parent_object()` from `parent_pk_url_kwarg` (default `"parent_pk"`) and merge
`{"parent_object": ...}` into the template context; `Create`/`Update` also set `parent_field` on the
instance before saving.

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
