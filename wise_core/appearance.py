"""
Appearances: whole alternative design languages a visitor can switch between.

Lumen (the default, everything in ``tokens.css``) and Tangerine
(``css/appearances/tangerine.css``) ship with wise_core. An appearance is one
attribute on ``<html>`` - ``data-appearance="tangerine"`` - which re-points the
system tokens every component reads, so templates never change.

This module is the single place that knows which appearances exist and how a
request's appearance is chosen. The pieces that use it:

* ``wise_core.middleware.AppearanceMiddleware`` sets ``request.appearance``
  (and persists a ``?appearance=`` query parameter as a cookie);
* ``wise_core.context_processors.appearance`` exposes it to templates, where
  ``wise_core/base.html`` renders it on ``<html>`` before first paint;
* ``wise_core.views.set_appearance`` (``wise_core.urls``) is the POST endpoint
  a switcher form talks to; ``wiseSetAppearance()`` in common.js is the
  no-reload equivalent.

Settings (all optional)::

    WISE_APPEARANCES = [('lumen', 'Lumen'), ('tangerine', 'Tangerine')]
    WISE_DEFAULT_APPEARANCE = 'lumen'
    WISE_APPEARANCE_COOKIE_NAME = 'wise_appearance'
    WISE_APPEARANCE_COOKIE_AGE = 60 * 60 * 24 * 365      # seconds
    WISE_APPEARANCE_QUERY_PARAM = 'appearance'          # None turns it off
    WISE_APPEARANCE_SESSION_KEY = 'wise_appearance'     # None turns it off
    WISE_APPEARANCE_RESOLVER = None   # 'myapp.prefs.appearance_for' (see below)

``WISE_APPEARANCE_RESOLVER`` is a dotted path to ``callable(request) -> str |
None``, consulted after the cookie and session and before the default - the
hook for a preference stored on the user's profile. Pair it with the
``appearance_changed`` signal to save that preference. See
docs/appearances.md.
"""
from django.conf import settings
from django.dispatch import Signal
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

DEFAULT_APPEARANCES = (
    ('lumen', _('Lumen')),
    ('tangerine', _('Tangerine')),
)

# Sent by set_appearance() after a visitor picks an appearance, with
# `request` and `appearance` as keyword arguments. Connect a receiver to
# persist the choice somewhere longer-lived than a cookie (a user profile).
appearance_changed = Signal()


def get_appearances():
    """The ``(value, label)`` pairs a visitor can choose from, in order."""
    return [tuple(choice) for choice in getattr(settings, 'WISE_APPEARANCES', DEFAULT_APPEARANCES)]


def get_appearance_values():
    return [value for value, _label in get_appearances()]


def get_default_appearance():
    values = get_appearance_values()
    default = getattr(settings, 'WISE_DEFAULT_APPEARANCE', 'lumen')
    if default in values:
        return default
    return values[0] if values else 'lumen'


def is_valid_appearance(value):
    return bool(value) and value in get_appearance_values()


def get_cookie_name():
    return getattr(settings, 'WISE_APPEARANCE_COOKIE_NAME', 'wise_appearance')


def get_cookie_age():
    return getattr(settings, 'WISE_APPEARANCE_COOKIE_AGE', 60 * 60 * 24 * 365)


def get_query_param():
    return getattr(settings, 'WISE_APPEARANCE_QUERY_PARAM', 'appearance')


def get_session_key():
    return getattr(settings, 'WISE_APPEARANCE_SESSION_KEY', 'wise_appearance')


def _resolve_from_hook(request):
    path = getattr(settings, 'WISE_APPEARANCE_RESOLVER', None)
    if not path:
        return None
    resolver = import_string(path) if isinstance(path, str) else path
    return resolver(request)


def get_appearance_from_request(request):
    """
    The appearance this request should render in, first match wins:

    1. ``?appearance=<value>`` (when ``WISE_APPEARANCE_QUERY_PARAM`` is set) -
       handy for links and screenshots; the middleware also persists it;
    2. the appearance cookie (written by ``set_appearance`` and by
       ``wiseSetAppearance()`` in the browser);
    3. the session (when ``WISE_APPEARANCE_SESSION_KEY`` is set);
    4. ``WISE_APPEARANCE_RESOLVER(request)`` - e.g. a user-profile field;
    5. ``WISE_DEFAULT_APPEARANCE``.

    Unknown values are ignored at every step, so a stale cookie for an
    appearance a project has since removed falls through to the default.
    """
    param = get_query_param()
    if param:
        value = request.GET.get(param)
        if is_valid_appearance(value):
            return value

    value = request.COOKIES.get(get_cookie_name())
    if is_valid_appearance(value):
        return value

    session_key = get_session_key()
    session = getattr(request, 'session', None)
    if session_key and session is not None:
        value = session.get(session_key)
        if is_valid_appearance(value):
            return value

    value = _resolve_from_hook(request)
    if is_valid_appearance(value):
        return value

    return get_default_appearance()


def persist_appearance(request, response, appearance):
    """Store ``appearance`` in the cookie (and the session, if enabled)."""
    response.set_cookie(
        get_cookie_name(),
        appearance,
        max_age=get_cookie_age(),
        path='/',
        samesite='Lax',
        secure=request.is_secure(),
    )
    session_key = get_session_key()
    session = getattr(request, 'session', None)
    if session_key and session is not None:
        session[session_key] = appearance
