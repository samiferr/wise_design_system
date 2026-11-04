from django.utils.cache import patch_vary_headers

from .appearance import get_appearance_from_request, get_query_param, is_valid_appearance, persist_appearance


class AppearanceMiddleware:
    """
    Decides which appearance (Lumen, Tangerine, ...) a request renders in and
    puts it on ``request.appearance`` - see ``wise_core.appearance`` for the
    order the sources are read in.

    Add it after ``SessionMiddleware`` (it reads the session when one is
    there) and before anything that renders templates::

        MIDDLEWARE = [
            ...
            'django.contrib.sessions.middleware.SessionMiddleware',
            'wise_core.middleware.AppearanceMiddleware',
            ...
        ]

    A ``?appearance=tangerine`` query parameter is remembered: the response
    sets the cookie, so the rest of the visit stays in that appearance.

    Responses get ``Vary: Cookie``, because the same URL now renders
    differently per visitor - a shared cache must not hand one visitor's
    appearance to another.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.appearance = get_appearance_from_request(request)
        response = self.get_response(request)

        param = get_query_param()
        if param and is_valid_appearance(request.GET.get(param)):
            persist_appearance(request, response, request.appearance)

        patch_vary_headers(response, ('Cookie',))
        return response
