from django.conf import settings as django_settings

if (django_settings.TESTS):
    import shutil
    import time
    from collections import defaultdict

    from django.core.management import call_command
    from django import test as django_test
    from django.test.runner import DiscoverRunner
    from django.contrib.sites.models import Site
    from django.utils import formats
    from django.utils.translation import gettext_lazy as _

    from speedy.core.base.test import tests_settings


    class SiteDiscoverRunner(DiscoverRunner):
        """
        Custom test runner that extends Django's DiscoverRunner to add additional functionality.

        Attributes:
            NUM_FAST_TESTS (int): Number of fastest tests to display.
            NUM_SLOW_TESTS (int): Number of slowest tests to display.
            test_languages (str): Languages to test.
            test_only (int): Number of tests to run.
            count_tests (int): Number of test groups to count.
            test_times (list): List of test times.

        Methods:
            __init__(self, *args, **kwargs): Initialize the test runner.
            _save_test_time(self, test_name, duration_func): Save the test time.
            _print_test_times(self, slowest_or_fastest): Print the test times.
            build_suite(self, test_labels=None, **kwargs): Build the test suite.
            test_suite(self, tests=()): Get the test suite.
            setup_test_environment(self, **kwargs): Set up the test environment.
            teardown_test_environment(self, **kwargs): Tear down the test environment.
            suite_result(self, suite, result, **kwargs): Get the suite result.
        """
        NUM_FAST_TESTS = 3
        NUM_SLOW_TESTS = 3

        def __init__(self, *args, **kwargs):
            assert (django_settings.TESTS is True)
            super().__init__(*args, **kwargs)
            self.test_languages = kwargs.get('test_languages', None)
            self.test_only = kwargs.get('test_only', None)
            self.count_tests = kwargs.get('count_tests', None)
            assert (self.test_languages in {'test-all-languages', 'test-default-languages', 'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'})
            if (self.test_only is not None):
                assert (self.test_only >= 0)
            if (self.count_tests is not None):
                assert (self.count_tests > 0)
            self.test_times = []

        def _save_test_time(self, test_name, duration_func):
            duration = duration_func()
            if (duration is not None):
                self.test_times.append((test_name, duration))

        def _print_test_times(self, slowest_or_fastest):
            assert (slowest_or_fastest in {"slowest", "fastest"})
            if (slowest_or_fastest == "slowest"):
                num_tests = self.NUM_SLOW_TESTS
                by_time_sorted_reverse = True
            elif (slowest_or_fastest == "fastest"):
                num_tests = self.NUM_FAST_TESTS
                by_time_sorted_reverse = False
            else:
                raise NotImplementedError("Invalid slowest_or_fastest.")

            by_time = sorted(self.test_times, key=lambda x: x[1], reverse=by_time_sorted_reverse)
            if by_time is not None:
                by_time = by_time[:num_tests]
            test_results = by_time
            test_result_count = len(test_results)
            if test_result_count:
                print()
                print("{test_result_count} {slowest_or_fastest} tests:".format(
                    test_result_count=test_result_count,
                    slowest_or_fastest=slowest_or_fastest,
                ))
            for func_name, timing in test_results:
                elapsed_time = formats.number_format(value=timing, decimal_pos=6)
                print("{elapsed_time}s {func_name}".format(
                    elapsed_time=elapsed_time,
                    func_name=func_name,
                ))

        def build_suite(self, test_labels=None, **kwargs):
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
            return super().build_suite(test_labels=test_labels, **kwargs)

        def test_suite(self, tests=()):
            if (self.test_only is not None):
                tests = tests[:self.test_only]
            if (self.count_tests is not None):
                if (len(tests) > 0):
                    count_by_group = defaultdict(int)
                    for test in tests:
                        parts = test.id().split('.')
                        group = '.'.join(parts[:self.count_tests])
                        count_by_group[group] += 1
                    print()
                    for (group, count) in count_by_group.items():
                        print(count, group)
                    print()
                else:
                    print()
                tests = []
            for test in tests:
                test.addCleanup(self._save_test_time, test.id(), test.get_elapsed_time)
            return super().test_suite(tests=tests)

        def setup_test_environment(self, **kwargs):
            super().setup_test_environment(**kwargs)
            django_settings.TEST_LANGUAGES = self.test_languages

        def teardown_test_environment(self, **kwargs):
            super().teardown_test_environment(**kwargs)
            del django_settings.TEST_LANGUAGES
            print("Deleting temporary files...")
            try:
                shutil.rmtree(django_settings.TESTS_MEDIA_ROOT)
            except OSError:
                pass

        def suite_result(self, suite, result, **kwargs):
            return_value = super().suite_result(suite=suite, result=result, **kwargs)
            self._print_test_times(slowest_or_fastest="fastest")
            self._print_test_times(slowest_or_fastest="slowest")
            print()
            return return_value


    class SpeedyCoreDiscoverRunner(SiteDiscoverRunner):
        """
        Custom test runner for Speedy Core that extends SiteDiscoverRunner.

        Methods:
            run_tests(self, *args, **kwargs): Override to prevent running tests on Speedy Core.
        """

        def run_tests(self, *args, **kwargs):
            # We don't run tests on speedy.core
            pass


    class SiteTestCase(django_test.TestCase):
        """
        Custom test case for site-specific tests.

        Attributes:
            maxDiff (int): Maximum difference for assert methods.

        Methods:
            _pre_setup(self): Pre-setup for the test case.
            validate_all_values(self): Validate all values for the site.
            run_or_skip_this_test(self): Skip the test if the language code is not in the list of languages to test.
            set_up(self): Set up the test case.
            start_time(self): Start the timer for the test.
            stop_time(self): Stop the timer for the test.
            get_elapsed_time(self, stop=False): Get the elapsed time for the test.
            tear_down(self): Tear down the test case.
            skipTest(self, *args, **kwargs): Skip the test and don't print the test duration.
            setUp(self): Set up the test case.
            tearDown(self): Tear down the test case.
        """
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
            self.assertIs(expr1=(17 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 25), expr2=True)
            self.assertIs(expr1=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_MODEL_LIST) < 33), expr2=True)
            self.assertIs(expr1=(17 < len(tests_settings.VALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 25), expr2=True)
            self.assertIs(expr1=(25 < len(tests_settings.INVALID_DATE_OF_BIRTH_IN_FORMS_LIST) < 33), expr2=True)

        def run_or_skip_this_test(self):
            """
            Skip this test if the language code is not in the list of languages to test.

            :return: None
            """
            if (self.language_code in {'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'}):
                pass
            else:
                raise NotImplementedError("Unsupported language_code.")
            run_this_test = False
            if (django_settings.TEST_LANGUAGES == "test-all-languages"):
                # Test all languages, and don't skip languages.
                run_this_test = True
            elif (django_settings.TEST_LANGUAGES == "test-default-languages"):
                # Test default languages.
                if (self.language_code in {'en', 'fr', 'he'}):
                    # Always run these tests.
                    run_this_test = True
                else:
                    # Run these tests only if self.language_code is equal to tests_settings.RANDOM_LANGUAGE_CODE_CHOICE (10% of the time chosen randomly), because these tests take a lot of time.
                    if (self.language_code == tests_settings.RANDOM_LANGUAGE_CODE_CHOICE):
                        run_this_test = True
            elif (django_settings.TEST_LANGUAGES in {'en', 'fr', 'de', 'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'he'}):
                # Test only one language (the given language code).
                if (self.language_code == django_settings.TEST_LANGUAGES):
                    run_this_test = True
            else:
                raise NotImplementedError("Unsupported TEST_LANGUAGES.")
            if (not (run_this_test)):
                self.skipTest(reason="Skipped test - language code skipped.")

        def set_up(self):
            self.language_code = django_settings.LANGUAGE_CODE
            self.run_or_skip_this_test()
            self.all_language_codes = [language_code for language_code, language_name in django_settings.LANGUAGES]
            self.all_other_language_codes = [language_code for language_code, language_name in django_settings.LANGUAGES if (not (language_code == self.language_code))]
            self.http_host = "{language_code}.{domain}".format(language_code=self.language_code, domain=self.site.domain)
            self.full_http_host = 'https://{http_host}/'.format(http_host=self.http_host)
            self.all_other_full_http_hosts = ['https://{language_code}.{domain}/'.format(language_code=language_code, domain=self.site.domain) for language_code in self.all_other_language_codes]
            self.client = self.client_class(HTTP_HOST=self.http_host)

        def start_time(self):
            self._start_time = time.perf_counter()

        def stop_time(self):
            if (not (hasattr(self, '_stop_time'))):
                self._stop_time = time.perf_counter()

        def get_elapsed_time(self, stop=False):
            if (not (hasattr(self, '_start_time'))):
                return None
            if stop:
                self.stop_time()
            stop_time = getattr(self, '_stop_time', None)
            if (stop_time is None):
                stop_time = time.perf_counter()
            return stop_time - self._start_time

        def tear_down(self):
            pass

        def skipTest(self, *args, **kwargs):
            """
            Skip this test. Don't print the test duration if the test is skipped.

            :param args: Optional. Positional arguments.
            :param kwargs: Optional. Keyword arguments.
            :return: None
            """
            if ("_start_time" in self.__dict__):
                del self._start_time
            return super().skipTest(*args, **kwargs)

        def setUp(self):
            self.start_time()
            return_value = super().setUp()
            self.set_up()
            self.validate_all_values()
            return return_value

        def tearDown(self):
            return_value = super().tearDown()
            self.tear_down()
            self.stop_time()
            return return_value


