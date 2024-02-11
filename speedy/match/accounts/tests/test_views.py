from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import unittest

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.tests.test_views import IndexViewTestCaseMixin, EditProfileNotificationsViewTestCaseMixin, ActivateSiteProfileViewTestCaseMixin1, ActivateSiteProfileViewTestCaseMixin2

        from speedy.core.accounts.models import User


        @only_on_speedy_match
        class IndexViewTestCase(IndexViewTestCaseMixin, SiteTestCase):
            def test_user_gets_redirected_to_his_matches(self):
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path='/')
                if (self.random_choice == 1):
                    self.assertEqual(first=self.user.is_active, second=True)
                    self.assertEqual(first=self.user.profile.is_active, second=True)
                    self.assertEqual(first=self.user.speedy_net_profile.is_active, second=True)
                    self.assertEqual(first=self.user.speedy_match_profile.is_active, second=True)
                    self.assertRedirects(response=r, expected_url='/matches/', status_code=302, target_status_code=200)
                elif (self.random_choice == 2):
                    self.assertEqual(first=self.user.is_active, second=True)
                    self.assertEqual(first=self.user.profile.is_active, second=False)
                    self.assertEqual(first=self.user.speedy_net_profile.is_active, second=True)
                    self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                    self.assertRedirects(response=r, expected_url='/registration-step-2/', status_code=302, target_status_code=200)
                elif (self.random_choice == 3):
                    self.assertEqual(first=self.user.is_active, second=False)
                    self.assertEqual(first=self.user.profile.is_active, second=False)
                    self.assertEqual(first=self.user.speedy_net_profile.is_active, second=False)
                    self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                    self.assertRedirects(response=r, expected_url='/welcome/', status_code=302, target_status_code=200)
                else:
                    raise NotImplementedError()


        @only_on_speedy_match
        class EditProfileNotificationsViewTestCase(EditProfileNotificationsViewTestCaseMixin, SiteTestCase):
            def test_user_can_save_his_settings(self):
                self.assertEqual(first=self.user.notify_on_message, second=User.NOTIFICATIONS_ON)
                self.assertEqual(first=self.user.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
                data = {
                    'notify_on_message': User.NOTIFICATIONS_OFF,
                    'notify_on_like': User.NOTIFICATIONS_OFF,
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url=self.page_url, status_code=302, target_status_code=200)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.notify_on_message, second=User.NOTIFICATIONS_OFF)
                self.assertEqual(first=user.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_OFF)


        @only_on_speedy_match
        class ActivateSiteProfileViewTestCase1(ActivateSiteProfileViewTestCaseMixin1, SiteTestCase):
            redirect_url = '/registration-step-2/'

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_inactive_user_can_request_activation(self):
                raise NotImplementedError()


        @only_on_speedy_match
        class ActivateSiteProfileViewTestCase2(ActivateSiteProfileViewTestCaseMixin2, SiteTestCase):
            redirect_url = '/welcome/'

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_inactive_user_can_request_activation(self):
                raise NotImplementedError()


