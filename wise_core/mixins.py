"""
Generic class-based view mixins for the Wise Design System.

Generalized from DCMS7's `core/generic.py` (its `W2*` views): the same
permission-driven CRUD pattern, with the tenant/SaaS-specific bits
(multi-tenant scoping, membership roles) stripped out and left as override
points instead, since those depend on an app's own tenancy model rather
than being something a reusable design system can assume.

Every view below auto-derives its `django.contrib.auth` permission codename
from the model (`<app_label>.<action>_<model_name>`), so a project using
these only needs to declare `model = MyModel` (and, for WiseListView, the
`django-filter` FilterSet config) to get a permission-gated CRUD view whose
templates match the rest of the design system (see
`wise_core/templates/wise_core/generic/*.html`).

A record with children of its own - a category's products, a patient's
payments and appointments, a product's variants and reviews - is rendered
as a *tabbed* page rather than one long scroll: `WiseParentDetailView` for
the parent's own overview tab and a `WiseParentDetailChild*View` per child
model, all sharing one `child_tabs` list of `ChildTab`s so the same bar
renders on every page in the group (see the `parent_*_generic.html`
templates).

A record with photos - a product, a listing, a property - gets its images
as a gallery via `WiseImageGalleryMixin`: one swipeable image with clickable
thumbnails on tablet and desktop and indicator dots on a phone, rendered by
`wise_core/components/_image_gallery.html`.
"""
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import router
from django.db.models.deletion import Collector, ProtectedError, RestrictedError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils.text import capfirst
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.base import ContextMixin
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin

from .gallery import build_image_gallery

try:
    from django_filters.views import FilterView
except ImportError as exc:  # pragma: no cover
    raise ImproperlyConfigured(
        'wise_core.mixins.WiseListView requires django-filter. '
        'Install it with `pip install django-filter` and add "django_filters" '
        'to INSTALLED_APPS.'
    ) from exc


def permission_codename(model, action):
    """`(Invoice, 'view')` -> `'billing.view_invoice'`."""
    return '{}.{}_{}'.format(model._meta.app_label, action, model._meta.model_name)


class OwnRecordsMixin:
    """
    Opt-in queryset scoping to "records the current user created". Off by
    default - set `own_records_only = True` on the view (or override
    `is_own_records_only()`) to turn it on. Requires the model to have a
    `created_by` field; WiseCreateView.form_valid() below populates it
    automatically when present.
    """
    own_records_only = False

    def is_own_records_only(self):
        return self.own_records_only

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.is_own_records_only():
            queryset = queryset.filter(created_by=self.request.user)
        return queryset


