import time

from pymemcache.client.murmur3 import murmur3_32
from django.utils import log

from speedy.core.base import cache_manager

CACHE_TYPES = {
    'mail_admins': 'speedy-core-base-log-mail-admins-{subject}',
}

MAIL_ADMINS_COOLDOWN_PERIOD = 3600  # 1 hour


def cache_key(cache_type, subject):
    """
    Build the cache key for a particular type of cached value.

    :param cache_type: Required. One of the keys of CACHE_TYPES.
    :param subject: Required. The subject of the log message.
    :return: A cache key.
    """
    return CACHE_TYPES[cache_type].format(subject=murmur3_32(data=subject))


class AdminEmailHandler(log.AdminEmailHandler):
    COUNT_FORMAT = 'Number in the last hour: {}'
    COUNT_HTML_FORMAT = '<p>{}</p>'.format(COUNT_FORMAT)

    def _should_send_mail(self, subject):
        """
        Returns whether to send mail or not, and the number of times the subject was logged in the last hour.
        If this is a WARNING message, it will be sent by mail only once per hour.
        Some specific messages are never sent by mail.

        :param subject: Required. The subject of the log message.
        :return: (should_send_mail (bool), count_last_hour (int, >= 1))
        """
        if (subject == "INFO: Found credentials in shared credentials file: ~/.aws/credentials"):
            return False, 1

        if (subject.startswith("WARNING (EXTERNAL IP): Not Found: ")):
            return False, 1

        if (not ((subject.startswith('WARNING')) or (subject.startswith('ERROR: get_ip_address_ipapi_info::')) or (subject.startswith('ERROR: is_active_and_valid::')))):
            return True, 1

        try:
            mail_admins_key = cache_key(cache_type='mail_admins', subject=subject)
            now = time.time()
            value = {
                'cooldown_start_time': now,
                'cooldown_count': 0,
                'cooldown_timestamps': [],
            }
            cached_value = cache_manager.cache_get_or_set(key=mail_admins_key, default=value, timeout=MAIL_ADMINS_COOLDOWN_PERIOD)
            # count = cached_value['cooldown_count'] + 1
            count_last_hour = sum(1 for timestamp in cached_value['cooldown_timestamps'] if (now - timestamp < MAIL_ADMINS_COOLDOWN_PERIOD)) + 1
            if (cached_value == value):
                # Not in cooldown period
                should_send_mail = True
            else:
                # Consider adding lock
                if (now - cached_value['cooldown_start_time'] >= MAIL_ADMINS_COOLDOWN_PERIOD):
                    # Cooldown period passed, reset cooldown period
                    should_send_mail = True
                    cache_manager.cache_set(key=mail_admins_key, value=value, timeout=MAIL_ADMINS_COOLDOWN_PERIOD)
                else:
                    # Still in cooldown period, update cooldown count
                    should_send_mail = False
                    cached_value['cooldown_count'] += 1
                    cached_value['cooldown_timestamps'].append(now)
                    cache_manager.cache_set(key=mail_admins_key, value=cached_value, timeout=MAIL_ADMINS_COOLDOWN_PERIOD)
            return should_send_mail, count_last_hour
        except Exception:
            return True, 1

    def send_mail(self, subject, message, *args, **kwargs):
        """
        Override to send mail only once per hour for WARNING messages.
        If this is a WARNING message, it will be sent by mail only once per hour.
        Some specific messages are never sent by mail.

        :param subject: Required. The subject of the log message.
        :param message: Required. The message of the log message.
        :param args: Optional. Positional arguments.
        :param kwargs: Optional. Keyword arguments.
        :return: None.
        """
        should_send_mail, count = self._should_send_mail(subject=subject)
        if (should_send_mail):
            if (count > 1):
                message = '{}\n\n{}'.format(self.COUNT_FORMAT.format(count), message)
                if ('html_message' in kwargs):
                    kwargs['html_message'] = kwargs['html_message'].replace('<body>\n', '<body>\n{}\n'.format(self.COUNT_HTML_FORMAT.format(count)))
            super().send_mail(subject, message, *args, **kwargs)


