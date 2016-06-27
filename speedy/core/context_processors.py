from django.conf import settings as dj_settings


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

