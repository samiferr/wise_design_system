from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .appearance import appearance_changed, get_query_param, is_valid_appearance, persist_appearance


@require_POST
def set_appearance(request):
    """
    Switch the visitor's appearance - Django's ``set_language`` for the
    design language. POST ``appearance`` (one of ``WISE_APPEARANCES``) and an
    optional ``next`` URL::

        <form action="{% url 'wise_set_appearance' %}" method="post">
            {% csrf_token %}
            <input type="hidden" name="next" value="{{ request.get_full_path }}">
            <button name="appearance" value="tangerine">Tangerine</button>
        </form>

    The choice is stored in the appearance cookie (and the session, if
    enabled) and ``appearance_changed`` is sent, so a project can also save
    it on the user. A form post redirects to ``next`` (or the referrer, or
    ``/``); a ``fetch()`` with ``Accept: application/json`` - or any request
    without a usable redirect target and ``X-Requested-With`` set - gets a
    204 instead, for switching without a reload.
    """
    appearance = request.POST.get('appearance', '')
    if not is_valid_appearance(appearance):
        return HttpResponseBadRequest('Unknown appearance.')

    wants_no_redirect = (
        'application/json' in request.headers.get('Accept', '')
        or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )
    if wants_no_redirect:
        response = HttpResponse(status=204)
    else:
        response = HttpResponseRedirect(_safe_next_url(request))

    persist_appearance(request, response, appearance)
    request.appearance = appearance
    appearance_changed.send(sender=set_appearance, request=request, appearance=appearance)
    return response


def _safe_next_url(request):
    for candidate in (request.POST.get('next'), request.GET.get('next'), request.headers.get('Referer')):
        if candidate and url_has_allowed_host_and_scheme(
            candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
        ):
            return _without_query_param(candidate)
    return '/'


def _without_query_param(url):
    # A `next` that still says ?appearance=lumen would override the choice
    # just made (the query parameter outranks the cookie), so drop it.
    param = get_query_param()
    if not param:
        return url
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != param]
    return urlunsplit(parts._replace(query=urlencode(query)))
