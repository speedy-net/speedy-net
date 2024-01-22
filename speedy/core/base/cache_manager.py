import time

from django.conf import settings as django_settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.translation import get_language

DEFAULT_VALUE = object()

USE_CACHE = True


def cache_get(key, default=None, version=None, sliding_timeout=None):
    """
    :type key: str
    :type default: object
    :type version: int
    :type sliding_timeout: int
    """
    if (not (USE_CACHE)):
        return None

    wrapped_value = cache.get(key=key, default=DEFAULT_VALUE, version=version)
    if (wrapped_value is DEFAULT_VALUE):
        return default

    if ((wrapped_value.get('site_id') != django_settings.SITE_ID) or (wrapped_value.get('language') != get_language())):
        return default

    if (wrapped_value['expire_time'] is not None) and (sliding_timeout):
        if (sliding_timeout == DEFAULT_TIMEOUT):
            sliding_timeout = cache.default_timeout
        now = time.time()
        ttl = wrapped_value['expire_time'] - now
        if (ttl < sliding_timeout):
            cache_set(key, wrapped_value['value'], timeout=sliding_timeout, version=version)

    return wrapped_value['value']


def cache_get_or_set(key, default, timeout=DEFAULT_TIMEOUT, version=None):
    """
    :type key: str
    :type default: object
    :type timeout: int
    :type version: int
    """
    if (not (USE_CACHE)):
        return None

    wrapped_default = _wrap(value=default, timeout=timeout)
    wrapped_value = cache.get_or_set(key=key, default=wrapped_default, timeout=timeout, version=version)
    return wrapped_value['value']


def cache_set(key, value, timeout=DEFAULT_TIMEOUT, version=None):
    """
    :type key: str
    :type value: object
    :type timeout: int
    :type version: int
    """
    if (not (USE_CACHE)):
        return

    wrapped_value = _wrap(value=value, timeout=timeout)
    return cache.set(key=key, value=wrapped_value, timeout=timeout, version=version)


def cache_delete_many(keys, version=None):
    """
    :type keys: list[str]
    :type version: int
    """
    cache.delete_many(keys=keys, version=version)


def _wrap(value, timeout):
    expire_time = None
    if (timeout is not None):
        if (timeout == DEFAULT_TIMEOUT):
            timeout = cache.default_timeout
        now = time.time()
        expire_time = now + timeout

    wrapped_value = {
        'value': value,
        'expire_time': expire_time,
        'site_id': django_settings.SITE_ID,
        'language': get_language(),
    }
    return wrapped_value


