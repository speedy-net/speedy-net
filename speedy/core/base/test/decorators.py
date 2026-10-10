from django.conf import settings as django_settings

if (django_settings.TESTS):
    import unittest

    from speedy.core.base.test import tests_settings


    def conditional_test(conditional_function):
        """
        Builds a decorator which skips a test unless `conditional_function()` returns a truthy value.

        :param conditional_function: Required. A callable with no arguments returning whether the test should run.
        :type conditional_function: callable
        :return: A `unittest.skipUnless` decorator.
        """
        return unittest.skipUnless(condition=conditional_function(), reason="This test is irrelevant in {}.".format(tests_settings.SITE_NAME_EN_DICT[django_settings.SITE_ID]))


    def exclude_on_site(site_id):
        """
        Builds a decorator which skips a test when running on the given site.

        :param site_id: Required. The site ID to exclude.
        :type site_id: int
        :return: A `unittest.skipUnless` decorator.
        """
        return conditional_test(conditional_function=lambda: (not (django_settings.SITE_ID == site_id)))


    def only_on_site(site_id):
        """
        Builds a decorator which skips a test unless running on the given site.

        :param site_id: Required. The only site ID to run the test on.
        :type site_id: int
        :return: A `unittest.skipUnless` decorator.
        """
        return conditional_test(conditional_function=lambda: (django_settings.SITE_ID == site_id))


    def only_on_sites(site_id_list):
        """
        Builds a decorator which skips a test unless running on one of the given sites.

        :param site_id_list: Required. The list of site IDs to run the test on.
        :type site_id_list: list[int]
        :return: A `unittest.skipUnless` decorator.
        """
        return conditional_test(conditional_function=lambda: (django_settings.SITE_ID in site_id_list))


    exclude_on_speedy_net = exclude_on_site(site_id=django_settings.SPEEDY_NET_SITE_ID)
    exclude_on_speedy_match = exclude_on_site(site_id=django_settings.SPEEDY_MATCH_SITE_ID)
    exclude_on_speedy_composer = exclude_on_site(site_id=django_settings.SPEEDY_COMPOSER_SITE_ID)
    exclude_on_speedy_mail_software = exclude_on_site(site_id=django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

    only_on_speedy_net = only_on_site(site_id=django_settings.SPEEDY_NET_SITE_ID)
    only_on_speedy_match = only_on_site(site_id=django_settings.SPEEDY_MATCH_SITE_ID)
    only_on_speedy_composer = only_on_site(site_id=django_settings.SPEEDY_COMPOSER_SITE_ID)
    only_on_speedy_mail_software = only_on_site(site_id=django_settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

    only_on_sites_with_login = only_on_sites(site_id_list=django_settings.SITES_WITH_LOGIN)


