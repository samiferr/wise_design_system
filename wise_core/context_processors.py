from django.conf import settings


def nav(request):
    """
    Feeds `wise_core/components/nav_menu.html` from a plain Python setting
    instead of hardcoding a project's menu into the design system's own
    templates. See docs/getting-started.md for the shape of
    `WISE_NAV_SECTIONS`.

    `WISE_BREADCRUMBS = True` also puts the breadcrumb trail above every page
    body (`wise_core/components/_breadcrumbs.html`, built from the same
    sections); it is off by default.
    """
    return {
        'wise_nav_sections': getattr(settings, 'WISE_NAV_SECTIONS', []),
        'wise_breadcrumbs': getattr(settings, 'WISE_BREADCRUMBS', False),
    }


def appearance(request):
    """
    The current appearance and the choices, for ``wise_core/base.html`` (which
    renders ``data-appearance`` on ``<html>``) and for any switcher you build:

    * ``wise_appearance``         - e.g. ``'tangerine'``
    * ``wise_appearances``        - ``[{'value': 'lumen', 'label': 'Lumen', 'selected': True}, ...]``
    * ``wise_appearance_default`` - ``WISE_DEFAULT_APPEARANCE``
    * ``wise_appearance_cookie``  - the cookie name ``wiseSetAppearance()`` writes

    Reads ``request.appearance`` when ``AppearanceMiddleware`` is installed and
    works it out itself otherwise, so the processor alone is enough for a
    read-only site.
    """
    from .appearance import (
        get_appearance_from_request, get_appearances, get_cookie_name, get_default_appearance,
    )

    current = getattr(request, 'appearance', None) or get_appearance_from_request(request)
    return {
        'wise_appearance': current,
        'wise_appearances': [
            {'value': value, 'label': label, 'selected': value == current}
            for value, label in get_appearances()
        ],
        'wise_appearance_default': get_default_appearance(),
        'wise_appearance_cookie': get_cookie_name(),
    }
