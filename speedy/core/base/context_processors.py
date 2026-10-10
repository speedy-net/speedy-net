from datetime import date

from django.utils.translation import get_language, gettext_lazy as _
from django.conf import settings as django_settings
from django.contrib.sites.models import Site


def active_url_name(request):
    """
    Returns the fully qualified name of the currently resolved URL (including its namespaces), for use in templates.

    :param request: The current request.
    :return: A dict with key 'active_url_name', containing the fully qualified URL name, or an empty string if it couldn't be resolved.
    :rtype: dict
    """
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
    """
    Exposes a whitelist of Django settings to templates.

    :param request: The current request.
    :return: A dict with key 'settings', containing a dict of the whitelisted settings that are defined.
    :rtype: dict
    """
    settings_in_templates = {}
    for attr in ["SITE_ID", "SPEEDY_NET_SITE_ID", "SPEEDY_MATCH_SITE_ID", "SPEEDY_COMPOSER_SITE_ID", "SPEEDY_MAIL_SOFTWARE_SITE_ID", "XD_AUTH_SITES", "LANGUAGES_WITH_ADS", "THIS_SITE_IS_UNDER_CONSTRUCTION", "LANGUAGES_IN_HTML"]:
        if (hasattr(django_settings, attr)):
            settings_in_templates[attr] = getattr(django_settings, attr)
    return {
        'settings': settings_in_templates,
    }


def sites(request):
    """
    Exposes the current site, its translated name and title, and the list of top sites, to templates.

    :param request: The current request.
    :return: A dict with keys 'site', 'site_name', 'site_title' and 'sites'.
    :rtype: dict
    """
    site = Site.objects.get_current()
    # Speedy Net and Speedy Match are in alpha (except Speedy Match in English).
    if (hasattr(django_settings, 'SITE_TITLE')):
        site_title = django_settings.SITE_TITLE
    else:
        site_title = _(site.name)
    # Speedy Match in English is not in alpha.
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
    """
    Exposes the domain of the Speedy Net site to templates.

    :param request: The current request.
    :return: A dict with key 'SPEEDY_NET_DOMAIN', containing the domain of the Speedy Net site.
    :rtype: dict
    """
    SPEEDY_NET_DOMAIN = Site.objects.get(pk=django_settings.SPEEDY_NET_SITE_ID).domain
    return {
        'SPEEDY_NET_DOMAIN': SPEEDY_NET_DOMAIN,
    }


def speedy_match_domain(request):
    """
    Exposes the domain of the Speedy Match site to templates.

    :param request: The current request.
    :return: A dict with key 'SPEEDY_MATCH_DOMAIN', containing the domain of the Speedy Match site.
    :rtype: dict
    """
    SPEEDY_MATCH_DOMAIN = Site.objects.get(pk=django_settings.SPEEDY_MATCH_SITE_ID).domain
    return {
        'SPEEDY_MATCH_DOMAIN': SPEEDY_MATCH_DOMAIN,
    }


def add_admin_user_prefix(request):
    """
    Exposes whether the current request is from a superuser/staff admin, and the URL prefix to use for admin-only links.

    :param request: The current request.
    :return: A dict with keys 'admin_user' (bool) and 'admin_user_prefix' (str).
    :rtype: dict
    """
    admin_user = False
    admin_user_prefix = ""
    if (hasattr(request, 'user')):
        if ((request.user.is_superuser) and (request.user.is_staff)):
            admin_user = True
            admin_user_prefix = "/admin/user"
    return {
        'admin_user': admin_user,
        'admin_user_prefix': admin_user_prefix,
    }


def display_ads_today_1(request):
    """
    Determines whether to display the first set of ads today, based on the day of the month.

    :param request: The current request.
    :return: A dict with key 'display_ads_today_1', containing a bool.
    :rtype: dict
    """
    today = date.today()
    display_ads_today_1 = ((today.day % 6) in {0, 1, 3})
    return {
        'display_ads_today_1': display_ads_today_1,
    }


def display_ads_today_2(request):
    """
    Determines whether to display the second set of ads today, based on the day of the month (the complement of `display_ads_today_1`).

    :param request: The current request.
    :return: A dict with key 'display_ads_today_2', containing a bool.
    :rtype: dict
    """
    today = date.today()
    display_ads_today_2 = (not ((today.day % 6) in {0, 1, 3}))
    return {
        'display_ads_today_2': display_ads_today_2,
    }


