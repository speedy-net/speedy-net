import time

from django.conf import settings as django_settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.translation import get_language

# Sentinel object returned by the cache when a key is not found, to distinguish it from a cached None.
DEFAULT_VALUE = object()

# Whether caching is enabled.
USE_CACHE = True


def cache_get(key, default=None, version=None, sliding_timeout=None):
    """
    Gets a value from the cache, returning `default` if the key is not in the cache, if the cache is disabled, or if the cached value was set for a different site or language.

    :param key: Required. The cache key.
    :type key: str
    :param default: Optional. The value to return if the key is not found in the cache. Default None.
    :type default: object
    :param version: Optional. The cache version.
    :type version: int
    :param sliding_timeout: Optional. If set, and the cached value's remaining time to live is less than this, resets the value's timeout to this value.
    :type sliding_timeout: int
    :return: The cached value, or `default` if not found.
    :rtype: object
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
            cache_set(key=key, value=wrapped_value['value'], timeout=sliding_timeout, version=version)

    return wrapped_value['value']


def cache_get_or_set(key, default, timeout=DEFAULT_TIMEOUT, version=None):
    """
    Gets a value from the cache, setting it to `default` first if the key is not already in the cache.

    :param key: Required. The cache key.
    :type key: str
    :param default: Required. The value to set and return if the key is not found in the cache.
    :type default: object
    :param timeout: Optional. The number of seconds the value should be cached for. Default DEFAULT_TIMEOUT.
    :type timeout: int
    :param version: Optional. The cache version.
    :type version: int
    :return: The cached (or newly set) value.
    :rtype: object
    """
    if (not (USE_CACHE)):
        return None

    wrapped_default = _wrap(value=default, timeout=timeout)
    wrapped_value = cache.get_or_set(key=key, default=wrapped_default, timeout=timeout, version=version)
    return wrapped_value['value']


def cache_set(key, value, timeout=DEFAULT_TIMEOUT, version=None):
    """
    Sets a value in the cache, if the cache is enabled.

    :param key: Required. The cache key.
    :type key: str
    :param value: Required. The value to cache.
    :type value: object
    :param timeout: Optional. The number of seconds the value should be cached for. Default DEFAULT_TIMEOUT.
    :type timeout: int
    :param version: Optional. The cache version.
    :type version: int
    :return: None, if the cache is disabled, otherwise the return value of the underlying cache backend's `set` method.
    """
    if (not (USE_CACHE)):
        return

    wrapped_value = _wrap(value=value, timeout=timeout)
    return cache.set(key=key, value=wrapped_value, timeout=timeout, version=version)


def cache_delete_many(keys, version=None):
    """
    Deletes several keys from the cache at once.

    :param keys: Required. A list of cache keys to delete.
    :type keys: list[str]
    :param version: Optional. The cache version.
    :type version: int
    """
    cache.delete_many(keys=keys, version=version)


def _wrap(value, timeout):
    """
    Wraps a value, along with its expiry time, the current site ID and the current language, for storage in the cache.

    :param value: Required. The value to wrap.
    :type value: object
    :param timeout: Required. The number of seconds the value should be cached for, or None for no expiry.
    :type timeout: int
    :return: A dict with keys 'value', 'expire_time', 'site_id' and 'language'.
    :rtype: dict
    """
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


