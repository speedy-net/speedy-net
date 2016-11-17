from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import translation


def redirect_to_www(request, site):
    url = '//www.{domain}{path}'.format(
        domain=site.domain,
        path="/",
    )
    return HttpResponseRedirect(url)


def language_selector(request):
    translation.activate('en')
    request.LANGUAGE_CODE = translation.get_language()
    return render(request, 'welcome.html')


class LocaleDomainMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.META.get('HTTP_HOST', '')

        for code, name in settings.LANGUAGES:
            if domain.startswith(code + '.'):
                translation.activate(code)
                request.LANGUAGE_CODE = translation.get_language()
                return self.get_response(request=request)

        site = Site.objects.get_current()
        if (not(domain + request.path == "www.{domain}{path}".format(domain=site.domain, path="/"))):
            return redirect_to_www(request=request, site=site)

        return language_selector(request=request)


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
