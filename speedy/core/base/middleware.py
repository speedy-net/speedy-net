import re

from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.shortcuts import redirect, render
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils import translation


def redirect_to_www(site: Site) -> HttpResponseBase:
    url = '//www.{domain}{path}'.format(
        domain=site.domain,
        path="/",
    )
    return redirect(to=url, permanent=(not (django_settings.DEBUG)))


def show_www_template(request: HttpRequest) -> HttpResponseBase:
    translation.activate(language='en')
    request.LANGUAGE_CODE = translation.get_language()
    return render(request=request, template_name='www/welcome.html')


class LocaleDomainMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        domain = request.META.get('HTTP_HOST', '')

        if (not (domain == domain.lower())):
            url = '//{domain}{path}'.format(
                domain=domain.lower(),
                path=request.get_full_path(),
            )
            return redirect(to=url, permanent=(not (django_settings.DEBUG)))

        site = Site.objects.get_current()

        for language_code, language_name in django_settings.LANGUAGES:
            if (domain == "{language_code}.{domain}".format(language_code=language_code, domain=site.domain)):
                translation.activate(language=language_code)
                request.LANGUAGE_CODE = translation.get_language()
                return self.get_response(request=request)

        if ((not (domain == domain.replace("-", ""))) and (site.domain == site.domain.replace("-", ""))):
            for language_code, language_name in django_settings.LANGUAGES:
                if (domain.replace("-", "") == "{language_code}.{domain}".format(language_code=language_code, domain=site.domain)):
                    url = '//{domain}{path}'.format(
                        domain=domain.replace("-", ""),
                        path=request.get_full_path(),
                    )
                    return redirect(to=url, permanent=(not (django_settings.DEBUG)))

        try:
            if (request.path == reverse('accounts:set_session')):
                return self.get_response(request=request)
        except NoReverseMatch:
            pass

        if (not (domain == "www.{domain}".format(domain=site.domain))):
            for _site in Site.objects.all().order_by("pk"):
                if (_site.domain in domain):
                    other_site = _site
                    return redirect_to_www(site=other_site)
            other_site = None
            if ("match" in domain):
                other_site = Site.objects.get(pk=django_settings.SPEEDY_MATCH_SITE_ID)
            elif ("composer" in domain):
                other_site = Site.objects.get(pk=django_settings.SPEEDY_COMPOSER_SITE_ID)
            elif ("mail" in domain):
                other_site = Site.objects.get(pk=django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)
            else:
                other_site = Site.objects.get(pk=django_settings.SPEEDY_NET_SITE_ID)
            if ((other_site is not None) and (other_site.id in [_site.id for _site in Site.objects.all().order_by("pk")])):
                return redirect_to_www(site=other_site)
            else:
                raise Exception("Unexpected: other_site={}".format(other_site))

        if (not (request.get_full_path() == '/')):
            return redirect_to_www(site=site)

        return show_www_template(request=request)


class SessionCookieDomainMiddleware(object):
    """
    Cross-domain auth.
    Overrides SESSION_COOKIE_DOMAIN setting with Site.objects.get_current().domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        site = Site.objects.get_current()
        response = self.get_response(request=request)
        if (django_settings.SESSION_COOKIE_NAME in response.cookies):
            response.cookies[django_settings.SESSION_COOKIE_NAME]['domain'] = '.' + site.domain.split(':')[0]
        return response


class RemoveExtraSlashesMiddleware(object):
    """
    Remove extra slashes from URLs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def normalize_path(path: str) -> str:
        return re.sub(pattern=r'(/{2,})', repl='/', string=path)

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        normalized_path = self.normalize_path(path=request.path)
        if (not (normalized_path == request.path)):
            request.path = normalized_path
            return redirect(to=request.get_full_path(), permanent=(not (django_settings.DEBUG)))
        return self.get_response(request=request)


