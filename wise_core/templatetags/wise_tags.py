import logging

from django import template
from django.urls import reverse

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def get_value(item, key):
    """
    Read an attribute off a model instance by name, following `__`-joined
    lookups across relations the same way the ORM does, e.g.
    `{{ invoice|get_value:"customer__company_name" }}`.

    Meant for generic templates (a datatable column list, a detail-panel
    row list) where the field name comes from a Python-side config list
    rather than being hardcoded in the template.
    """
    keys = key.split('__')
    if len(keys) > 1:
        for key in keys:
            if item is None:
                break
            item = getattr(item, key)
        return item
    return getattr(item, key)


@register.filter
def get_dict_value(item, key):
    """Look up `key` in a dict - the `dict[key]` templates can't spell directly."""
    return item[key]


@register.filter
def get_absolute_url(object_instance, field):
    """
    `{{ order|get_absolute_url:"customer" }}` -> `order.customer.get_absolute_url()`.
    Given a `__`-joined field path, resolves every segment but the last
    relation and calls `get_absolute_url()` on it.
    """
    fields = field.split('__')
    field = fields[-2] if len(fields) > 1 else field
    return getattr(object_instance, field).get_absolute_url()


@register.simple_tag
def get_field_verbose_name(obj, field_name):
    """
    `{% get_field_verbose_name object "customer__company_name" %}` -> the
    verbose_name of the *last* field in a `__`-joined lookup path, walking
    through each relation's remote model along the way. Lets a generic
    detail/list template label a column from the model's own Meta instead
    of hardcoding a label per template.
    """
    fields_list = field_name.split('__')
    if len(fields_list) > 1:
        model = obj
        last_field = fields_list.pop()
        for field in fields_list:
            model = model._meta.get_field(field).remote_field.model
        return '{} '.format(model._meta.get_field(last_field).verbose_name)
    try:
        return obj._meta.get_field(field_name).verbose_name
    except AttributeError:
        logger.error('Field %s has no verbose_name!', field_name)
        return ''


@register.simple_tag
def get_field_help_text(obj, field_name):
    """Same relation-walking lookup as get_field_verbose_name, for help_text."""
    fields_list = field_name.split('__')
    if len(fields_list) > 1:
        model = obj
        last_field = fields_list.pop()
        for field in fields_list:
            model = model._meta.get_field(field).remote_field.model
        return '{} '.format(model._meta.get_field(last_field).help_text)
    try:
        return obj._meta.get_field(field_name).help_text
    except AttributeError:
        logger.error('Field %s has no help_text!', field_name)
        return ''


@register.simple_tag
def get_model_verbose_name(obj):
    return obj._meta.verbose_name


@register.simple_tag
def get_model_verbose_name_plural(obj):
    return obj._meta.verbose_name_plural


@register.simple_tag(takes_context=True)
def sort_url(context, field):
    """
    Build the `?sort=` URL for a `.data-table` sortable header: toggles
    ascending/descending when `field` is already the active sort, defaults to
    ascending otherwise, resets pagination back to page 1, and preserves
    every other query parameter (active filters included). Pairs with
    `WiseListView.sortable_fields` and `current_sort` in the context - see
    `wise_core/components/_sortable_th.html`.
    """
    params = context['request'].GET.copy()
    params['sort'] = '-' + field if context.get('current_sort') == field else field
    params.pop('page', None)
    return '?' + params.urlencode()


@register.simple_tag
def get_url_for_model(model_name, action, *args, **kwargs):
    """
    Build a CRUD URL from a model name and action, given the
    `{model_name}_{action}` URL-naming convention WiseListView's siblings
    use (e.g. `list`, `detail`, `create`, `update`, `delete`):
    `{% get_url_for_model "invoice" "detail" pk=object.pk %}`.
    """
    return reverse('{}_{}'.format(model_name, action), kwargs=kwargs, args=args)
