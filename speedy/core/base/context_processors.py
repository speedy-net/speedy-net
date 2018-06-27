from django.utils.translation import ugettext_lazy as _
from django.conf import settings as dj_settings
from django.contrib.sites.models import Site
from django.utils.translation import get_language


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
    site = Site.objects.get_current()
    if hasattr(dj_settings, 'SITE_TITLE'):
        site_title = dj_settings.SITE_TITLE
    else:
        site_title = _(site.name)
    return {
        'site': site,
        'site_name': _(site.name),
        'site_title': site_title,
        'sites': Site.objects.all().order_by('pk'),
    }


def speedy_net_url(request):
    SPEEDY_NET_SITE_ID = dj_settings.SITE_PROFILES.get('net').get('site_id')
    SPEEDY_NET_URL = Site.objects.get(id=SPEEDY_NET_SITE_ID).domain
    return {
        'SPEEDY_NET_URL': SPEEDY_NET_URL,
    }


def speedy_match_url(request):
    SPEEDY_MATCH_SITE_ID = dj_settings.SITE_PROFILES.get('match').get('site_id')
    SPEEDY_MATCH_URL = Site.objects.get(id=SPEEDY_MATCH_SITE_ID).domain
    return {
        'SPEEDY_MATCH_URL': SPEEDY_MATCH_URL,
    }


