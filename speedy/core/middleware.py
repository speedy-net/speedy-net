from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch
from django.urls import reverse
from django.utils import translation
from speedy.core.settings.utils import env


def redirect_to_www(site):
    url = '//www.{domain}{path}'.format(
        domain=site.domain,
        path="/",
    )
    return redirect(to=url, permanent=True)


def language_selector(request):
    translation.activate('en')
    request.LANGUAGE_CODE = translation.get_language()
    return render(request, 'www/welcome.html')


class LocaleDomainMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.META.get('HTTP_HOST', '').lower()
        site = Site.objects.get_current()

        for lang_code, lang_name in settings.LANGUAGES:
            if (domain == "{lang_code}.{domain}".format(lang_code=lang_code, domain=site.domain)):
                translation.activate(lang_code)
                request.LANGUAGE_CODE = translation.get_language()
                return self.get_response(request=request)

        try:
            if request.path == reverse('accounts:set_session'):
                return self.get_response(request=request)
        except NoReverseMatch:
            pass

        if (not(domain == "www.{domain}".format(domain=site.domain))):
            for other_site in Site.objects.all().order_by("pk"):
                if (other_site.domain in domain):
                    return redirect_to_www(site=other_site)
            if ("match" in domain):
                other_site = Site.objects.get(pk=int(env('SPEEDY_MATCH_SITE_ID')))
                return redirect_to_www(site=other_site)
            if ("composer" in domain):
                other_site = Site.objects.get(pk=int(env('SPEEDY_COMPOSER_SITE_ID')))
                return redirect_to_www(site=other_site)
            if ("mail" in domain):
                other_site = Site.objects.get(pk=int(env('SPEEDY_MAIL_SOFTWARE_SITE_ID')))
                return redirect_to_www(site=other_site)
            other_site = Site.objects.get(pk=int(env('SPEEDY_NET_SITE_ID')))
            return redirect_to_www(site=other_site)
        elif (not(request.path == '/')):
            return redirect_to_www(site=site)

        return language_selector(request=request)


class SessionCookieDomainMiddleware(object):
    """
    Cross-domain auth.
    Overrides SESSION_COOKIE_DOMAIN setting with Site.objects.get_current().domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        site = Site.objects.get_current()
        response = self.get_response(request=request)
        if settings.SESSION_COOKIE_NAME in response.cookies:
            response.cookies[settings.SESSION_COOKIE_NAME]['domain'] = '.' + site.domain.split(':')[0]
        return response
