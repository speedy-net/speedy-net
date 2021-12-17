from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net
        from speedy.core.accounts.tests.test_views import IndexViewTestCaseMixin, EditProfileNotificationsViewTestCaseMixin, ActivateSiteProfileViewTestCaseMixin1, ActivateSiteProfileViewTestCaseMixin2
        from speedy.core.accounts.models import User
        from speedy.core.accounts.test.user_factories import ActiveUserFactory


        @only_on_speedy_net
        class IndexViewTestCase(IndexViewTestCaseMixin, SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()

            def test_user_gets_redirected_to_his_profile(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path='/')
                self.assertRedirects(response=r, expected_url='/{}/'.format(self.user.slug), status_code=302, target_status_code=200)


        @only_on_speedy_net
        class EditProfileNotificationsViewTestCase(EditProfileNotificationsViewTestCaseMixin, SiteTestCase):
            def test_user_can_save_his_settings(self):
                self.assertEqual(first=self.user.notify_on_message, second=User.NOTIFICATIONS_ON)
                data = {
                    'notify_on_message': User.NOTIFICATIONS_OFF,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.notify_on_message, second=User.NOTIFICATIONS_OFF)


        @only_on_speedy_net
        class ActivateSiteProfileViewTestCase1(ActivateSiteProfileViewTestCaseMixin1, SiteTestCase):
            redirect_url = '/welcome/'

            def test_inactive_user_can_request_activation(self):
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)


        @only_on_speedy_net
        class ActivateSiteProfileViewTestCase2(ActivateSiteProfileViewTestCaseMixin2, SiteTestCase):
            redirect_url = '/welcome/'

            def test_inactive_user_can_request_activation(self):
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/', status_code=302, target_status_code=302)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.profile.is_active, second=True)
                self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)


