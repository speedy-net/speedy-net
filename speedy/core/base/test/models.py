from django.conf import settings as django_settings
from django.core.management import call_command
from django.test import TestCase as DjangoTestCase
from django.test.runner import DiscoverRunner
from django.contrib.sites.models import Site

from speedy.core.base.test import tests_settings


class SiteDiscoverRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if (not (test_labels)):
            test_labels = [label for label in django_settings.INSTALLED_APPS if (label.startswith('speedy.'))]
        return super().build_suite(test_labels=test_labels, extra_tests=extra_tests, **kwargs)


class SpeedyCoreDiscoverRunner(SiteDiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # We don't run tests on speedy.core
        pass


class SiteTestCase(DjangoTestCase):
    maxDiff = None

    def _1___setup(self, django_settings): #### ~~~~ TODO: remove this function
        # ~~~~ TODO: remove all the following lines.
        from speedy.core.accounts.models import Entity, User
        from speedy.core.accounts.validators import get_username_validators, get_slug_validators, validate_date_of_birth_in_model
        Entity.settings = django_settings.ENTITY_SETTINGS
        Entity.validators = {
            'username': get_username_validators(min_username_length=Entity.settings.MIN_USERNAME_LENGTH, max_username_length=Entity.settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=True),
            'slug': get_slug_validators(min_username_length=Entity.settings.MIN_USERNAME_LENGTH, max_username_length=Entity.settings.MAX_USERNAME_LENGTH, min_slug_length=Entity.settings.MIN_SLUG_LENGTH, max_slug_length=Entity.settings.MAX_SLUG_LENGTH, allow_letters_after_digits=True) + ["validate_slug"],
        }
        User.settings = django_settings.USER_SETTINGS
        User.validators = {
            'username': get_username_validators(min_username_length=User.settings.MIN_USERNAME_LENGTH, max_username_length=User.settings.MAX_USERNAME_LENGTH, allow_letters_after_digits=False),
            'slug': get_slug_validators(min_username_length=User.settings.MIN_USERNAME_LENGTH, max_username_length=User.settings.MAX_USERNAME_LENGTH, min_slug_length=User.settings.MIN_SLUG_LENGTH, max_slug_length=User.settings.MAX_SLUG_LENGTH, allow_letters_after_digits=False) + ["validate_slug"],
            'date_of_birth': [validate_date_of_birth_in_model],
        }
        # raise Exception
        # ~~~~ TODO: remove all the above lines.

    def _pre_setup(self):
        super()._pre_setup()
        call_command('loaddata', tests_settings.SITES_FIXTURE, verbosity=0)
        self.site = Site.objects.get_current()

    def validate_all_values(self):
        site_id_dict = {
            django_settings.SPEEDY_NET_SITE_ID: 1,
            django_settings.SPEEDY_MATCH_SITE_ID: 2,
            django_settings.SPEEDY_COMPOSER_SITE_ID: 3,
            django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 4,
        }
        domain_dict = {
            django_settings.SPEEDY_NET_SITE_ID: "speedy.net.localhost",
            django_settings.SPEEDY_MATCH_SITE_ID: "speedy.match.localhost",
            django_settings.SPEEDY_COMPOSER_SITE_ID: "speedy.composer.localhost",
            django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: "speedy.mail.software.localhost",
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
        # print("tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST", tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST, len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST), len(set(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST)))  # ~~~~ TODO
        # print("tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST", tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST, len(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST), len(set(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST)))  # ~~~~ TODO
        # print("tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST", tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST, len(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST), len(set(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST)))  # ~~~~ TODO
        # print("tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST", tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST, len(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST), len(set(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST)))  # ~~~~ TODO
        self.assertTrue(expr=(15 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 23))
        self.assertTrue(expr=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 33))
        self.assertTrue(expr=(15 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 23))
        self.assertTrue(expr=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 33))

    def setup(self):
        self._1___setup(django_settings=django_settings) #### ~~~~ TODO: remove this line
        self.language_code = django_settings.LANGUAGE_CODE
        self.all_languages_code_list = [language_code for language_code, language_name in django_settings.LANGUAGES]
        self.all_other_languages_code_list = [language_code for language_code in self.all_languages_code_list if (not (language_code == self.language_code))]
        self.http_host = "{language_code}.{domain}".format(language_code=self.language_code, domain=self.site.domain)
        self.full_http_host = 'http://{http_host}/'.format(http_host=self.http_host)
        self.all_other_full_http_host_list = ['http://{language_code}.{domain}/'.format(language_code=language_code, domain=self.site.domain) for language_code in self.all_other_languages_code_list]
        self.validate_all_values()
        self.client = self.client_class(HTTP_HOST=self.http_host)

    def setUp(self):
        super().setUp()
        self.setup()


