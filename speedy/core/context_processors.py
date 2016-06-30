from django.conf import settings as dj_settings
from django.contrib.sites.models import Site


def active_url_name(request):
    components = []
    try:
        components.extend(request.resolver_match.namespaces)
        components.append(request.resolver_match.url_name)
    except AttributeError:
        pass
    return {
        'active_url_name': ':'.join(components)
    }


def settings(request):
    return {
        'settings': dj_settings,
    }


def sites(request):
    return {
        'site': request.site,
        'sites': Site.objects.all(),
    }
