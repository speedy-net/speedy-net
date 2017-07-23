from django.utils.translation import ugettext_lazy as _
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


def speedy_net(request):
    speedy_net_id = dj_settings.SITE_PROFILES['net']['site_id']
    return {
        'speedy_net': Site.objects.get(id=speedy_net_id)
    }
