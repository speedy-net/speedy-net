"""
Middleware of Speedy Core: locale by domain, session cookie domain and removal of extra slashes from URLs, and helpers for redirecting to the www domain.
"""
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
    """
    Builds a redirect response to the "www" subdomain of the given site.

    :param site: Required. The site to redirect to.
    :type site: Site
    :return: A redirect response (permanent, unless DEBUG is enabled) to the "www" subdomain of the site.
    :rtype: HttpResponseBase
    """
    url = '//www.{domain}{path}'.format(
        domain=site.domain,
        path="/",
    )
    return redirect(to=url, permanent=(not (django_settings.DEBUG)))


def show_www_template(request: HttpRequest) -> HttpResponseBase:
    """
    Activates the English language and renders the "www" welcome page.

    :param request: Required. The current request.
    :type request: HttpRequest
    :return: The rendered "www/welcome.html" page.
    :rtype: HttpResponseBase
    """
    translation.activate(language='en')
    request.LANGUAGE_CODE = translation.get_language()
    return render(request=request, template_name='www/welcome.html')


class LocaleDomainMiddleware(object):
    """
    Middleware which handles locale subdomains, lower-cases the domain, redirects legacy or unrecognized domains to the correct site, and shows the "www" welcome page for requests to the bare "www" domain.

    Methods:
        __call__: Processes the request and returns the appropriate response (the normal response, or a redirect, or the "www" welcome page).
    """

    def __init__(self, get_response):
        """
        Initializes the middleware.

        :param get_response: Required. The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        """
        Handles domain casing, locale subdomains, legacy/unrecognized domains and the "www" welcome page, redirecting or rendering as needed before delegating to the next middleware or view.

        :param request: Required. The current request.
        :type request: HttpRequest
        :return: The response from the next middleware/view in the chain, a redirect response, or the rendered "www" welcome page.
        :rtype: HttpResponseBase
        :raises Exception: If an unexpected site is determined for the domain.
        """
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
            if (request.path == reverse(viewname='accounts:set_session')):
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

    Methods:
        __call__: Processes the request and sets the session cookie's domain on the response.
    """

    def __init__(self, get_response):
        """
        Initializes the middleware.

        :param get_response: Required. The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        """
        Gets the response from the next middleware/view, then overrides the session cookie's domain with the current site's domain (if the session cookie is present in the response).

        :param request: Required. The current request.
        :type request: HttpRequest
        :return: The response from the next middleware/view in the chain, with the session cookie's domain overridden if present.
        :rtype: HttpResponseBase
        """
        site = Site.objects.get_current()
        response = self.get_response(request=request)
        if (django_settings.SESSION_COOKIE_NAME in response.cookies):
            response.cookies[django_settings.SESSION_COOKIE_NAME]['domain'] = '.' + site.domain.split(':')[0]
        return response


class RemoveExtraSlashesMiddleware(object):
    """
    Remove extra slashes from URLs.

    Methods:
        normalize_path: Collapses consecutive slashes in a path into a single slash.
        __call__: Redirects to the normalized path if it differs from the requested path, otherwise delegates to the next middleware/view.
    """

    def __init__(self, get_response):
        """
        Initializes the middleware.

        :param get_response: Required. The next middleware or view in the chain.
        """
        self.get_response = get_response

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Collapses consecutive slashes in a path into a single slash.

        :param path: Required. The path to normalize.
        :type path: str
        :return: The normalized path.
        :rtype: str
        """
        return re.sub(pattern=r'(/{2,})', repl='/', string=path)

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        """
        Redirects to the normalized path (with extra slashes removed) if it differs from the requested path, otherwise delegates to the next middleware/view.

        :param request: Required. The current request.
        :type request: HttpRequest
        :return: A redirect response to the normalized path, or the response from the next middleware/view in the chain.
        :rtype: HttpResponseBase
        """
        normalized_path = self.normalize_path(path=request.path)
        if (not (normalized_path == request.path)):
            request.path = normalized_path
            return redirect(to=request.get_full_path(), permanent=(not (django_settings.DEBUG)))
        return self.get_response(request=request)


