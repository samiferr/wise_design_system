"""
Settings for the Wise Design System demo/docs site.

This project exists to *run* the design system - see docs/getting-started.md
for how a real project wires up wise_core/wise_autocomplete/wise_richtext.
Nothing here is production configuration (SECRET_KEY, DEBUG, the SQLite
DB): it's a throwaway showcase.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent

SECRET_KEY = 'demo-insecure-secret-key-not-for-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'django_filters',
    'rest_framework',

    'wise_core',
    'wise_autocomplete',
    'wise_richtext',

    'showcase',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wise_core.context_processors.nav',
                'showcase.context_processors.docs_nav',
            ],
        },
    },
]

WSGI_APPLICATION = 'demo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []  # demo project - no password strength requirements

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
# wise_core/wise_autocomplete/wise_richtext static files are picked up
# automatically via django.contrib.staticfiles's AppDirectoriesFinder -
# no STATICFILES_DIRS entry needed for them.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

PROJECT_NAME = 'Wise Design System'

# Fed to wise_core/components/nav_menu.html by wise_core.context_processors.nav.
# See docs/getting-started.md for the shape.
# Fed to wise_core/components/nav_menu.html. The *documentation* tree is a
# separate, much deeper structure - it lives in showcase/navigation.py and is
# rendered by showcase/components/_docs_tree.html, not by nav_menu.html.
WISE_NAV_SECTIONS = [
    {
        'title': 'Documentation',
        'items': [
            {'label': 'Browse the docs', 'url_name': 'docs', 'icon': 'file-text', 'match': 'docs'},
        ],
    },
    {
        'title': 'Playground',
        'items': [
            {'label': 'Categories', 'url_name': 'category_list_view', 'icon': 'tag', 'match': 'category_'},
            {'label': 'Products', 'url_name': 'product_list_view', 'icon': 'pill', 'match': 'product_'},
        ],
    },
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
