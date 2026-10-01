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


def _relative_luminance(red, green, blue):
    """WCAG 2.x relative luminance of an sRGB color given as 0-255 channels."""
    def linear(channel):
        channel /= 255
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    return 0.2126 * linear(red) + 0.7152 * linear(green) + 0.0722 * linear(blue)


@register.filter
def on_color(value):
    """
    `#000000` or `#ffffff`, whichever reads better on the CSS hex color `value`.

    For a color the user chose (a category swatch, a tag color) - text on it can't use a fixed
    design token, since the background isn't one. Picks the higher WCAG contrast of the two, which
    is always at least 4.58:1. Anything that isn't `#rgb` / `#rrggbb` falls back to white.

        <span style="background: {{ category.color }}; color: {{ category.color|on_color }}">A</span>
    """
    color = str(value or '').strip().lstrip('#')
    if len(color) == 3:
        color = ''.join(char * 2 for char in color)
    try:
        red, green, blue = (int(color[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return '#ffffff'
    if len(color) != 6:
        return '#ffffff'
    luminance = _relative_luminance(red, green, blue)
    # Contrast with black is (L + 0.05) / 0.05, with white 1.05 / (L + 0.05): black wins above L ~ 0.179.
    return '#000000' if luminance > 0.179 else '#ffffff'


@register.filter
def startswith(value, prefix):
    """
    `{% if request.resolver_match.url_name|startswith:"invoice_" %}`.

    Used by the sidebar to decide which nav item is the selected one. Prefix
    rather than substring: with children nested under a parent, an
    `order_line_list_view` URL contains `line_` *and* `order_`, so a
    substring test lights up two sections at once.
    """
    return str(value).startswith(str(prefix))


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


@register.simple_tag(takes_context=True)
def page_url(context, number):
    """
    Build the `?page=` URL for one pager link, preserving every other query
    parameter - the `?view=table` mode, the active sort and the filters - so
    paging never drops them. Used by `wise_core/components/_pagination.html`.
    """
    params = context['request'].GET.copy()
    params['page'] = number
    return '?' + params.urlencode()


@register.filter
def page_window(page_obj, siblings=1):
    """
    The numbered buttons of a pager, as Lumen's Pagination component lays
    them out: every page when there are at most `5 + 2 * siblings` of them,
    otherwise the first, the last and the current page with `siblings` pages
    either side, and `None` wherever a gap (an ellipsis) goes -
    `{% for item in page_obj|page_window %}`.
    """
    siblings = int(siblings)
    page, count = page_obj.number, page_obj.paginator.num_pages
    if count <= 5 + 2 * siblings:
        return list(range(1, count + 1))
    left, right = max(page - siblings, 2), min(page + siblings, count - 1)
    if page <= siblings + 3:
        left, right = 2, 2 * siblings + 3
    elif page >= count - siblings - 2:
        left, right = count - (2 * siblings + 2), count - 1
    items = [1]
    if left > 2:
        items.append(None)
    items.extend(range(left, right + 1))
    if right < count - 1:
        items.append(None)
    items.append(count)
    return items


@register.simple_tag
def get_url_for_model(model_name, action, *args, **kwargs):
    """
    Build a CRUD URL from a model name and action, given the
    `{model_name}_{action}` URL-naming convention WiseListView's siblings
    use (e.g. `list`, `detail`, `create`, `update`, `delete`):
    `{% get_url_for_model "invoice" "detail" pk=object.pk %}`.
    """
    return reverse('{}_{}'.format(model_name, action), kwargs=kwargs, args=args)
