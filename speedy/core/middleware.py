from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render
from django.utils import translation


def redirect_to_www(request, site):
    url = '//www.{domain}{path}'.format(
        domain=site.domain,
        path="/",
    )
    return HttpResponsePermanentRedirect(url)


def language_selector(request):
    translation.activate('en')
    request.LANGUAGE_CODE = translation.get_language()
    return render(request, 'welcome.html')


class LocaleDomainMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.META.get('HTTP_HOST', '')
        site = Site.objects.get_current()

        for lang_code, lang_name in settings.LANGUAGES:
            if (domain == "{lang_code}.{domain}".format(lang_code=lang_code, domain=site.domain)):
                translation.activate(lang_code)
                request.LANGUAGE_CODE = translation.get_language()
                return self.get_response(request=request)

        if domain != "www.{domain}".format(domain=site.domain, path="/"):
            for other_site in Site.objects.exclude(id=1):
                # "Speedy Mail Software" → "mail"
                other_site_part = other_site.name.split()[1].lower()
                if other_site_part in domain:
                    return redirect_to_www(request=request, site=other_site)
            return redirect_to_www(request=request, site=site)

        return language_selector(request=request)
