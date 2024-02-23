from django.utils.translation import get_language, gettext_lazy as _
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
    settings_in_templates = {}
    for attr in ["SITE_ID", "SPEEDY_NET_SITE_ID", "SPEEDY_MATCH_SITE_ID", "SPEEDY_COMPOSER_SITE_ID", "SPEEDY_MAIL_SOFTWARE_SITE_ID", "XD_AUTH_SITES", "LANGUAGES_WITH_ADS", "THIS_SITE_IS_UNDER_CONSTRUCTION"]:
        if (hasattr(django_settings, attr)):
            settings_in_templates[attr] = getattr(django_settings, attr)
    return {
        'settings': settings_in_templates,
    }


def sites(request):
    site = Site.objects.get_current()
    if (hasattr(django_settings, 'SITE_TITLE')):
        site_title = django_settings.SITE_TITLE
    else:
        site_title = _(site.name)
    if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
        if (get_language() == 'en'):
            site_title = _(site.name)
    return {
        'site': site,
        'site_name': _(site.name),
        'site_title': site_title,
        'sites': Site.objects.filter(pk__in=django_settings.TEMPLATES_TOP_SITES).order_by('pk'),
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


def add_admin_user_prefix(request):
    if ((request.user.is_superuser) and (request.user.is_staff)):
        admin_user = True
        admin_user_prefix = "/admin/user"
    else:
        admin_user = False
        admin_user_prefix = ""
    return {
        'admin_user': admin_user,
        'admin_user_prefix': admin_user_prefix,
    }


