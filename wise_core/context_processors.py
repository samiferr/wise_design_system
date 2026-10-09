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
