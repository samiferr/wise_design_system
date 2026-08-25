from django.conf import settings


def nav(request):
    """
    Feeds `wise_core/components/nav_menu.html` from a plain Python setting
    instead of hardcoding a project's menu into the design system's own
    templates. See docs/getting-started.md for the shape of
    `WISE_NAV_SECTIONS`.
    """
    return {'wise_nav_sections': getattr(settings, 'WISE_NAV_SECTIONS', [])}
