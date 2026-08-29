"""
The documentation site's information architecture.

This single list drives three things at once, so the site's structure lives in
exactly one place:

1. the sidebar tree (``showcase/components/_docs_tree.html``),
2. the URL patterns (``urls.py`` expands ``DOCS_NAV`` into one route per page),
3. the prev/next pager at the foot of every doc page.

A page's template is resolved by convention from its section + page slug:
``showcase/docs/<section>/<page>.html``. Adding a page means adding an entry
here and dropping the template in - no view or URL edit needed.
"""

DOCS_NAV = [
    {
        'title': 'Getting Started',
        'slug': 'getting-started',
        'icon': 'zap',
        'items': [
            {'title': 'Installation', 'slug': 'installation'},
            {'title': 'Usage', 'slug': 'usage'},
            {'title': 'Localization', 'slug': 'localization'},
        ],
    },
    {
        'title': 'Theming & Utilities',
        'slug': 'theming',
        'icon': 'settings',
        'items': [
            {'title': 'Overview', 'slug': 'overview'},
            {'title': 'Built-in Themes', 'slug': 'built-in-themes'},
            {'title': 'Color Palettes', 'slug': 'color-palettes'},
            {'title': 'Design Tokens', 'slug': 'design-tokens'},
            {'title': 'Customizing & Theming', 'slug': 'customizing'},
            {'title': 'CSS Utilities', 'slug': 'css-utilities'},
        ],
    },
    {
        'title': 'Actions',
        'slug': 'actions',
        'icon': 'zap',
        'items': [
            {'title': 'Button', 'slug': 'button'},
            {'title': 'Button Group', 'slug': 'button-group'},
            {'title': 'Copy Button', 'slug': 'copy-button'},
            {'title': 'Dropdown', 'slug': 'dropdown'},
        ],
    },
    {
        'title': 'Forms',
        'slug': 'forms',
        'icon': 'clipboard-list',
        'items': [
            {'title': 'Input', 'slug': 'input'},
            {'title': 'Textarea', 'slug': 'textarea'},
            {'title': 'Number Input', 'slug': 'number-input'},
            {'title': 'Select', 'slug': 'select'},
            {'title': 'Checkbox', 'slug': 'checkbox'},
            {'title': 'Radio', 'slug': 'radio'},
            {'title': 'Switch', 'slug': 'switch'},
            {'title': 'Rating', 'slug': 'rating'},
            {'title': 'OTP Input', 'slug': 'otp-input'},
            {'title': 'File Input', 'slug': 'file-input'},
            {'title': 'Color Picker', 'slug': 'color-picker'},
            {'title': 'Date Input', 'slug': 'date-input'},
            {'title': 'Date Picker', 'slug': 'date-picker'},
            {'title': 'Split Date', 'slug': 'split-date'},
            {'title': 'Time Input', 'slug': 'time-input'},
            {'title': 'Combobox', 'slug': 'combobox'},
            {'title': 'Autocomplete Input', 'slug': 'autocomplete-input'},
            {'title': 'Auto Suggest Input', 'slug': 'auto-suggest-input'},
            {'title': 'Rich Text Input', 'slug': 'rich-text-input'},
            {'title': 'Form Layout', 'slug': 'form-layout'},
        ],
    },
    {
        'title': 'Layout',
        'slug': 'layout',
        'icon': 'layout-dashboard',
        'items': [
            {'title': 'Accordion', 'slug': 'accordion'},
            {'title': 'Card', 'slug': 'card'},
            {'title': 'Dialog', 'slug': 'dialog'},
            {'title': 'Divider', 'slug': 'divider'},
            {'title': 'Drawer', 'slug': 'drawer'},
            {'title': 'Scroller', 'slug': 'scroller'},
        ],
    },
    {
        'title': 'Navigation',
        'slug': 'navigation',
        'icon': 'menu',
        'items': [
            {'title': 'Breadcrumb', 'slug': 'breadcrumb'},
            {'title': 'Pagination', 'slug': 'pagination'},
            {'title': 'Tab Group', 'slug': 'tab-group'},
            {'title': 'Tree', 'slug': 'tree'},
            {'title': 'Sidebar', 'slug': 'sidebar'},
            {'title': 'Topbar', 'slug': 'topbar'},
        ],
    },
    {
        'title': 'Feedback',
        'slug': 'feedback',
        'icon': 'info',
        'items': [
            {'title': 'Badge', 'slug': 'badge'},
            {'title': 'Tag', 'slug': 'tag'},
            {'title': 'Callout', 'slug': 'callout'},
            {'title': 'Toast', 'slug': 'toast'},
            {'title': 'Tooltip', 'slug': 'tooltip'},
            {'title': 'Progress Bar', 'slug': 'progress-bar'},
            {'title': 'Progress Ring', 'slug': 'progress-ring'},
            {'title': 'Spinner', 'slug': 'spinner'},
        ],
    },
    {
        'title': 'Media',
        'slug': 'media',
        'icon': 'image',
        'items': [
            {'title': 'Icons', 'slug': 'icons'},
            {'title': 'Avatar', 'slug': 'avatar'},
            {'title': 'Image', 'slug': 'image'},
            {'title': 'Video', 'slug': 'video'},
            {'title': 'Carousel', 'slug': 'carousel'},
            {'title': 'QR Code & Barcode', 'slug': 'qr-code'},
        ],
    },
    {
        'title': 'Data Viz',
        'slug': 'data-viz',
        'icon': 'activity',
        'items': [
            {'title': 'Data Table', 'slug': 'data-table'},
            {'title': 'Bar Chart', 'slug': 'bar-chart'},
            {'title': 'Line Chart', 'slug': 'line-chart'},
            {'title': 'Sparkline', 'slug': 'sparkline'},
            {'title': 'Pie Chart', 'slug': 'pie-chart'},
            {'title': 'Doughnut Chart', 'slug': 'doughnut-chart'},
            {'title': 'Polar Area Chart', 'slug': 'polar-area-chart'},
            {'title': 'Radar Chart', 'slug': 'radar-chart'},
            {'title': 'Scatter Chart', 'slug': 'scatter-chart'},
            {'title': 'Bubble Chart', 'slug': 'bubble-chart'},
        ],
    },
    {
        'title': 'Patterns',
        'slug': 'patterns',
        'icon': 'clipboard-list',
        'items': [
            {'title': 'Simple Data Page', 'slug': 'simple-data-page'},
            {'title': 'Parent / Child CRUD', 'slug': 'parent-child-crud'},
            {'title': 'Calendar', 'slug': 'calendar'},
        ],
    },
]


def iter_pages():
    """Yield ``(section, item)`` for every page in the tree, in nav order."""
    for section in DOCS_NAV:
        for item in section['items']:
            yield section, item


def flat_pages():
    """
    The whole tree flattened to a list of dicts, in nav order.

    Used for the prev/next pager and for the URL expansion in urls.py.
    """
    return [
        {
            'section_slug': section['slug'],
            'section_title': section['title'],
            'slug': item['slug'],
            'title': item['title'],
            'url_name': f"docs_{section['slug'].replace('-', '_')}_{item['slug'].replace('-', '_')}",
        }
        for section, item in iter_pages()
    ]


def neighbours(section_slug, page_slug):
    """Return the ``(previous, next)`` page dicts around the given page."""
    pages = flat_pages()
    for i, page in enumerate(pages):
        if page['section_slug'] == section_slug and page['slug'] == page_slug:
            return (pages[i - 1] if i > 0 else None,
                    pages[i + 1] if i + 1 < len(pages) else None)
    return None, None
