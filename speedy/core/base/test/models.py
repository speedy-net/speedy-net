import shutil

from django.conf import settings as django_settings
from django.core.management import call_command
from django.test import TestCase as DjangoTestCase
from django.test.runner import DiscoverRunner
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from speedy.core.base.test import tests_settings


class SiteDiscoverRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        assert (django_settings.TESTS is True)
        super().__init__(*args, **kwargs)

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if (not (test_labels)):
            # Default test_labels are all the relevant directories under "speedy". For example ["speedy.core", "speedy.net"].
            # Due to problems with templates, "speedy.match" label is not added to speedy.net tests, and "speedy.net" label is not added to speedy.match tests. # ~~~~ TODO: fix this bug and enable these labels, although the tests there are skipped.
            test_labels = []
            for label in django_settings.INSTALLED_APPS:
                if (label.startswith('speedy.')):
                    label_to_test = '.'.join(label.split('.')[:2])
                    if (label_to_test == 'speedy.net'):
                        add_this_label = (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID)
                    elif (label_to_test == 'speedy.match'):
                        add_this_label = (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID)
                    else:
                        add_this_label = True
                    if (add_this_label):
                        if (not (label_to_test in test_labels)):
                            test_labels.append(label_to_test)
        print(test_labels)
        return super().build_suite(test_labels=test_labels, extra_tests=extra_tests, **kwargs)


class SpeedyCoreDiscoverRunner(SiteDiscoverRunner):
    def run_tests(self, *args, **kwargs):
        # We don't run tests on speedy.core
        pass


class SiteTestCase(DjangoTestCase):
    maxDiff = None

    def _pre_setup(self):
        self.assertTrue(expr=django_settings.TESTS)
        super()._pre_setup()
        call_command('load_data', tests_settings.SITES_FIXTURE, verbosity=0)
        self.site = Site.objects.get_current()
        self.site_name = _(self.site.name)

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
        site_name_dict = {
            django_settings.SPEEDY_NET_SITE_ID: {'en': "Speedy Net", 'he': "ספידי נט"}[self.language_code],
            django_settings.SPEEDY_MATCH_SITE_ID: {'en': "Speedy Match", 'he': "ספידי מץ'"}[self.language_code],
            django_settings.SPEEDY_COMPOSER_SITE_ID: {'en': "Speedy Composer", 'he': "ספידי קומפוזר"}[self.language_code],
            django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: {'en': "Speedy Mail Software", 'he': "תוכנת דואר ספידי"}[self.language_code],
        }
        self.assertEqual(first=self.site.id, second=site_id_dict[self.site.id])
        self.assertEqual(first=self.site.domain, second=domain_dict[self.site.id])
        self.assertEqual(first=self.site_name, second=site_name_dict[self.site.id])
        self.assertEqual(first=len(self.all_language_codes), second=2)
        self.assertEqual(first=len(self.all_other_language_codes), second=1)
        self.assertEqual(first=len(self.all_language_codes), second=len(set(self.all_language_codes)))
        self.assertEqual(first=len(self.all_other_language_codes), second=len(set(self.all_other_language_codes)))
        self.assertListEqual(list1=self.all_language_codes, list2=['en', 'he'])
        self.assertListEqual(list1=self.all_other_language_codes, list2={'en': ['he'], 'he': ['en']}[self.language_code])
        self.assertIn(member=self.language_code, container=self.all_language_codes)
        self.assertNotIn(member=self.language_code, container=self.all_other_language_codes)
        self.assertSetEqual(set1=set(self.all_language_codes) - {self.language_code}, set2=set(self.all_other_language_codes))
        self.assertEqual(first=self.full_http_host, second='https://{language_code}.{domain}/'.format(language_code=self.language_code, domain=self.site.domain))
        self.assertEqual(first=len(self.all_other_full_http_hosts), second=len(self.all_other_language_codes))
        self.assertEqual(first=len(self.all_other_full_http_hosts), second=len(set(self.all_other_full_http_hosts)))
        self.assertListEqual(list1=self.all_other_full_http_hosts, list2={'en': ['https://he.{domain}/'.format(domain=self.site.domain)], 'he': ['https://en.{domain}/'.format(domain=self.site.domain)]}[self.language_code])
        # print("tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST", tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST, len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST), len(set(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST)))  # ~~~~ TODO
        # print("tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST", tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST, len(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST), len(set(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST)))  # ~~~~ TODO
        # print("tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST", tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST, len(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST), len(set(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST)))  # ~~~~ TODO
        # print("tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST", tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST, len(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST), len(set(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST)))  # ~~~~ TODO
        self.assertTrue(expr=(15 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 23))
        self.assertTrue(expr=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 33))
        self.assertTrue(expr=(15 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 23))
        self.assertTrue(expr=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 33))

    def set_up(self):
        self.language_code = django_settings.LANGUAGE_CODE
        self.all_language_codes = [language_code for language_code, language_name in django_settings.LANGUAGES]
        self.all_other_language_codes = [language_code for language_code, language_name in django_settings.LANGUAGES if (not (language_code == self.language_code))]
        self.http_host = "{language_code}.{domain}".format(language_code=self.language_code, domain=self.site.domain)
        self.full_http_host = 'https://{http_host}/'.format(http_host=self.http_host)
        self.all_other_full_http_hosts = ['https://{language_code}.{domain}/'.format(language_code=language_code, domain=self.site.domain) for language_code in self.all_other_language_codes]
        self.client = self.client_class(HTTP_HOST=self.http_host)

    def setUp(self):
        super().setUp()
        self.set_up()
        self.validate_all_values()

    @classmethod
    def tearDownClass(cls):
        # Canceled print (prints this line many times, this class is used many times).
        # print("Deleting temporary files...")
        try:
            shutil.rmtree(django_settings.TESTS_MEDIA_ROOT)
        except OSError:
            pass
        super().tearDownClass()


