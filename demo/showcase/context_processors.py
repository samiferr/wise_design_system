from django.conf import settings

from . import navigation


def site_chrome(request):
    """
    Branding that varies by which of the two showcase surfaces the request
    is in - the documentation site (/docs/) and the demo app (/demo/) are
    deliberately kept apart (separate URL prefix, separate nav, separate
    chrome), and a distinct `project_name` is the one piece of that split
    every page picks up automatically through `wise_core/base.html` and
    `wise_core/components/topbar.html` (both read `project_name` already).
    """
    project_name = 'Wise Demo App' if request.path.startswith('/demo/') else settings.PROJECT_NAME
    return {'project_name': project_name}


def docs_nav(request):
    """
    Exposes the documentation tree (navigation.DOCS_NAV) to every template,
    enriched with the URL name each page resolves to so the sidebar tree can
    link to it with a plain {% url %}.

    Which node is *selected* is decided in the template by comparing against
    `current_section_slug`/`current_page_slug`, which DocPageView puts in the
    context - the tree renders unselected on non-docs pages.
    """
    tree = [
        {
            'title': section['title'],
            'slug': section['slug'],
            'icon': section.get('icon', 'chevron-right'),
            'items': [
                {
                    'title': item['title'],
                    'slug': item['slug'],
                    'url_name': (
                        f"docs_{section['slug'].replace('-', '_')}"
                        f"_{item['slug'].replace('-', '_')}"
                    ),
                }
                for item in section['items']
            ],
        }
        for section in navigation.DOCS_NAV
    ]
    return {'docs_nav': tree}
