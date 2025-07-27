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
            def get_page_url(self):
                raise NotImplementedError()

            def assert_permission_denied(self, r):
                self.assertEqual(first=r.status_code, second=403)
                self.assertIn(member="<h1>{}</h1>".format(escape(self._permission_denied_h1)), container=r.content.decode())
                self.assertIn(member=escape(self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())

            def set_up(self):
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory(is_superuser=True, is_staff=True)
                self.page_url = self.get_page_url()

            def test_visitor_has_no_access(self):
                self.client.logout()
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_user_1_has_no_access(self):
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_user_2_has_no_access(self):
                self.client.login(username=self.user_2.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assert_permission_denied(r=r)

            def test_admin_has_access(self):
                self.client.login(username=self.user_3.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertNotIn(member="<h1>{}</h1>".format(escape(self._permission_denied_h1)), container=r.content.decode())
                self.assertNotIn(member=escape(self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())
                return r


        class AdminMainPageViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            def get_page_url(self):
                return '/admin/'

            def assert_permission_denied(self, r):
                self.assertRedirects(response=r, expected_url='/admin/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                self.assertNotIn(member=escape(self._speedy_net_profiles), container=r.content.decode())
                self.assertNotIn(member=escape(self._speedy_match_profiles), container=r.content.decode())

            def test_admin_has_access(self):
                r = super().test_admin_has_access()
                self.assertIn(member=escape(self._speedy_net_profiles), container=r.content.decode())
                self.assertIn(member=escape(self._speedy_match_profiles), container=r.content.decode())


        @only_on_sites_with_login
        class AdminMainPageViewAllLanguagesEnglishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminMainPageViewAllLanguagesFrenchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminMainPageViewAllLanguagesGermanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminMainPageViewAllLanguagesSpanishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminMainPageViewAllLanguagesPortugueseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminMainPageViewAllLanguagesItalianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminMainPageViewAllLanguagesDutchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminMainPageViewAllLanguagesSwedishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminMainPageViewAllLanguagesKoreanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminMainPageViewAllLanguagesFinnishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminMainPageViewAllLanguagesHebrewTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUsersListViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            def get_page_url(self):
                return '/admin/users/'

            def test_admin_has_access(self):
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(user.name), container=r.content.decode())
                    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                        self.assertIn(member=escape(user.full_name), container=r.content.decode())
                    elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                        self.assertNotIn(member=escape(user.full_name), container=r.content.decode())
                    else:
                        raise NotImplementedError()
                    self.assertNotIn(member=escape(user.id), container=r.content.decode())
                self.assertEqual(first=r.content.decode().count(escape("['{}']".format(self.language_code))), second=0)


        @only_on_sites_with_login
        class AdminUsersListViewAllLanguagesEnglishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersListViewAllLanguagesFrenchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersListViewAllLanguagesGermanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersListViewAllLanguagesSpanishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersListViewAllLanguagesPortugueseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersListViewAllLanguagesItalianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersListViewAllLanguagesDutchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUsersListViewAllLanguagesSwedishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUsersListViewAllLanguagesKoreanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUsersListViewAllLanguagesFinnishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersListViewAllLanguagesHebrewTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUsersWithDetailsListViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            def get_page_url(self):
                return '/admin/users/with-details/'

            def test_admin_has_access(self):
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(user.name), container=r.content.decode())
                    if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                        self.assertIn(member=escape(user.full_name), container=r.content.decode())
                    elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                        self.assertNotIn(member=escape(user.full_name), container=r.content.decode())
                    else:
                        raise NotImplementedError()
                    self.assertIn(member=escape(user.id), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape("['{}']".format(self.language_code))), second=0)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape("['{}']".format(self.language_code))), second=3)
                else:
                    raise NotImplementedError()


        @only_on_sites_with_login
        class AdminUsersWithDetailsListViewAllLanguagesEnglishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersWithDetailsListViewAllLanguagesFrenchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersWithDetailsListViewAllLanguagesGermanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersWithDetailsListViewAllLanguagesSpanishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersWithDetailsListViewAllLanguagesPortugueseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersWithDetailsListViewAllLanguagesItalianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersWithDetailsListViewAllLanguagesDutchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUsersWithDetailsListViewAllLanguagesSwedishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUsersWithDetailsListViewAllLanguagesKoreanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUsersWithDetailsListViewAllLanguagesFinnishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersWithDetailsListViewAllLanguagesHebrewTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUserDetailViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            def get_page_url(self):
                return '/admin/user/{}/'.format(self.user_1.slug)

            def test_admin_has_access(self):
                r = super().test_admin_has_access()
                user = self.user_1
                self.assertIn(member=escape(user.first_name), container=r.content.decode())
                self.assertIn(member=escape(user.name), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertIn(member=escape(user.full_name), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotIn(member=escape(user.full_name), container=r.content.decode())
                else:
                    raise NotImplementedError()
                self.assertIn(member=escape(user.id), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape("['{}']".format(self.language_code))), second=0)
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertEqual(first=r.content.decode().count(escape("['{}']".format(self.language_code))), second=1)
                else:
                    raise NotImplementedError()


        @only_on_sites_with_login
        class AdminUserDetailViewAllLanguagesEnglishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUserDetailViewAllLanguagesFrenchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUserDetailViewAllLanguagesGermanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUserDetailViewAllLanguagesSpanishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUserDetailViewAllLanguagesPortugueseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUserDetailViewAllLanguagesItalianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUserDetailViewAllLanguagesDutchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUserDetailViewAllLanguagesSwedishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUserDetailViewAllLanguagesKoreanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUserDetailViewAllLanguagesFinnishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUserDetailViewAllLanguagesHebrewTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