class WiseListView(OwnRecordsMixin, LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    """
    The "datatable" view: a permission-gated, paginated, django-filter-backed,
    sortable list view. Pair with `wise_core/generic/list_generic.html`
    (extend it and fill in `list_title`/`card_item`/`list_actions`), a
    `filterset_fields` list or a `filterset_class`, and the
    `.data-table`/`.card` CSS components.

    Column sorting is opt-in and allowlisted: set `sortable_fields` to the
    field names (or `__`-joined relation lookups) a visitor may pass as
    `?sort=<field>`/`?sort=-<field>` - never read the raw query parameter
    into `order_by()` yourself, since that lets a visitor order by any field,
    or traverse relations, as a slow-query and information-disclosure
    hazard. A deterministic `pk` tiebreak is always appended, so pagination
    can't repeat or skip rows across pages. Render header links with
    `wise_core/components/_sortable_th.html`, which reads `current_sort` back
    out of this view's context.

    Free-text search is a filter of its own: give the FilterSet a hidden
    `q` CharFilter (`search_param`) wired to a method that ORs the
    searchable columns. The view then hands the template `can_search` (and
    `search_query`), so `wise_core/components/_search_bar.html` - which the
    default `list_actions` block renders - appears by itself; the search is
    kept out of `filter_kwargs_count` and the filter drawer on purpose, as
    it has its own box and is not one of the drawer's fields.

    Set `create_url_name` to the URL name of this model's create page and the
    empty state (`wise_core/components/_no_data.html`) grows a "New <model>"
    button, and the list header can render its own from the same
    `create_url` - resolved once, here, and only for a user who actually
    holds the model's `add` permission, instead of every template pairing a
    hand-written `{% url %}` with a `{% if perms.app.add_model %}` of its own.
    """
    login_url = reverse_lazy('login')
    paginate_by = 20
    ordering = ['-pk']
    sortable_fields = ()
    create_url_name = None
    search_param = 'q'

    def get_permission_required(self):
        return (permission_codename(self.model, 'view'),)

    def get_current_sort(self):
        sort = self.request.GET.get('sort', '')
        return sort if sort.lstrip('-') in self.sortable_fields else None

    def get_ordering(self):
        current_sort = self.get_current_sort()
        if current_sort is None:
            return super().get_ordering()
        return [current_sort, 'pk']

    def can_add(self):
        """Whether the current user may create a record of this model."""
        return self.request.user.has_perm(permission_codename(self.model, 'add'))

    def get_create_url(self):
        """
        This list's "new record" page, or None when the view doesn't declare
        one. Overridden by `WiseParentDetailChildListView` to pass the parent
        along, since a child is always created under its parent.
        """
        if not self.create_url_name:
            return None
        return reverse(self.create_url_name)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_sort'] = self.get_current_sort()
        context['filter_kwargs_count'] = len(self.get_applied_filters())
        context['filter_kwarg'] = self.get_label_value_filter_kwargs()
        context['can_search'] = self.search_param in self.filterset.filters
        context['search_param'] = self.search_param
        context['search_query'] = self.request.GET.get(self.search_param, '')
        context['search_active'] = bool(context['can_search'] and context['search_query'])
        context['create_url'] = self.get_create_url() if self.can_add() else None
        context['model_verbose_name'] = self.model._meta.verbose_name
        context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        return context

    def get_applied_filters(self):
        """
        The filter fields the visitor has filled in - `{name: value}` - without
        the free-text search, which has its own box and is not one of the
        filter drawer's fields.
        """
        return {key: value for key, value in self.request.GET.items()
                if value != '' and key in self.filterset.filters and key != self.search_param}

    def get_label_value_filter_kwargs(self):
        return {self.filterset.filters[key].label: value for key, value in self.get_applied_filters().items()}


class WiseDetailView(OwnRecordsMixin, LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    login_url = reverse_lazy('login')

    def get_permission_required(self):
        return (permission_codename(self.model, 'view'),)


class AutoCreatedByMixin:
    """Populate `instance.created_by` from `request.user` on create, if the field exists."""

    def form_valid(self, form):
        if hasattr(form.instance, 'created_by_id'):
            form.instance.created_by = self.request.user
        return super().form_valid(form)


class ValidationErrorFormMixin:
    """
    Catch a `ValidationError` raised from `form_valid()`/model `clean()`/
    `save()` and turn it into a form error instead of a 500 - on the field
    named in `error.params['field']` when the model raised one, or as a
    non-field error otherwise.
    """

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as e:
            if getattr(e, 'params', None) and e.params.get('field'):
                form.add_error(e.params.get('field'), e.message)
            else:
                form.add_error(None, e.message)
            return self.form_invalid(form)


class WiseCreateView(ValidationErrorFormMixin, AutoCreatedByMixin, LoginRequiredMixin,
                      PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = reverse_lazy('login')

    def get_permission_required(self):
        return (permission_codename(self.model, 'add'),)


class WiseUpdateView(ValidationErrorFormMixin, OwnRecordsMixin, LoginRequiredMixin,
                      PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('login')

    def get_permission_required(self):
        return (permission_codename(self.model, 'change'),)


class ProtectedDeleteMixin:
    """
    A record that other records still point at through an `on_delete=PROTECT`
    (or `RESTRICT`) key is not deleted, and the visitor is told which ones -
    a page instead of a server error. `WiseDeleteView` (and so every
    `WiseParentDetailChildDeleteView`) already includes it.

    The confirm page knows before the visitor presses Delete:
    `get_context_data` asks Django's deletion collector what deleting the
    record would run into - without deleting anything - and hands the
    template `delete_blockers` (each kind of record in the way: its label,
    its count and, when the visitor may view that kind, its first few as
    links) and `delete_blocked_message`. `confirm_generic.html` /
    `parent_child_confirm_generic.html` then render
    `components/_delete_blockers.html` in place of the warning and leave the
    Delete button out. A POST that reaches the database's refusal anyway (a
    record added in between) is caught here and shows the same page.

    `protected_message` is an optional sentence of the view's own, said
    above the list ("This unit cannot be deleted: products use it."). A
    record's link is its `get_absolute_url()`; override `get_blocker_url()`
    for a kind of record that has no page of its own (an order line, whose
    order is the page a person opens).
    """
    protected_message = None
    # How many records of each kind the page names; the rest are counted.
    blocker_sample_size = 5

    def get_context_data(self, **kwargs):
        if 'delete_blockers' not in kwargs:
            kwargs['delete_blockers'] = self.describe_blockers(self.find_blockers(self.object))
        if kwargs['delete_blockers']:
            kwargs.setdefault('delete_blocked_message', self.get_protected_message())
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except (ProtectedError, RestrictedError) as error:
            blockers = self.describe_blockers(self.blocking_records(error))
            return self.render_to_response(self.get_context_data(form=form, delete_blockers=blockers))

    @staticmethod
    def blocking_records(error):
        if isinstance(error, ProtectedError):
            return error.protected_objects
        return error.restricted_objects

    @classmethod
    def find_blockers(cls, obj):
        """The records that keep `obj` from being deleted - none when it can go. Deletes nothing."""
        collector = Collector(using=router.db_for_write(obj.__class__, instance=obj), origin=obj)
        try:
            collector.collect([obj])
        except (ProtectedError, RestrictedError) as error:
            return cls.blocking_records(error)
        return ()

    def get_protected_message(self):
        if self.protected_message:
            return self.protected_message
        message = gettext('%(record)s cannot be deleted: the records below still refer to it. '
                          'Delete them or point them elsewhere first.') % {'record': capfirst(str(self.object))}
        if any(field.name == 'is_active' for field in self.object._meta.concrete_fields):
            message = '%s %s' % (message, gettext('You can also deactivate it instead.'))
        return message

    def describe_blockers(self, records):
        """
        The blocking records grouped by kind, for `_delete_blockers.html`:
        each kind's name and count and - when the visitor may view that kind -
        the first few of them, each with the page that shows it.
        """
        by_model = defaultdict(list)
        for record in records:
            by_model[record._meta.model].append(record)
        user = self.request.user
        groups = []
        for model, items in by_model.items():
            opts = model._meta
            items.sort(key=lambda item: item.pk)
            visible = user.has_perm(permission_codename(model, 'view'))
            shown = items[:self.blocker_sample_size] if visible else []
            groups.append({
                'label': capfirst(opts.verbose_name if len(items) == 1 else opts.verbose_name_plural),
                'count': len(items),
                'records': [{'label': str(item), 'url': self.get_blocker_url(item)} for item in shown],
                'more': len(items) - len(shown) if visible else 0,
            })
        groups.sort(key=lambda group: str(group['label']))
        return groups

    def get_blocker_url(self, record):
        """The page that shows a blocking record, or None when it has none."""
        get_url = getattr(record, 'get_absolute_url', None)
        if get_url is None:
            return None
        try:
            return get_url()
        except NoReverseMatch:
            return None


class WiseDeleteView(ProtectedDeleteMixin, OwnRecordsMixin, LoginRequiredMixin, PermissionRequiredMixin,
                      SuccessMessageMixin, DeleteView):
    model = None
    login_url = reverse_lazy('login')

    def get_permission_required(self):
        return (permission_codename(self.model, 'delete'),)


class ChildTab:
    """
    One tab in a parent record's tab bar.

    A parent normally has more than one child model - a patient's payments,
    diagnoses and appointments; a product's variants and reviews - so a
    parent record is a *tabbed* page: one tab per child model, plus the
    parent's own overview as the first. Build that first tab with
    `ChildTab.overview()`, which resolves its URL with `pk` (the parent's
    own detail route) instead of `parent_pk`::

        PRODUCT_TABS = [
            ChildTab.overview(_('Overview'), 'product_detail_view', icon='info'),
            ChildTab(_('Variants'), 'product_variant_list_view',
                     model=ProductVariant, icon='tag', count='variants'),
            ChildTab(_('Reviews'), 'product_review_list_view',
                     model=ProductReview, icon='star', count='reviews'),
        ]

    Hang that one list off `child_tabs` on the parent's detail view and on
    every child view underneath it (see `ChildTabsMixin`) and every page in
    the group renders the identical bar - defining the tabs once, in Python,
    rather than repeating a hand-written bar in each template.

    Arguments:

    `label`
        The tab's text. Wrap it in `gettext_lazy` in a translated project.
    `url_name`
        URL name of the child's list view, reversed with the parent's pk.
    `model`
        The child model. Used to derive the tab's permission, so a user
        without `<app_label>.view_<model>` never sees the tab.
    `permission`
        An explicit permission codename (or an iterable of them) to require
        instead of the one derived from `model`. A tab with neither `model`
        nor `permission` is always visible.
    `icon`
        Name of a Lucide icon to render before the label.
    `count`
        A badge showing how many children there are: the name of a related
        manager on the parent (`'variants'` -> `parent.variants.count()`),
        the name of a plain attribute or annotation, or a callable taking
        the parent record.
    `match`
        The URL-name prefix (or prefixes) that light this tab up. Defaults
        to `url_name` minus a trailing `_list`/`_list_view`, so the child's
        create/update/delete/detail pages keep their own tab selected -
        `product_variant_list_view` lights up for every URL name starting
        `product_variant`. When two tabs both match, the longest match wins.
    `url_kwarg`
        The URL kwarg carrying the parent's pk. `'parent_pk'` for a child
        list view, `'pk'` for the parent's own overview.
    """

    def __init__(self, label, url_name, *, model=None, permission=None, icon=None,
                 count=None, match=None, url_kwarg='parent_pk'):
        self.label = label
        self.url_name = url_name
        self.model = model
        self.permission = permission
        self.icon = icon
        self.count = count
        self.url_kwarg = url_kwarg
        self.match = self._resolve_match(match, url_name)

    @classmethod
    def overview(cls, label, url_name, **kwargs):
        """The parent's own tab: same bar, but reversed with `pk`."""
        kwargs.setdefault('url_kwarg', 'pk')
        return cls(label, url_name, **kwargs)

    @staticmethod
    def _resolve_match(match, url_name):
        if match is None:
            for suffix in ('_list_view', '_list'):
                if url_name.endswith(suffix):
                    return (url_name[: -len(suffix)],)
            return (url_name,)
        if isinstance(match, str):
            return (match,)
        return tuple(match)

    def get_permissions(self):
        if self.permission is not None:
            return (self.permission,) if isinstance(self.permission, str) else tuple(self.permission)
        if self.model is not None:
            return (permission_codename(self.model, 'view'),)
        return ()

    def is_visible(self, user):
        permissions = self.get_permissions()
        return not permissions or user.has_perms(permissions)

    def match_length(self, url_name):
        """Length of the longest prefix matching `url_name`, or 0 for no match."""
        if not url_name:
            return 0
        return max((len(prefix) for prefix in self.match if url_name.startswith(prefix)), default=0)

    def get_url(self, record):
        return reverse(self.url_name, kwargs={self.url_kwarg: record.pk})

    def get_count(self, record):
        if self.count is None:
            return None
        if callable(self.count):
            return self.count(record)
        value = getattr(record, self.count, None)
        # A related manager (or queryset) counts its rows; anything else -
        # an annotation, a property - is already the number.
        return value.count() if hasattr(value, 'all') else value


class ChildTabsMixin(ContextMixin):
    """
    Renders `child_tabs` into the context as the resolved tab bar, so every
    page of a parent/child group - the parent's overview and each child's
    list/create/update/delete/detail - carries the same navigation.

    Subclasses say which record the tabs hang off by implementing
    `get_tab_record()`; `WiseParentDetailView` returns the object being
    viewed, and `ParentObjectMixin` (so every `WiseParentDetailChild*View`)
    returns the parent - which is why those views list `ParentObjectMixin`
    ahead of this mixin, so its implementation wins over the stub below.

    Pair with `wise_core/components/_child_tabs.html`, which the
    `parent_*_generic.html` templates already include.
    """
    child_tabs = ()

    def get_child_tabs(self):
        return self.child_tabs

    def get_tab_record(self):
        raise NotImplementedError(
            '%s must implement get_tab_record() to say which record its tabs belong to.'
            % self.__class__.__name__
        )

    def build_child_tabs(self, record):
        """Resolve the declared tabs against this request: permissions, URLs, counts."""
        url_name = self.request.resolver_match.url_name if self.request.resolver_match else ''
        tabs = [tab for tab in self.get_child_tabs() if tab.is_visible(self.request.user)]
        # Longest match wins, so a `product_review_reply_*` tab beats the
        # `product_review_*` one it is nested under rather than lighting both.
        selected = None
        best = 0
        for tab in tabs:
            length = tab.match_length(url_name)
            if length > best:
                selected, best = tab, length
        return [
            {
                'label': tab.label,
                'url': tab.get_url(record),
                'icon': tab.icon,
                'count': tab.get_count(record),
                'selected': tab is selected,
            }
            for tab in tabs
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.get_child_tabs():
            tabs = self.build_child_tabs(self.get_tab_record())
            context['child_tabs'] = tabs
            # The tab this page sits under, so a template can title itself
            # from the bar instead of repeating the label - see
            # `parent_child_list_generic.html`'s `list_title` block.
            context['selected_tab'] = next((tab for tab in tabs if tab['selected']), None)
        return context


class WiseParentDetailView(ChildTabsMixin, WiseDetailView):
    """
    A parent record's own page - the first tab of a tabbed parent/child
    group. Identical to `WiseDetailView` apart from the tab bar and
    `parent_object` in the context, which is the same object as `object`
    here so that one chrome (`parent_base_generic.html`) can render the
    parent's title and actions on the overview and on every child page
    alike. Pair with `wise_core/generic/parent_detail_generic.html`.
    """

    def get_tab_record(self):
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_object'] = self.object
        return context


class ParentObjectMixin(ContextMixin):
    """
    Master-detail support: resolve a parent object from `parent_pk_url_kwarg`
    in the URLconf, for a child list/create/update/delete/detail view scoped
    under it (e.g. `/orders/<parent_pk>/lines/`).
    """
    parent_model = None
    parent_pk_url_kwarg = 'parent_pk'
    child_list_url_name = None
    paginate_by = 20
    _parent_object_cache = None

    def get_parent_object(self, queryset=None):
        """
        Fetch the parent named by `parent_pk_url_kwarg`, caching it for the
        rest of the request: the queryset scoping, the tab bar and the
        template each ask for it, and without the cache that is the same
        query three times on every child page.
        """
        if queryset is not None:
            return self._fetch_parent_object(queryset)
        if self._parent_object_cache is None:
            self._parent_object_cache = self._fetch_parent_object(
                self.parent_model._default_manager.all()
            )
        return self._parent_object_cache

    def _fetch_parent_object(self, queryset):
        pk = self.kwargs.get(self.parent_pk_url_kwarg)
        if pk is None:
            raise AttributeError(
                'Generic detail view %s must be called with a parent object pk in the URLconf.'
                % self.__class__.__name__
            )
        queryset = queryset.filter(pk=pk)

        try:
            return queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _('No %(verbose_name)s found matching the query')
                % {'verbose_name': queryset.model._meta.verbose_name}
            )

    def get_tab_record(self):
        """`ChildTabsMixin`'s hook: a child page's tabs belong to its parent."""
        return self.get_parent_object()

    def get_child_list_url(self):
        """
        The child's own list under this parent - the tab the visitor is
        working inside. Set `child_list_url_name` and the create/update/
        delete views redirect there after saving, and the generic templates
        point their back link and Cancel button at it (as `child_list_url`
        in the context), instead of every project spelling the same
        `reverse_lazy(..., kwargs={'parent_pk': ...})` out five times.
        """
        if not self.child_list_url_name:
            return None
        return reverse(
            self.child_list_url_name,
            kwargs={self.parent_pk_url_kwarg: self.get_parent_object().pk},
        )

    def get_parent_context_data(self, **kwargs):
        """
        Merge `{'parent_object': ...}` into an already-built context.
        Deliberately does NOT call `get_context_data()` itself: every
        caller below already holds a fully resolved context (from its own
        `super().get_context_data()` call) and only needs `parent_object`
        merged in. A second `get_context_data()` call here would re-enter
        the same MRO chain and produce an independent context dict that
        then clobbers the correct one on `.update()` - silently discarding
        an invalid, error-carrying form from `form_invalid()`.
        """
        context = {
            'parent_object': self.get_parent_object(),
            'child_list_url': self.get_child_list_url(),
        }
        context.update(kwargs)
        return context


class WiseParentDetailChildListView(ParentObjectMixin, ChildTabsMixin, WiseListView):
    """
    A child model's list, scoped to one parent - the body of one tab on the
    parent's page. Pair with `wise_core/generic/parent_child_list_generic.html`.
    """
    parent_field = 'parent_id'
    ordering = ['pk']

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_create_url(self):
        """`create_url_name` reversed under this parent - a child record is
        only ever created inside the parent whose tab you are looking at."""
        if not self.create_url_name:
            return None
        return reverse(
            self.create_url_name,
            kwargs={self.parent_pk_url_kwarg: self.get_parent_object().pk},
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.get_parent_context_data())
        return context


class WiseParentDetailChildCreateView(ParentObjectMixin, ChildTabsMixin, WiseCreateView):
    """
    Add a child under one parent. The parent comes from the URL, never from
    a form field, so it cannot be reassigned by posting a different value.
    Pair with `wise_core/generic/parent_child_form_generic.html`.
    """
    parent_field = 'parent_id'
    success_message = _('Record added successfully')

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def form_valid(self, form):
        setattr(form.instance, self.parent_field, self.kwargs[self.parent_pk_url_kwarg])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_parent_context_data())
        return context

    def get_success_url(self):
        return self.get_child_list_url() or super().get_success_url()


class WiseParentDetailChildUpdateView(ParentObjectMixin, ChildTabsMixin, WiseUpdateView):
    """
    Edit one child of one parent. Pair with
    `wise_core/generic/parent_child_form_generic.html`.
    """
    parent_field = 'parent_id'
    success_message = _('Record updated successfully')

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_parent_context_data())
        return context

    def get_success_url(self):
        return self.get_child_list_url() or super().get_success_url()


class WiseParentDetailChildDeleteView(ParentObjectMixin, ChildTabsMixin, WiseDeleteView):
    """
    Delete one child of one parent. Pair with
    `wise_core/generic/parent_child_confirm_generic.html`.
    """
    parent_field = 'parent_id'
    success_message = _('Record deleted successfully')

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_parent_context_data())
        return context

    def get_success_url(self):
        return self.get_child_list_url() or super().get_success_url()


class WiseParentDetailChildDetailView(ParentObjectMixin, ChildTabsMixin, WiseDetailView):
    """
    One child record, still inside the parent's chrome and tab bar. Pair
    with `wise_core/generic/parent_child_detail_generic.html`.
    """
    parent_field = 'parent_id'

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_parent_context_data())
        return context


