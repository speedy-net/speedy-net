import random

from django.conf import settings as django_settings

if (django_settings.TESTS):
    import copy
    import logging.config
    from datetime import date, datetime
    from dateutil.relativedelta import relativedelta

    from django.core.signals import setting_changed
    from django.dispatch import receiver

    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.utils import get_random_user_password


    class TestsDynamicSettings(object):
        @staticmethod
        def valid_date_of_birth_list(max_age_allowed):
            today = date.today()
            end_of_tests_date = (datetime.now() + relativedelta(hours=1.5)).date()
            valid_date_of_birth_list = [
                '1904-02-29',
                '1980-01-31',
                '1980-02-29',
                '1999-12-01',
                '1999-12-31',
                '2000-01-01',
                '2000-02-28',
                '2000-02-29',
                '2001-02-28',
                '2004-02-29',
                '2018-10-15',
                '2019-01-01',
                '{}-01-01'.format(today.year + 1 - max_age_allowed),
                '{}-12-31'.format(today.year + 1 - max_age_allowed),
                '{}-01-01'.format(today.year),
                '{}-01-01'.format(today.year - 1),
                '{}-12-31'.format(today.year - 1),
                today.isoformat(),
                (today - relativedelta(days=1)).isoformat(),
                (end_of_tests_date - relativedelta(years=max_age_allowed) + relativedelta(days=1)).isoformat(),
            ]
            valid_date_of_birth_list = sorted(list(set(valid_date_of_birth_list)))
            return valid_date_of_birth_list

        @staticmethod
        def invalid_date_of_birth_list(max_age_allowed):
            today = date.today()
            end_of_tests_date = (datetime.now() + relativedelta(hours=1.5)).date()
            invalid_date_of_birth_list = [
                '1900-02-29',
                '1901-02-29',
                '1980-02-31',
                '1980-02-99',
                '1980-02-00',
                '1980-02-001',
                '1999-00-01',
                '1999-13-01',
                '2001-02-29',
                '2025-01-01',
                '3000-01-01',
                '9999-12-31',
                '10000-01-01',
                '1768-10-01',
                '1000-01-01',
                '1-01-01',
                '100-01-01',
                '999-01-01',
                '0001-01-01',
                '0999-01-01',
                '{}-01-01'.format(end_of_tests_date.year + 1),
                '{}-12-31'.format(end_of_tests_date.year + 1),
                '{}-01-01'.format(today.year - 1 - max_age_allowed),
                '{}-12-31'.format(today.year - 1 - max_age_allowed),
                (end_of_tests_date + relativedelta(days=1)).isoformat(),
                (today - relativedelta(years=max_age_allowed)).isoformat(),
                date(year=1, month=1, day=1).isoformat(),
                date(year=9999, month=12, day=31).isoformat(),
                (date(year=1, month=1, day=2) - relativedelta(days=1)).isoformat(),
                (date(year=9999, month=12, day=31) - relativedelta(days=1)).isoformat(),
                (date(year=9999, month=12, day=30) + relativedelta(days=1)).isoformat(),
                'a',
                '',
            ]
            invalid_date_of_birth_list = sorted(list(set(invalid_date_of_birth_list)))
            return invalid_date_of_birth_list


    SITES_FIXTURE = 'default_sites_tests.json'
    VALID_DATE_OF_BIRTH_IN_MODEL_LIST = TestsDynamicSettings.valid_date_of_birth_list(max_age_allowed=250)
    INVALID_DATE_OF_BIRTH_IN_MODEL_LIST = TestsDynamicSettings.invalid_date_of_birth_list(max_age_allowed=250)
    VALID_DATE_OF_BIRTH_IN_FORMS_LIST = TestsDynamicSettings.valid_date_of_birth_list(max_age_allowed=180)
    INVALID_DATE_OF_BIRTH_IN_FORMS_LIST = TestsDynamicSettings.invalid_date_of_birth_list(max_age_allowed=180)

    SLUGS_TO_TEST_LIST = [
        {"slug": 'a-' * 28 + 'b', "slug_length": 57},
        {"slug": 'a-' * 29, "slug_length": 57},
        {"slug": 'a-' * 29 + 'b', "slug_length": 59},
        {"slug": 'a-' * 30, "slug_length": 59},
        {"slug": 'a-' * 30 + 'b', "slug_length": 61},
        {"slug": 'a-' * 31, "slug_length": 61},
        {"slug": 'z-' * 31 + 'b', "slug_length": 63},
        {"slug": 'z-' * 32, "slug_length": 63},
    ]


    class OVERRIDE_ENTITY_SETTINGS(object):
        MIN_SLUG_LENGTH = 60


    class OVERRIDE_USER_SETTINGS(object):
        MIN_SLUG_LENGTH = 60
        MAX_NUMBER_OF_FRIENDS_ALLOWED = 4

        MIN_AGE_ALLOWED_IN_MODEL = 2  # In years.
        MAX_AGE_ALLOWED_IN_MODEL = 240  # In years.

        MIN_AGE_ALLOWED_IN_FORMS = 2  # In years.
        MAX_AGE_ALLOWED_IN_FORMS = 178  # In years.


    class OVERRIDE_SPEEDY_MATCH_SITE_PROFILE_SETTINGS(object):
        MIN_AGE_TO_MATCH_ALLOWED = 2  # In years.
        MAX_AGE_TO_MATCH_ALLOWED = 178  # In years.

        MIN_HEIGHT_TO_MATCH = 120  # In cm.
        MAX_HEIGHT_TO_MATCH = 220  # In cm.


    class OVERRIDE_LOGGING_SETTINGS(object):
        LOGGING = copy.deepcopy(django_settings.LOGGING)
        LOGGING['loggers']['speedy']['handlers'] = ['console']


    SITE_NAME_EN_DICT = {
        django_settings.SPEEDY_NET_SITE_ID: "Speedy Net",
        django_settings.SPEEDY_MATCH_SITE_ID: "Speedy Match",
        django_settings.SPEEDY_COMPOSER_SITE_ID: "Speedy Composer",
        django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: "Speedy Mail Software",
    }

    if (django_settings.LOGIN_ENABLED):
        # Generate a new random password for each test.
        USER_PASSWORD = get_random_user_password()
        # USER_PASSWORD = 'vjha9c4q44zs'

    RANDOM_LANGUAGE_CODE_CHOICE = random.choice(['de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', '__1', '__2'])


    @receiver(signal=setting_changed)
    def logging_changed(**kwargs):
        if kwargs['setting'] == 'LOGGING':
            logging.config.dictConfig(config=kwargs['value'])


