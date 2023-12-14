from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.html import escape

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.admin.test.mixins import SpeedyCoreAdminLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory


        class AdminViewBaseMixin(SpeedyCoreAdminLanguageMixin):
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


        class AdminMainPageViewTestCaseMixin(AdminViewBaseMixin):
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
        class AdminMainPageViewEnglishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminMainPageViewFrenchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminMainPageViewGermanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminMainPageViewSpanishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminMainPageViewPortugueseTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminMainPageViewItalianTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminMainPageViewDutchTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminMainPageViewSwedishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminMainPageViewKoreanTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminMainPageViewFinnishTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminMainPageViewHebrewTestCase(AdminMainPageViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUsersListViewTestCaseMixin(AdminViewBaseMixin):
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
        class AdminUsersListViewEnglishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersListViewFrenchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersListViewGermanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersListViewSpanishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersListViewPortugueseTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersListViewItalianTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersListViewDutchTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUsersListViewSwedishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUsersListViewKoreanTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUsersListViewFinnishTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersListViewHebrewTestCase(AdminUsersListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUsersWithDetailsListViewTestCaseMixin(AdminViewBaseMixin):
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
        class AdminUsersWithDetailsListViewEnglishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUsersWithDetailsListViewFrenchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUsersWithDetailsListViewGermanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUsersWithDetailsListViewSpanishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUsersWithDetailsListViewPortugueseTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUsersWithDetailsListViewItalianTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUsersWithDetailsListViewDutchTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUsersWithDetailsListViewSwedishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUsersWithDetailsListViewKoreanTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUsersWithDetailsListViewFinnishTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUsersWithDetailsListViewHebrewTestCase(AdminUsersWithDetailsListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class AdminUserDetailViewTestCaseMixin(AdminViewBaseMixin):
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
        class AdminUserDetailViewEnglishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class AdminUserDetailViewFrenchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class AdminUserDetailViewGermanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class AdminUserDetailViewSpanishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class AdminUserDetailViewPortugueseTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class AdminUserDetailViewItalianTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class AdminUserDetailViewDutchTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class AdminUserDetailViewSwedishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class AdminUserDetailViewKoreanTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class AdminUserDetailViewFinnishTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class AdminUserDetailViewHebrewTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


