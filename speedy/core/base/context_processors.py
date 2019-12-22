from django.utils.translation import gettext_lazy as _
from django.conf import settings as django_settings
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
        'settings': django_settings,
    }


def sites(request):
    site = Site.objects.get_current()
    if (hasattr(django_settings, 'SITE_TITLE')):
        site_title = django_settings.SITE_TITLE
    else:
        site_title = _(site.name)
    return {
        'site': site,
        'site_name': _(site.name),
        'site_title': site_title,
        'sites': Site.objects.all().order_by('pk'),
    }


def speedy_net_domain(request):
    SPEEDY_NET_DOMAIN = Site.objects.get(pk=django_settings.SPEEDY_NET_SITE_ID).domain
    return {
        'SPEEDY_NET_DOMAIN': SPEEDY_NET_DOMAIN,
    }


def speedy_match_domain(request):
    SPEEDY_MATCH_DOMAIN = Site.objects.get(pk=django_settings.SPEEDY_MATCH_SITE_ID).domain
    return {
        'SPEEDY_MATCH_DOMAIN': SPEEDY_MATCH_DOMAIN,
    }


def admin_prefix(request):
    import logging
    logger = logging.getLogger(__name__)
    logger.info('admin_prefix:: request.user={request_user}, request.user.is_superuser={is_superuser}, request.user.is_staff={is_staff}'.format(request_user=request.user, is_superuser=request.user.is_superuser, is_staff=request.user.is_staff))
    if ((request.user.is_superuser) or (request.user.is_staff)):
        admin_user_prefix = "/admin/user"
    else:
        admin_user_prefix = ""
    return {
        'admin_user_prefix': admin_user_prefix,
    }


