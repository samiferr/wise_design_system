from . import navigation


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
