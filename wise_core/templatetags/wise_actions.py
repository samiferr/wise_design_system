"""
Actions on a record: the buttons of its detail panel and the menu on each row
of a list.

    {% load wise_actions %}

    {# inside the detail_actions block of a detail page #}
    {% record_actions object %}

    {# in a table row #}
    <td>{% row_actions item %}</td>

Both tags work out *which* actions the visitor gets (Edit and Delete behind
the model's `change` / `delete` permission, any extra action behind its own),
so a template never pairs a hand-written `{% url %}` with a
`{% if perms.app.change_model %}` of its own - and so the presentation is the
same on every page: the first action is a button, the rest are items of an
overflow menu behind a vertical-dots button (`details.dropdown.
detail-panel-overflow`), Delete last in the danger color. That keeps a detail
panel's header to one row on a phone however many actions a record has.

URLs follow the project's `<model>_update_view` / `<model>_delete_view`
naming (the one `get_url_for_model` and the generic views use) unless the
tag is given `edit_url` / `delete_url` - a child record under a tabbed parent
passes its own, since its URL carries the parent's pk too.

An extra action is a plain dict (see `ACTION_KEYS`):

    {'label': _('Approve'), 'icon': 'check', 'url': url, 'style': 'primary'}
    {'label': _('Print'), 'icon': 'printer', 'url': url, 'new_tab': True}
    # An action that changes the record when it runs is a POST form with a
    # CSRF token, never a link:
    {'label': _('Archive'), 'icon': 'folder', 'url': url, 'post': True}
    # Only for a visitor holding a permission of its own:
    {'label': _('Approve'), 'url': url, 'permission': 'billing.approve_invoice'}
"""
from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _

register = template.Library()

# What a template may read off an action.
ACTION_KEYS = (
    'label',      # the text
    'url',        # where it goes (or posts to)
    'icon',       # a lucide icon name; defaults to 'arrow-right'
    'style',      # the button style when it is the first action: 'primary', 'secondary' (default), 'danger'...
    'post',       # True: a POST form with a CSRF token instead of a link
    'name',       # a POST action's button name and value, for the view to read
    'value',
    'new_tab',    # opens in a new tab
    'danger',     # a destructive action: the danger color, kept last in the menu
    'permission', # 'app.codename' the visitor must hold, or the action is left out
)


def _reverse_or_none(name, **kwargs):
    try:
        return reverse(name, kwargs=kwargs)
    except NoReverseMatch:
        return None


def _allowed(user, action):
    permission = action.get('permission')
    return not permission or user.has_perm(permission)


def build_actions(user, obj, edit_url=None, delete_url=None, edit=True, delete=True, actions=(), more_actions=()):
    """
    The actions `user` may take on `obj`, in order: `actions` (the ones that
    come first, a workflow's transitions say), Edit, `more_actions` (an extra
    like Print), and Delete last. Each is a dict with the keys of
    `ACTION_KEYS`; Edit and Delete appear only with the model's `change` /
    `delete` permission and a URL, and so does an action with a
    `permission` of its own.
    """
    opts = obj._meta
    model_name = opts.model_name
    result = [dict(action) for action in actions or () if _allowed(user, action)]
    if edit and user.has_perm(f'{opts.app_label}.change_{model_name}'):
        url = edit_url or _reverse_or_none(f'{model_name}_update_view', pk=obj.pk)
        if url:
            result.append({'label': _('Edit'), 'icon': 'pencil', 'url': url, 'style': 'secondary'})
    result.extend(dict(action) for action in more_actions or () if _allowed(user, action))
    if delete and user.has_perm(f'{opts.app_label}.delete_{model_name}'):
        url = delete_url or _reverse_or_none(f'{model_name}_delete_view', pk=obj.pk)
        if url:
            result.append({'label': _('Delete'), 'icon': 'trash-2', 'url': url, 'style': 'outline-danger',
                           'danger': True})
    for action in result:
        action.setdefault('icon', 'arrow-right')
        action.setdefault('style', 'secondary')
    return result


@register.inclusion_tag('wise_core/components/_record_actions.html', takes_context=True)
def record_actions(context, obj, edit_url=None, delete_url=None, edit=True, delete=True, actions=None,
                   more_actions=None):
    """
    The actions of a record's detail panel - put it in the `detail_actions`
    block of `detail_generic.html` / `parent_detail_generic.html` (or a
    child's `parent_child_detail_generic.html`), and leave the page's top bar
    to the back link:

        {% block detail_actions %}{% record_actions object %}{% endblock %}

    The first action is a button; any others sit in a menu behind a
    vertical-dots button, so the panel's header never runs out of room on a
    phone. `actions` come first (a workflow's transitions, an "Approve"),
    `more_actions` between Edit and Delete (Print, Duplicate); `edit=False` /
    `delete=False` leave those out; `edit_url` / `delete_url` replace the
    conventional ones.
    """
    built = build_actions(context['request'].user, obj, edit_url=edit_url, delete_url=delete_url, edit=edit,
                          delete=delete, actions=actions, more_actions=more_actions)
    return {
        'main_action': built[0] if built else None,
        'more_actions': built[1:],
    }


@register.inclusion_tag('wise_core/components/_row_actions.html', takes_context=True)
def row_actions(context, obj, edit_url=None, delete_url=None, edit=True, delete=True, actions=None,
                more_actions=None):
    """
    The menu on a table row - a vertical-dots button opening Edit, Delete
    and whatever else the row offers, each behind its permission. It renders
    nothing when the visitor may do none of them, so the cell stays empty
    rather than holding a button that opens an empty menu:

        <th></th>                      {# an empty header: the actions column #}
        <td>{% row_actions item %}</td>

    On a phone the row is a card and this menu goes to the card's corner
    (see `.data-table`). Same arguments as `record_actions`.
    """
    built = build_actions(context['request'].user, obj, edit_url=edit_url, delete_url=delete_url, edit=edit,
                          delete=delete, actions=actions, more_actions=more_actions)
    return {'more_actions': built}
