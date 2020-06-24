from django.conf import settings as django_settings
from django.test import override_settings
from django.utils.html import escape

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login

    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.admin.test.mixins import SpeedyCoreAdminLanguageMixin


    class AdminViewBaseMixin(SpeedyCoreAdminLanguageMixin):
        def get_page_url(self):
            raise NotImplementedError()

        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            self.user_3 = ActiveUserFactory(is_superuser=True, is_staff=True)
            self.page_url = self.get_page_url()

        def test_visitor_has_no_access(self):
            self.client.logout()
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=403)
            self.assertIn(member="<h1>{}</h1>".format(escape(self._permission_denied_h1)), container=r.content.decode())
            self.assertIn(member=escape(self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())

        def test_user_1_has_no_access(self):
            self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=403)
            self.assertIn(member="<h1>{}</h1>".format(escape(self._permission_denied_h1)), container=r.content.decode())
            self.assertIn(member=escape(self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())

        def test_user_2_has_no_access(self):
            self.client.login(username=self.user_2.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=403)
            self.assertIn(member="<h1>{}</h1>".format(escape(self._permission_denied_h1)), container=r.content.decode())
            self.assertIn(member=escape(self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())

        def test_admin_has_access(self):
            self.client.login(username=self.user_3.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertNotIn(member="<h1>{}</h1>".format(escape(self._permission_denied_h1)), container=r.content.decode())
            self.assertNotIn(member=escape(self._speedy_is_sorry_but_this_page_is_private_alert), container=r.content.decode())
            return r


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
    @override_settings(LANGUAGE_CODE='he')
    class AdminUserDetailViewHebrewTestCase(AdminUserDetailViewTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


