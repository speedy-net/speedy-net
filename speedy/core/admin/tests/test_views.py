from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.html import escape

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.admin.test.mixins import SpeedyCoreAdminLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory


        class AdminViewBaseMixin(SpeedyCoreAdminLanguageMixin, TestCaseMixin):
            """
            Base mixin for testing admin-only views: sets up three users (two regular, one admin/superuser) and asserts access is denied to visitors and regular users, but granted to the admin.

            Methods:
                get_page_url(self): Not implemented in this mixin - must be overridden by subclasses to return the page URL under test.
                assert_permission_denied(self, r): Asserts the given response denies permission (status code 403, with the "Permission Denied" heading and the private-page alert).
                set_up(self): Creates two regular users and one admin/superuser user, and sets the page URL under test.
                test_visitor_has_no_access(self): Asserts a logged-out visitor is denied access to the page.
                test_user_1_has_no_access(self): Asserts a regular (non-admin) user is denied access to the page.
                test_user_2_has_no_access(self): Asserts another regular (non-admin) user is denied access to the page.
                test_admin_has_access(self): Asserts the admin user can access the page (status code 200, without the permission-denied heading or alert), and returns the response.
            """
            def get_page_url(self):
                """
                Not implemented in this mixin - must be overridden by subclasses to return the page URL under test.

                :raises NotImplementedError: Always, since this method must be overridden by subclasses.
                """
                raise NotImplementedError("This method is not implemented in this mixin.")

            def assert_permission_denied(self, r):
                """
                Asserts the given response denies permission to the page (status code 403, containing the "Permission Denied" heading and the private-page alert).

                :param r: The HTTP response to check.
                :type r: django.http.HttpResponse
                """
                self.assertEqual(first=r.status_code, second=403)
                self.assertIn(member="<h1>{}</h1>".format(escape(text=self._permission_denied_h1)), container=r.content.decode())
                self.assertIn(member=escape(text=self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())

            def set_up(self):
                """
                Creates two regular active users and one admin (superuser/staff) active user, and sets the page URL under test.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory(is_superuser=True, is_staff=True)
                self.page_url = self.get_page_url()

            def test_visitor_has_no_access(self):
                """
                Asserts that a logged-out visitor is denied access to the page.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_user_1_has_no_access(self):
                """
                Asserts that a regular (non-admin) user is denied access to the page.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_user_2_has_no_access(self):
                """
                Asserts that another regular (non-admin) user is denied access to the page.
                """
                self.client.login(username=self.user_2.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_admin_has_access(self):
                """
                Asserts that the admin (superuser/staff) user can access the page, without the permission-denied heading or alert, and returns the response.

                :return: The HTTP response of the page.
                :rtype: django.http.HttpResponse
                """
                self.client.login(username=self.user_3.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertNotIn(member="<h1>{}</h1>".format(escape(text=self._permission_denied_h1)), container=r.content.decode())
                self.assertNotIn(member=escape(text=self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())
                return r


        class AdminMainPageViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin main page view, asserting it links to both the Speedy Net and Speedy Match profile lists.

            Methods:
                get_page_url(self): Returns the admin main page URL.
                assert_permission_denied(self, r): Asserts the given response redirects to the admin login page, without the profile-list links.
                test_admin_has_access(self): Asserts the admin can access the page and it contains both the Speedy Net and Speedy Match profile-list links.
            """
            def get_page_url(self):
                """
                Returns the admin main page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/'

            def assert_permission_denied(self, r):
                """
                Asserts the given response redirects to the admin login page, without the Speedy Net or Speedy Match profile-list links.

                :param r: The HTTP response to check.
                :type r: django.http.HttpResponse
                """
                self.assertRedirects(response=r, expected_url='/admin/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertNotIn(member=escape(text=self._speedy_net_profiles), container=r.content.decode())
                self.assertNotIn(member=escape(text=self._speedy_match_profiles), container=r.content.decode())

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and it contains both the Speedy Net and Speedy Match profile-list links.
                """
                r = super().test_admin_has_access()
                self.assertIn(member=escape(text=self._speedy_net_profiles), container=r.content.decode())
                self.assertIn(member=escape(text=self._speedy_match_profiles), container=r.content.decode())


        @only_on_sites_with_login
        class AdminMainPageViewAllMainLanguagesEnglishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminMainPageViewAllMainLanguagesFrenchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminMainPageViewAllMainLanguagesGermanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminMainPageViewAllMainLanguagesSpanishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminMainPageViewAllMainLanguagesPortugueseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminMainPageViewAllMainLanguagesItalianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminMainPageViewAllMainLanguagesDutchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminMainPageViewAllMainLanguagesHebrewTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin main page view for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUsersListViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin users list view, asserting the three users appear (or not) by first name, name, full name and id depending on the site, and that no "other"-language users are mislabeled.

            Methods:
                get_page_url(self): Returns the admin users list page URL.
                test_admin_has_access(self): Asserts the admin can access the page and all three users appear by first name and name; full name appears only on Speedy Net, and ids never appear.
            """
            def get_page_url(self):
                """
                Returns the admin users list page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/users/'

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and all three users appear by first name and name; on Speedy Net the full name also appears, while on Speedy Match it does not; ids never appear, and no "other"-language markers appear in the response.
                """
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(text=user.name), container=r.content.decode())
                    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                        self.assertIn(member=escape(text=user.full_name), container=r.content.decode())
                    elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                        self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                    else:
                        raise NotImplementedError("Unsupported SITE_ID.")
                    self.assertNotIn(member=escape(text=user.id), container=r.content.decode())
                self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)


        @only_on_sites_with_login
        class AdminUsersListViewAllMainLanguagesEnglishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersListViewAllMainLanguagesFrenchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersListViewAllMainLanguagesGermanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersListViewAllMainLanguagesSpanishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersListViewAllMainLanguagesPortugueseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersListViewAllMainLanguagesItalianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersListViewAllMainLanguagesDutchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersListViewAllMainLanguagesHebrewTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users list view for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUsersWithDetailsListViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin users list view with details, asserting the three users appear by first name, name, full name (Speedy Net only) and id, with language markers present only on Speedy Match.

            Methods:
                get_page_url(self): Returns the admin users with-details list page URL.
                test_admin_has_access(self): Asserts the admin can access the page and all three users appear by first name, name and id; full name appears only on Speedy Net; language markers appear only on Speedy Match (once per user).
            """
            def get_page_url(self):
                """
                Returns the admin users with-details list page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/users/with-details/'

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and all three users appear by first name, name and id; on Speedy Net the full name also appears (and no language markers appear), while on Speedy Match the full name does not appear (and a language marker appears once per user, i.e. three times).
                """
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(text=user.name), container=r.content.decode())
                    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                        self.assertIn(member=escape(text=user.full_name), container=r.content.decode())
                    elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                        self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                    else:
                        raise NotImplementedError("Unsupported SITE_ID.")
                    self.assertIn(member=escape(text=user.id), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=3)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")


        @only_on_sites_with_login
        class AdminUsersWithDetailsListViewAllMainLanguagesEnglishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersWithDetailsListViewAllMainLanguagesFrenchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersWithDetailsListViewAllMainLanguagesGermanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersWithDetailsListViewAllMainLanguagesSpanishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersWithDetailsListViewAllMainLanguagesPortugueseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersWithDetailsListViewAllMainLanguagesItalianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersWithDetailsListViewAllMainLanguagesDutchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersWithDetailsListViewAllMainLanguagesHebrewTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin users with details list view for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUserDetailViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            """
            Tests the admin user detail view, asserting user_1's details appear (full name only on Speedy Net), with exactly one language marker on Speedy Match.

            Methods:
                get_page_url(self): Returns the admin user detail page URL for user_1.
                test_admin_has_access(self): Asserts the admin can access the page and user_1's first name, name and id appear; full name appears only on Speedy Net; exactly one language marker appears on Speedy Match.
            """
            def get_page_url(self):
                """
                Returns the admin user detail page URL for user_1.

                :return: The page URL.
                :rtype: str
                """
                return '/admin/user/{}/'.format(self.user_1.slug)

            def test_admin_has_access(self):
                """
                Asserts the admin can access the page and user_1's first name, name and id appear; on Speedy Net the full name also appears (and no language markers appear), while on Speedy Match the full name does not appear (and exactly one language marker appears).
                """
                r = super().test_admin_has_access()
                user = self.user_1
                self.assertIn(member=escape(text=user.first_name), container=r.content.decode())
                self.assertIn(member=escape(text=user.name), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertIn(member=escape(text=user.full_name), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotIn(member=escape(text=user.full_name), container=r.content.decode())
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.assertIn(member=escape(text=user.id), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=0)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape(text="['{}']".format(self.language_code))), second=1)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")


        @only_on_sites_with_login
        class AdminUserDetailViewAllMainLanguagesEnglishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUserDetailViewAllMainLanguagesFrenchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUserDetailViewAllMainLanguagesGermanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUserDetailViewAllMainLanguagesSpanishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUserDetailViewAllMainLanguagesPortugueseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUserDetailViewAllMainLanguagesItalianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUserDetailViewAllMainLanguagesDutchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUserDetailViewAllMainLanguagesHebrewTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the admin user detail view for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


