from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sites.models import Site
from django.shortcuts import render
from django.utils import translation


def language_selector(request):
    return render(request, 'language.html')


class LocaleDomainMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.META.get('HTTP_HOST', '')

        for code, name in settings.LANGUAGES:
            if domain.startswith(code + '.'):
                translation.activate(code)
                request.LANGUAGE_CODE = translation.get_language()
                return self.get_response(request)

        translation.activate('en')
        request.LANGUAGE_CODE = translation.get_language()
        return language_selector(request)


class SharedSessionMiddleware(SessionMiddleware):
    """
    A session that is shared across multiple domains.
    Temporary disabled.
    """

    def process_response(self, request, response):
        response = super().process_response(request, response)
        if settings.SESSION_COOKIE_NAME in response.cookies:
            cookie = response.cookies[settings.SESSION_COOKIE_NAME].copy()
            sites = [{'domain': '.' + site.domain, 'id': site.id} for site in Site.objects.all()]
            sites.append({'domain': None, 'id': Site.objects.get_current().id})
            for site in sites:
                response.set_cookie(
                    key=settings.SESSION_COOKIE_NAME_TEMPLATE.format(site_id=site['id']),
                    value=getattr(cookie, 'value', ''),
                    max_age=cookie.get('max-age', None),
                    expires=cookie.get('expires', None),
                    path=cookie.get('path', '/'),
                    domain=site['domain'],
                    secure=cookie.get('secure', False),
                    httponly=cookie.get('httponly', False)
                )
        return response
