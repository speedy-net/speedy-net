import inspect
from datetime import date
# from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core.management import call_command
from django.test import override_settings, TestCase as DjangoTestCase
from django.test.runner import DiscoverRunner
from django.contrib.sites.models import Site


class SiteDiscoverRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if (not (test_labels)):
            test_labels = [label for label in settings.INSTALLED_APPS if (label.startswith('speedy.'))]
        return super().build_suite(test_labels=test_labels, extra_tests=extra_tests, **kwargs)


class SpeedyCoreDiscoverRunner(SiteDiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # We don't run tests on speedy.core
        pass


class TestsDynamicSettingsMixin(object):
    SITES_FIXTURE = 'default_sites_tests.json'
    OVERRIDE_MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED = 4

    @staticmethod
    def get_override_settings_kwargs():
        # import speedy.core.settings.tests as tests_settings  # ~~~~ TODO: remove this line!
        kwargs = dict(
            SITES_FIXTURE=__class__.SITES_FIXTURE,
            OVERRIDE_MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED=__class__.OVERRIDE_MAXIMUM_NUMBER_OF_FRIENDS_ALLOWED,
            VALID_DATE_OF_BIRTH_LIST=__class__._valid_date_of_birth_list(),
            INVALID_DATE_OF_BIRTH_LIST=__class__._invalid_date_of_birth_list(),
        )
        return kwargs

    @staticmethod
    def _valid_date_of_birth_list():
        today = date.today()
        VALID_DATE_OF_BIRTH_LIST = [
            '1904-02-29',
            '1980-01-31',
            '1999-12-01',
            '2000-02-29',
            '2004-02-29',
            '2018-10-15',
            '2019-01-01',  # ~~~~ TODO
            '3000-01-01',  # ~~~~ TODO
            '9999-12-31',  # ~~~~ TODO
            '1769-01-01',  # ~~~~ TODO
            '1768-01-01',  # ~~~~ TODO
            '1000-01-01',  # ~~~~ TODO
            '0001-01-01',  # ~~~~ TODO
            '0999-01-01',  # ~~~~ TODO
            (today + relativedelta(days=1)).isoformat(),  # ~~~~ TODO
            (today - relativedelta(years=250)).isoformat(),  # ~~~~ TODO
            today.isoformat(),  # ~~~~ TODO
            (today - relativedelta(years=250) + relativedelta(days=1)).isoformat(),  # ~~~~ TODO
            date(year=1, month=1, day=1).isoformat(),  # ~~~~ TODO
            date(year=9999, month=12, day=31).isoformat(),  # ~~~~ TODO
            (date(year=1, month=1, day=2) - relativedelta(days=1)).isoformat(),  # ~~~~ TODO
            (date(year=9999, month=12, day=31) - relativedelta(days=1)).isoformat(),  # ~~~~ TODO
            (date(year=9999, month=12, day=30) + relativedelta(days=1)).isoformat(),  # ~~~~ TODO
        ]
        print("VALID_DATE_OF_BIRTH_LIST", VALID_DATE_OF_BIRTH_LIST, len(VALID_DATE_OF_BIRTH_LIST), len(set(VALID_DATE_OF_BIRTH_LIST)))  # ~~~~ TODO
        return VALID_DATE_OF_BIRTH_LIST

    @staticmethod
    def _invalid_date_of_birth_list():
        today = date.today()
        INVALID_DATE_OF_BIRTH_LIST = [
            '1900-02-29',
            '1901-02-29',
            '1980-02-31',
            '1980-02-99',
            '1980-02-00',
            '1980-02-001',
            '1999-00-01',
            '1999-13-01',
            '2001-02-29',
            # '2018-10-16', # ~~~~ TODO
            # '2019-01-01', # ~~~~ TODO
            # '3000-01-01', # ~~~~ TODO
            # '9999-12-31', # ~~~~ TODO
            '10000-01-01',  # ~~~~ TODO
            # '1769-01-01', # ~~~~ TODO
            # '1768-01-01', # ~~~~ TODO
            # '1000-01-01', # ~~~~ TODO
            '1-01-01',
            '100-01-01',
            '999-01-01',
            # '0001-01-01', # ~~~~ TODO
            # '0999-01-01', # ~~~~ TODO
            # (today + relativedelta(days=1)).isoformat(), # ~~~~ TODO
            # (today - relativedelta(years=250)).isoformat(), # ~~~~ TODO
            # today.isoformat(), # ~~~~ TODO
            # (today - relativedelta(years=250) + relativedelta(days=1)).isoformat(), # ~~~~ TODO
            # date(year=1, month=1, day=1).isoformat(), # ~~~~ TODO
            # date(year=9999, month=12, day=31).isoformat(), # ~~~~ TODO
            # (date(year=1, month=1, day=2) - relativedelta(days=1)).isoformat(), # ~~~~ TODO
            # (date(year=9999, month=12, day=31) - relativedelta(days=1)).isoformat(), # ~~~~ TODO
            # (date(year=9999, month=12, day=30) + relativedelta(days=1)).isoformat(), # ~~~~ TODO
            'a',
            '',
        ]
        print("INVALID_DATE_OF_BIRTH_LIST", INVALID_DATE_OF_BIRTH_LIST, len(INVALID_DATE_OF_BIRTH_LIST), len(set(INVALID_DATE_OF_BIRTH_LIST)))  # ~~~~ TODO
        return INVALID_DATE_OF_BIRTH_LIST


# class TestCase(TestsDynamicSettingsMixin, DjangoTestCase):
@override_settings(**TestsDynamicSettingsMixin.get_override_settings_kwargs())
class TestCase(DjangoTestCase):
    maxDiff = None

    def _pre_setup(self):
        super()._pre_setup()
        # import speedy.core.settings.tests as tests_settings # ~~~~ TODO: remove this line!
        # call_command('loaddata', tests_settings.SITES_FIXTURE, verbosity=0) # ~~~~ TODO: remove this line!
        call_command('loaddata', settings.SITES_FIXTURE, verbosity=0)
        self.site = Site.objects.get_current()

    def validate_all_values(self):
        site_id_dict = {
            settings.SPEEDY_NET_SITE_ID: 1,
            settings.SPEEDY_MATCH_SITE_ID: 2,
            settings.SPEEDY_COMPOSER_SITE_ID: 3,
            settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 4,
        }
        domain_dict = {
            settings.SPEEDY_NET_SITE_ID: "speedy.net.localhost",
            settings.SPEEDY_MATCH_SITE_ID: "speedy.match.localhost",
            settings.SPEEDY_COMPOSER_SITE_ID: "speedy.composer.localhost",
            settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: "speedy.mail.software.localhost",
        }
        self.assertEqual(first=self.site.id, second=site_id_dict[self.site.id])
        self.assertEqual(first=self.site.domain, second=domain_dict[self.site.id])
        self.assertEqual(first=len(self.all_languages_code_list), second=2)
        self.assertEqual(first=len(self.all_other_languages_code_list), second=1)
        self.assertEqual(first=len(self.all_languages_code_list), second=len(set(self.all_languages_code_list)))
        self.assertEqual(first=len(self.all_other_languages_code_list), second=len(set(self.all_other_languages_code_list)))
        self.assertListEqual(list1=self.all_languages_code_list, list2=['en', 'he'])
        self.assertListEqual(list1=self.all_other_languages_code_list, list2={'en': ['he'], 'he': ['en']}[self.language_code])
        self.assertIn(member=self.language_code, container=self.all_languages_code_list)
        self.assertSetEqual(set1=set(self.all_languages_code_list) - {self.language_code}, set2=set(self.all_other_languages_code_list))
        self.assertEqual(first=self.full_http_host, second='http://{language_code}.{domain}/'.format(language_code=self.language_code, domain=self.site.domain))
        self.assertEqual(first=len(self.all_other_full_http_host_list), second=len(self.all_other_languages_code_list))
        self.assertEqual(first=len(self.all_other_full_http_host_list), second=len(set(self.all_other_full_http_host_list)))
        self.assertListEqual(list1=self.all_other_full_http_host_list, list2={'en': ['http://he.{domain}/'.format(domain=self.site.domain)], 'he': ['http://en.{domain}/'.format(domain=self.site.domain)]}[self.language_code])

    def setup(self):
        self.language_code = settings.LANGUAGE_CODE
        self.all_languages_code_list = [language_code for language_code, language_name in settings.LANGUAGES]
        self.all_other_languages_code_list = [language_code for language_code in self.all_languages_code_list if (not (language_code == self.language_code))]
        self.http_host = "{language_code}.{domain}".format(language_code=self.language_code, domain=self.site.domain)
        self.full_http_host = 'http://{http_host}/'.format(http_host=self.http_host)
        self.all_other_full_http_host_list = ['http://{language_code}.{domain}/'.format(language_code=language_code, domain=self.site.domain) for language_code in self.all_other_languages_code_list]
        self.validate_all_values()
        self.client = self.client_class(HTTP_HOST=self.http_host)

    def setUp(self):
        super().setUp()
        self.setup()


def conditional_test(test_func):
    def wrapper(method_or_class):
        if (inspect.isclass(method_or_class)):
            # Decorate class
            if (test_func()):
                return method_or_class
            else:
                return
        else:
            # Decorate method
            def inner(*args, **kwargs):
                if (test_func()):
                    return method_or_class(*args, **kwargs)
                else:
                    return

            return inner

    return wrapper


exclude_on_site = lambda site_id: conditional_test(test_func=lambda: (not (settings.SITE_ID == site_id)))
exclude_on_speedy_net = exclude_on_site(site_id=settings.SPEEDY_NET_SITE_ID)
exclude_on_speedy_match = exclude_on_site(site_id=settings.SPEEDY_MATCH_SITE_ID)
exclude_on_speedy_composer = exclude_on_site(site_id=settings.SPEEDY_COMPOSER_SITE_ID)
exclude_on_speedy_mail_software = exclude_on_site(site_id=settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

only_on_site = lambda site_id: conditional_test(test_func=lambda: (settings.SITE_ID == site_id))
only_on_speedy_net = only_on_site(site_id=settings.SPEEDY_NET_SITE_ID)
only_on_speedy_match = only_on_site(site_id=settings.SPEEDY_MATCH_SITE_ID)
only_on_speedy_composer = only_on_site(site_id=settings.SPEEDY_COMPOSER_SITE_ID)
only_on_speedy_mail_software = only_on_site(site_id=settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

only_on_sites = lambda site_id_list: conditional_test(test_func=lambda: (settings.SITE_ID in site_id_list))
only_on_sites_with_login = only_on_sites(site_id_list=[settings.SPEEDY_NET_SITE_ID, settings.SPEEDY_MATCH_SITE_ID])
