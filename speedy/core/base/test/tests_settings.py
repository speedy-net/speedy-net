from datetime import date
from dateutil.relativedelta import relativedelta

from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.utils import get_random_user_password


class TestsDynamicSettings(object):
    @staticmethod
    def valid_date_of_birth_list(max_age_allowed):
        today = date.today()
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
            (today - relativedelta(years=max_age_allowed) + relativedelta(days=1)).isoformat(),
        ]
        valid_date_of_birth_list = sorted(list(set(valid_date_of_birth_list)))
        return valid_date_of_birth_list

    @staticmethod
    def invalid_date_of_birth_list(max_age_allowed):
        today = date.today()
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
            '{}-01-01'.format(today.year + 1),
            '{}-12-31'.format(today.year + 1),
            '{}-01-01'.format(today.year - 1 - max_age_allowed),
            '{}-12-31'.format(today.year - 1 - max_age_allowed),
            (today + relativedelta(days=1)).isoformat(),
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


if (django_settings.LOGIN_ENABLED):
    # Generate a new random password for each test.
    USER_PASSWORD = get_random_user_password()
    # USER_PASSWORD = 'vjha9c4q44zs'