class WiseImageGalleryMixin(ContextMixin):
    """
    Puts a record's images into the context as `gallery`, ready for
    `wise_core/components/_image_gallery.html`: one large image the visitor
    swipes through, a strip of clickable thumbnails beneath it on tablet and
    desktop, and page-indicator dots in their place on a phone::

        class ProductDetailView(WiseImageGalleryMixin, WiseDetailView):
            model = Product
            gallery_images = 'images'          # product.images.all()
            gallery_image_field = 'image'      # ProductImage.image
            gallery_alt_field = 'alt_text'     # ProductImage.alt_text
            gallery_ordering = ('position', 'pk')

        {% include 'wise_core/components/_image_gallery.html' %}

    The images hang off `get_gallery_object()` - the detail view's `object`
    by default - so this works under any single-object view, including the
    parent/child ones. Which image shows first comes from the query string
    (`?image=3`, 1-based), so a link can point at one photo; a missing or
    out-of-range value falls back to the first.

    Attributes:

    `gallery_images`
        Where the images live on the record: the name of a related manager
        (`'images'` -> `record.images.all()`), of a plain attribute or
        property returning an iterable, or a callable taking the record.
    `gallery_image_field`, `gallery_thumbnail_field`, `gallery_alt_field`
        The field (or callable) each image's full-size file, thumbnail and
        alt text are read from. No thumbnail field reuses the full-size
        image; no alt text falls back to `str(record)`.
    `gallery_ordering`
        Applied to a related manager's queryset with `order_by()`, so the
        gallery order doesn't depend on the image model's `Meta.ordering`.
    `gallery_query_param`
        The query parameter carrying the image to show first. None turns it off.
    `gallery_aspect_ratio`, `gallery_fit`, `gallery_thumbnail_position`
        The stage's shape (`'1 / 1'`), how a photo fills it (`'contain'` or
        `'cover'`) and where the thumbnails sit on large screens (`'bottom'`
        or `'start'`, a vertical rail). See `wise_core.gallery`.
    `gallery_label`
        The gallery's accessible name.
    `gallery_context_name`
        The context variable to fill - change it to show two galleries on
        one page, then `{% include ... with gallery=other_gallery %}`.
    """
    gallery_images = 'images'
    gallery_image_field = 'image'
    gallery_thumbnail_field = None
    gallery_alt_field = None
    gallery_ordering = None
    gallery_query_param = 'image'
    gallery_aspect_ratio = '1 / 1'
    gallery_fit = 'contain'
    gallery_thumbnail_position = 'bottom'
    gallery_label = _('Images')
    gallery_context_name = 'gallery'

    def get_gallery_object(self):
        """The record whose images the gallery shows."""
        record = getattr(self, 'object', None)
        if record is None:
            raise ImproperlyConfigured(
                '%s has no `object` to read gallery images from; '
                'override get_gallery_object().' % self.__class__.__name__
            )
        return record

    def get_gallery_images(self, record):
        """The record's images, in gallery order."""
        source = self.gallery_images
        if source is None:
            raise ImproperlyConfigured(
                '%s needs `gallery_images` (or get_gallery_images()) to find its images.'
                % self.__class__.__name__
            )
        images = source(record) if callable(source) else getattr(record, source)
        if hasattr(images, 'all'):
            # A related manager or queryset.
            images = images.all()
            if self.gallery_ordering:
                images = images.order_by(*self.gallery_ordering)
        return images or ()

    def get_gallery_selected(self):
        """The 1-based image to show first, as the visitor asked for it (unvalidated)."""
        if not self.gallery_query_param:
            return 1
        return self.request.GET.get(self.gallery_query_param, 1)

    def get_gallery_id(self, record):
        """A DOM id unique to this record, e.g. `product-3-gallery`."""
        opts = getattr(record, '_meta', None)
        name = opts.model_name if opts else record.__class__.__name__.lower()
        return '{}-{}-gallery'.format(name, getattr(record, 'pk', '') or '')

    def get_gallery_default_alt(self, record):
        """Alt text for an image that has none of its own."""
        return str(record)

    def get_gallery(self):
        record = self.get_gallery_object()
        return build_image_gallery(
            self.get_gallery_images(record),
            gallery_id=self.get_gallery_id(record),
            label=self.gallery_label,
            image_field=self.gallery_image_field,
            thumbnail_field=self.gallery_thumbnail_field,
            alt_field=self.gallery_alt_field,
            default_alt=self.get_gallery_default_alt(record),
            selected=self.get_gallery_selected(),
            aspect_ratio=self.gallery_aspect_ratio,
            fit=self.gallery_fit,
            thumbnail_position=self.gallery_thumbnail_position,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.gallery_context_name] = self.get_gallery()
        return context


