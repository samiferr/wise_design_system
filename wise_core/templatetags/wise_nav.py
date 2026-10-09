"""
The app chrome that is computed rather than written: the sidebar's tree
(`nav_tree`, rendered by `wise_core/components/nav_menu.html`) and the
breadcrumb trail above a page's body (`breadcrumbs`, rendered by
`wise_core/components/_breadcrumbs.html`). Both read `WISE_NAV_SECTIONS`, so
a page's place in the app is declared once, in settings - see
docs/getting-started.md.
"""
from django import template
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import BaseCreateView, BaseDeleteView, BaseUpdateView

from wise_core.mixins import ConfirmActionMixin

register = template.Library()


def _prefixes(item):
    """An item's `match`: one url_name prefix, or a list of them."""
    match = item.get('match') or ()
    return (match,) if isinstance(match, str) else tuple(match)


def _url_name(context):
    request = context.get('request')
    match = getattr(request, 'resolver_match', None)
    return (match.url_name or '') if match else ''


def _sections(context):
    return context.get('wise_nav_sections') or getattr(settings, 'WISE_NAV_SECTIONS', [])


def _selected(sections, url_name):
    """
    (section, item) of the nav entry the current page belongs to. The longest
    matching prefix wins, so `my_profile_language` selects Language rather
    than lighting Profile (`my_profile`) as well.
    """
    best, best_length = (None, None), 0
    for section in sections:
        for item in section['items']:
            for prefix in _prefixes(item):
                if url_name.startswith(prefix) and len(prefix) > best_length:
                    best, best_length = (section, item), len(prefix)
    return best


@register.simple_tag(takes_context=True)
def nav_tree(context):
    """
    WISE_NAV_SECTIONS resolved for this request: each section gets `open`
    (it holds the current page - or, on a page that belongs to none, such as
    the dashboard, every section is open) and each item `selected`. Items
    marked `staff_only` are left out for anyone who is not a staff user.
    """
    sections = _sections(context)
    current_section, current_item = _selected(sections, _url_name(context))
    user = getattr(context.get('request'), 'user', None)
    is_staff = bool(user and user.is_active and user.is_staff)
    return [
        {
            'title': section['title'],
            'open': current_section is None or section is current_section,
            'items': [{**item, 'selected': item is current_item} for item in section['items']
                      if is_staff or not item.get('staff_only')],
        }
        for section in sections
    ]


def _crumb(label, url=None, icon=None):
    return {'label': label, 'url': url, 'icon': icon}


def _object_url(obj):
    get_url = getattr(obj, 'get_absolute_url', None)
    if not get_url:
        return None
    try:
        return get_url()
    except NoReverseMatch:
        return None


def _action_label(view):
    if isinstance(view, BaseCreateView):
        return _('New')
    if isinstance(view, BaseUpdateView):
        return _('Edit')
    if isinstance(view, BaseDeleteView):
        return _('Delete')
    if isinstance(view, ConfirmActionMixin):
        return str(view.action_name)
    return None


def _home_url():
    try:
        return reverse('home')
    except NoReverseMatch:
        return None


@register.simple_tag(takes_context=True)
def breadcrumbs(context):
    """
    Home > nav entry > parent record > child tab > record > action, each step
    only where the page has one:

      - the nav entry is the WISE_NAV_SECTIONS item the page belongs to;
      - a tabbed child page adds its parent (`parent_object`) and the tab it
        sits under (`selected_tab`, the overview tab being the parent itself);
      - a single-record page adds the record, and a create/update/delete or
        confirm-action page names the action;
      - a page outside that pattern (a profile tab) sets `breadcrumb_label`
        on its view, which replaces the record and action steps ('' for a page
        the nav entry already names, such as Settings > Company).

    The last crumb is the current page and is not a link. A page with nothing
    to show past Home (the dashboard, a logged-out page) gets no trail.
    """
    request = context.get('request')
    if request is None or not request.user.is_authenticated:
        return []
    view = context.get('view')
    crumbs = [_crumb(_('Home'), _home_url(), icon='house')]

    _section, item = _selected(_sections(context), _url_name(context))
    if item is not None:
        try:
            crumbs.append(_crumb(item['label'], reverse(item['url_name'])))
        except NoReverseMatch:
            crumbs.append(_crumb(item['label']))

    label = getattr(view, 'breadcrumb_label', None)
    if label is not None:
        # '' - the nav entry already names the page - adds no step of its own.
        if label:
            crumbs.append(_crumb(str(label)))
    else:
        parent = context.get('parent_object')
        obj = context.get('object') if isinstance(view, SingleObjectMixin) else None
        if parent is not None:
            parent_url = _object_url(parent)
            crumbs.append(_crumb(str(parent), parent_url))
            tab = context.get('selected_tab')
            if tab and tab['url'] != parent_url:
                crumbs.append(_crumb(str(tab['label']), tab['url']))
        if obj is not None and obj != parent:
            crumbs.append(_crumb(str(obj), _object_url(obj)))
        action = _action_label(view)
        if action:
            crumbs.append(_crumb(action))

    if len(crumbs) < 2:
        return []
    crumbs[-1]['url'] = None
    return crumbs
