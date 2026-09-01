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
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.base import ContextMixin
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin

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
    """
    login_url = reverse_lazy('login')
    paginate_by = 20
    ordering = ['-pk']
    sortable_fields = ()

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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_sort'] = self.get_current_sort()
        context['filter_kwargs_count'] = len(
            [key for key, value in self.request.GET.items() if value != '' and key in self.filterset.filters]
        )
        context['filter_kwarg'] = self.get_label_value_filter_kwargs()
        return context

    def get_label_value_filter_kwargs(self):
        kwargs = {}
        for key, value in self.request.GET.items():
            if value != '' and key in self.filterset.filters:
                kwargs[self.filterset.filters[key].label] = value
        return kwargs


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


class WiseDeleteView(OwnRecordsMixin, LoginRequiredMixin, PermissionRequiredMixin,
                      SuccessMessageMixin, DeleteView):
    model = None
    login_url = reverse_lazy('login')

    def get_permission_required(self):
        return (permission_codename(self.model, 'delete'),)


class ParentObjectMixin(ContextMixin):
    """
    Master-detail support: resolve a parent object from `parent_pk_url_kwarg`
    in the URLconf, for a child list/create/update/delete/detail view scoped
    under it (e.g. `/orders/<parent_pk>/lines/`).
    """
    parent_model = None
    parent_pk_url_kwarg = 'parent_pk'
    paginate_by = 20

    def get_parent_object(self, queryset=None):
        if queryset is None:
            queryset = self.parent_model._default_manager.all()

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
        context = {'parent_object': self.get_parent_object()}
        context.update(kwargs)
        return context


class WiseParentDetailChildListView(ParentObjectMixin, WiseListView):
    parent_field = 'parent_id'
    ordering = ['pk']

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.get_parent_context_data())
        return context


class WiseParentDetailChildCreateView(ParentObjectMixin, WiseCreateView):
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


class WiseParentDetailChildUpdateView(ParentObjectMixin, WiseUpdateView):
    parent_field = 'parent_id'
    success_message = _('Record updated successfully')

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_parent_context_data())
        return context


class WiseParentDetailChildDeleteView(ParentObjectMixin, WiseDeleteView):
    parent_field = 'parent_id'
    success_message = _('Record deleted successfully')

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_parent_context_data())
        return context


class WiseParentDetailChildDetailView(ParentObjectMixin, WiseDetailView):
    parent_field = 'parent_id'

    def get_queryset(self):
        return super().get_queryset().filter(**{self.parent_field: self.get_parent_object()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_parent_context_data())
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