class ConfirmActionMixin:
    """A POST-only "do this one thing to the object" action, e.g. cancel/approve/archive."""
    success_url = None
    action = ''
    action_name = _('Not set')

    def do_action(self, request, *args, **kwargs):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        return self.do_action(request, *args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        raise ImproperlyConfigured('No URL to redirect to. Provide a success_url.')


class BaseConfirmActionView(ConfirmActionMixin, BaseDetailView):
    """Requires subclassing with a response mixin - see WiseConfirmActionView."""


class WiseConfirmActionView(OwnRecordsMixin, LoginRequiredMixin, PermissionRequiredMixin,
                             SuccessMessageMixin, SingleObjectTemplateResponseMixin,
                             BaseConfirmActionView):
    """
    Confirm-and-act view: `self.action` names an instance method taking the
    acting user (e.g. `object.cancel(request.user)`); permission is derived
    as `<app_label>.<action>_<model_name>`, so add a matching entry to the
    model's `Meta.permissions` for actions that aren't the default
    add/change/delete/view four.
    """
    template_name = 'wise_core/generic/confirm_action_generic.html'
    login_url = reverse_lazy('login')
    success_url = None
    success_message = _('Action completed successfully')

    def do_action(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            action = getattr(self.object, self.action)
            action(self.request.user)
            messages.success(
                request,
                _('The action "%(action_name)s" was completed successfully') % {'action_name': self.action_name},
            )
            return HttpResponseRedirect(self.get_success_url())
        except ValidationError as e:
            for msg in e.messages:
                messages.error(request, msg)
            return render(request, self.template_name, self.get_context_data())

    def get_permission_required(self):
        return (permission_codename(self.model, self.action),)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_name'] = self.action_name
        context['action'] = self.action
        context['model'] = self.model
        context['model_name'] = self.model._meta.model_name
        context['model_app_label'] = self.model._meta.app_label
        return context
