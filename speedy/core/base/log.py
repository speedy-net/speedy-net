import time

from pymemcache.client.murmur3 import murmur3_32
from django.utils import log

from speedy.core.base import cache_manager

CACHE_TYPES = {
    'mail_admins': 'speedy-ma-%s',
}

MAIL_ADMINS_COOLDOWN_PERIOD = 3600  # 1 hour


def cache_key(type, subject):
    return CACHE_TYPES[type] % murmur3_32(subject)


class AdminEmailHandler(log.AdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        should_send_mail, count = self._should_send_mail(subject)
        if should_send_mail:
            if count:
                message = ('Count: %s' % count) + message
            super().send_mail(subject, message, *args, **kwargs)

    def _should_send_mail(self, subject):
        if (not (subject.startswith('WARNING'))):
            return True, 0

        try:
            mail_admins_key = cache_key('mail_admins', subject)
            now = time.time()
            value = {
                'cooldown_start_time': now,
                'cooldown_count': 0,
            }
            cached_value = cache_manager.cache_get_or_set(mail_admins_key, value, timeout=MAIL_ADMINS_COOLDOWN_PERIOD)
            count = cached_value['cooldown_count']
            if (cached_value == value):
                # Not in cooldown period
                should_send_mail = True
            else:
                # Consider adding lock
                if (cached_value['cooldown_start_time'] - now >= MAIL_ADMINS_COOLDOWN_PERIOD):
                    # Cooldown period passed, reset cooldown period
                    should_send_mail = True
                    cache_manager.cache_set(mail_admins_key, value, timeout=MAIL_ADMINS_COOLDOWN_PERIOD)
                else:
                    # Still in cooldown period, update cooldown count
                    should_send_mail = False
                    cached_value['cooldown_count'] += 1
                    cache_manager.cache_set(mail_admins_key, cached_value, timeout=MAIL_ADMINS_COOLDOWN_PERIOD)
            return should_send_mail, count
        except Exception:
            return True, 0
