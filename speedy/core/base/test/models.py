from django.conf import settings as django_settings

if (django_settings.TESTS):
    import shutil

    from django.core.management import call_command
    from django import test as django_test
    from django.test.runner import DiscoverRunner
    from django.contrib.sites.models import Site
    from django.utils.translation import gettext_lazy as _

    from speedy.core.base.test import tests_settings


    class SiteDiscoverRunner(DiscoverRunner):
        def __init__(self, *args, **kwargs):
            assert (django_settings.TESTS is True)
            super().__init__(*args, **kwargs)
            self.test_all_languages = kwargs.get('test_all_languages', False)
            self.test_default_languages = kwargs.get('test_default_languages', False)
            self.test_only_english = kwargs.get('test_only_english', False)
            self.test_only_language_code = kwargs.get('test_only_language_code', None)
            if ((self.test_all_languages is False) and (self.test_only_english is False) and (self.test_only_language_code is None)):
                self.test_default_languages = True
            self.test_only = kwargs.get('test_only', None)
            assert (self.test_all_languages in {True, False})
            assert (self.test_default_languages in {True, False})
            assert (self.test_only_english in {True, False})
            assert (self.test_only_language_code in {None, 'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'})
            assert (sum([(1 if (value is True) else (0 if (value is False) else 99)) for value in [self.test_all_languages, self.test_default_languages, self.test_only_english]] + [(1 if (value in {'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'}) else (0 if (value is None) else 99)) for value in [self.test_only_language_code]]) == 1)
            if (self.test_only is not None):
                assert (self.test_only >= 0)

        def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
            if (not (test_labels)):
                # Default test_labels are all the relevant directories under "speedy". For example ["speedy.core", "speedy.net"].
                # Due to problems with templates, "speedy.match" label is not added to speedy.net tests, and "speedy.net" label is not added to speedy.match tests.  # ~~~~ TODO: fix this bug and enable these labels, although the tests there are skipped.
                test_labels = []
                for label in django_settings.INSTALLED_APPS:
                    if (label.startswith('speedy.')):
                        label_to_test = '.'.join(label.split('.')[:2])
                        if (label_to_test == 'speedy.net'):
                            add_this_label = (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID)
                        elif (label_to_test == 'speedy.match'):
                            add_this_label = (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID)
                        elif (label_to_test == 'speedy.composer'):
                            add_this_label = (django_settings.SITE_ID == django_settings.SPEEDY_COMPOSER_SITE_ID)
                        elif (label_to_test == 'speedy.mail'):
                            add_this_label = (django_settings.SITE_ID == django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)
                        else:
                            add_this_label = True
                        if (add_this_label):
                            if (not (label_to_test in test_labels)):
                                test_labels.append(label_to_test)
            print(test_labels)
            return super().build_suite(test_labels=test_labels, extra_tests=extra_tests, **kwargs)

        def test_suite(self, tests=()):
            if (self.test_only is not None):
                tests = tests[:self.test_only]
            return super().test_suite(tests=tests)

        def setup_test_environment(self, **kwargs):
            super().setup_test_environment(**kwargs)
            django_settings.TEST_ALL_LANGUAGES = self.test_all_languages
            django_settings.TEST_DEFAULT_LANGUAGES = self.test_default_languages
            django_settings.TEST_ONLY_ENGLISH = self.test_only_english
            django_settings.TEST_ONLY_LANGUAGE_CODE = self.test_only_language_code

        def teardown_test_environment(self, **kwargs):
            super().teardown_test_environment(**kwargs)
            del django_settings.TEST_ALL_LANGUAGES
            del django_settings.TEST_DEFAULT_LANGUAGES
            del django_settings.TEST_ONLY_ENGLISH
            del django_settings.TEST_ONLY_LANGUAGE_CODE


    class SpeedyCoreDiscoverRunner(SiteDiscoverRunner):
        def run_tests(self, *args, **kwargs):
            # We don't run tests on speedy.core
            pass


    class SiteTestCase(django_test.TestCase):
        maxDiff = None

        def _pre_setup(self):
            assert (django_settings.TESTS is True)
            return_value = super()._pre_setup()
            call_command('load_data', tests_settings.SITES_FIXTURE, verbosity=0)
            self.site = Site.objects.get_current()
            self.site_name = _(self.site.name)
            return return_value

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
            if (self.language_code in {'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi'}):
                c = 'en'
            else:
                c = self.language_code
            site_name_dict = {
                django_settings.SPEEDY_NET_SITE_ID: {'en': "Speedy Net", 'he': "ספידי נט"}[c],
                django_settings.SPEEDY_MATCH_SITE_ID: {'en': "Speedy Match", 'he': "ספידי מץ'"}[c],
                django_settings.SPEEDY_COMPOSER_SITE_ID: {'en': "Speedy Composer", 'he': "ספידי קומפוזר"}[c],
                django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: {'en': "Speedy Mail Software", 'he': "תוכנת דואר ספידי"}[c],
            }
            self.assertEqual(first=self.site.id, second=django_settings.SITE_ID)
            self.assertEqual(first=self.site.id, second=site_id_dict[self.site.id])
            self.assertEqual(first=self.site.domain, second=domain_dict[self.site.id])
            self.assertEqual(first=self.site_name, second=site_name_dict[self.site.id])
            self.assertEqual(first=self.site.name, second=tests_settings.SITE_NAME_EN_DICT[django_settings.SITE_ID])
            if (self.language_code in {'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi'}):
                self.assertEqual(first=self.site_name, second=self.site.name)
            else:
                self.assertNotEqual(first=self.site_name, second=self.site.name)
            self.assertEqual(first=len(self.all_language_codes), second={django_settings.SPEEDY_NET_SITE_ID: 11, django_settings.SPEEDY_MATCH_SITE_ID: 11, django_settings.SPEEDY_COMPOSER_SITE_ID: 2, django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 2}[self.site.id])
            self.assertEqual(first=len(self.all_other_language_codes), second={django_settings.SPEEDY_NET_SITE_ID: 10, django_settings.SPEEDY_MATCH_SITE_ID: 10, django_settings.SPEEDY_COMPOSER_SITE_ID: 1, django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: 1}[self.site.id])
            self.assertEqual(first=len(self.all_language_codes), second=len(set(self.all_language_codes)))
            self.assertEqual(first=len(self.all_other_language_codes), second=len(set(self.all_other_language_codes)))
            self.assertListEqual(list1=self.all_language_codes, list2={django_settings.SPEEDY_NET_SITE_ID: ['en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'], django_settings.SPEEDY_MATCH_SITE_ID: ['en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'], django_settings.SPEEDY_COMPOSER_SITE_ID: ['en', 'he'], django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: ['en', 'he']}[self.site.id])
            if (self.language_code == 'en'):
                self.assertListEqual(list1=self.all_other_language_codes, list2={django_settings.SPEEDY_NET_SITE_ID: ['fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'], django_settings.SPEEDY_MATCH_SITE_ID: ['fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'], django_settings.SPEEDY_COMPOSER_SITE_ID: ['he'], django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: ['he']}[self.site.id])
            self.assertIn(member=self.language_code, container=self.all_language_codes)
            self.assertNotIn(member=self.language_code, container=self.all_other_language_codes)
            self.assertSetEqual(set1=set(self.all_language_codes) - {self.language_code}, set2=set(self.all_other_language_codes))
            self.assertEqual(first=self.full_http_host, second='https://{language_code}.{domain}/'.format(language_code=self.language_code, domain=self.site.domain))
            self.assertEqual(first=len(self.all_other_full_http_hosts), second=len(self.all_other_language_codes))
            self.assertEqual(first=len(self.all_other_full_http_hosts), second=len(set(self.all_other_full_http_hosts)))
            if (self.language_code == 'en'):
                self.assertListEqual(list1=self.all_other_full_http_hosts, list2={django_settings.SPEEDY_NET_SITE_ID: ['https://fr.{domain}/'.format(domain=self.site.domain), 'https://de.{domain}/'.format(domain=self.site.domain), 'https://es.{domain}/'.format(domain=self.site.domain), 'https://pt.{domain}/'.format(domain=self.site.domain), 'https://it.{domain}/'.format(domain=self.site.domain), 'https://nl.{domain}/'.format(domain=self.site.domain), 'https://sv.{domain}/'.format(domain=self.site.domain), 'https://ko.{domain}/'.format(domain=self.site.domain), 'https://fi.{domain}/'.format(domain=self.site.domain), 'https://he.{domain}/'.format(domain=self.site.domain)], django_settings.SPEEDY_MATCH_SITE_ID: ['https://fr.{domain}/'.format(domain=self.site.domain), 'https://de.{domain}/'.format(domain=self.site.domain), 'https://es.{domain}/'.format(domain=self.site.domain), 'https://pt.{domain}/'.format(domain=self.site.domain), 'https://it.{domain}/'.format(domain=self.site.domain), 'https://nl.{domain}/'.format(domain=self.site.domain), 'https://sv.{domain}/'.format(domain=self.site.domain), 'https://ko.{domain}/'.format(domain=self.site.domain), 'https://fi.{domain}/'.format(domain=self.site.domain), 'https://he.{domain}/'.format(domain=self.site.domain)], django_settings.SPEEDY_COMPOSER_SITE_ID: ['https://he.{domain}/'.format(domain=self.site.domain)], django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID: ['https://he.{domain}/'.format(domain=self.site.domain)]}[self.site.id])
            # print("tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST", tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST, len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST), len(set(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST)))  # ~~~~ TODO
            # print("tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST", tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST, len(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST), len(set(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST)))  # ~~~~ TODO
            # print("tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST", tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST, len(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST), len(set(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST)))  # ~~~~ TODO
            # print("tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST", tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST, len(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST), len(set(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST)))  # ~~~~ TODO
            self.assertIs(expr1=(15 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 23), expr2=True)
            self.assertIs(expr1=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 33), expr2=True)
            self.assertIs(expr1=(15 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 23), expr2=True)
            self.assertIs(expr1=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 33), expr2=True)

        def set_up(self):
            self.language_code = django_settings.LANGUAGE_CODE
            if (self.language_code in {'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'}):
                pass
            else:
                raise NotImplementedError()
            run_this_test = False
            if (django_settings.TEST_ALL_LANGUAGES):
                # Test all languages, and don't skip languages.
                run_this_test = True
            elif (django_settings.TEST_DEFAULT_LANGUAGES):
                # Test default languages.
                if (self.language_code in {'en', 'fr', 'he'}):
                    # Always run these tests.
                    run_this_test = True
                else:
                    # Run these tests only if self.language_code is equal to tests_settings.RANDOM_LANGUAGE_CODE_CHOICE (10% of the time chosen randomly), because these tests take a lot of time.
                    if (self.language_code == tests_settings.RANDOM_LANGUAGE_CODE_CHOICE):
                        run_this_test = True
            elif (django_settings.TEST_ONLY_ENGLISH):
                # Test only English.
                if (self.language_code in {'en'}):
                    run_this_test = True
            elif (django_settings.TEST_ONLY_LANGUAGE_CODE is not None):
                # Test only one language (the given language code).
                if (self.language_code == django_settings.TEST_ONLY_LANGUAGE_CODE):
                    run_this_test = True
            else:
                raise NotImplementedError()
            if (not (run_this_test)):
                self.skipTest(reason="Skipped test - language code skipped.")
                return
            self.all_language_codes = [language_code for language_code, language_name in django_settings.LANGUAGES]
            self.all_other_language_codes = [language_code for language_code, language_name in django_settings.LANGUAGES if (not (language_code == self.language_code))]
            self.http_host = "{language_code}.{domain}".format(language_code=self.language_code, domain=self.site.domain)
            self.full_http_host = 'https://{http_host}/'.format(http_host=self.http_host)
            self.all_other_full_http_hosts = ['https://{language_code}.{domain}/'.format(language_code=language_code, domain=self.site.domain) for language_code in self.all_other_language_codes]
            self.client = self.client_class(HTTP_HOST=self.http_host)

        def tear_down(self):
            pass

        def setUp(self):
            return_value = super().setUp()
            self.set_up()
            self.validate_all_values()
            return return_value

        def tearDown(self):
            return_value = super().tearDown()
            self.tear_down()
            return return_value

        @classmethod
        def tearDownClass(cls):
            # Canceled print (prints this line many times, this class is used many times).
            # print("Deleting temporary files...")
            try:
                shutil.rmtree(django_settings.TESTS_MEDIA_ROOT)
            except OSError:
                pass
            return super().tearDownClass()


