import unittest

from django.conf import settings as django_settings

from speedy.core.base.test import tests_settings
from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.tests.test_views import IndexViewTestCaseMixin, EditProfileNotificationsViewTestCaseMixin, ActivateSiteProfileViewTestCaseMixin
    from speedy.core.accounts.models import User
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    @only_on_speedy_match
    class IndexViewTestCase(IndexViewTestCaseMixin, SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user = ActiveUserFactory()

        def test_user_gets_redirected_to_his_matches(self):
            self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path='/')
            self.assertRedirects(response=r, expected_url='/matches/', target_status_code=200)


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
            self.assertRedirects(response=r, expected_url=self.page_url)
            user = User.objects.get(pk=self.user.pk)
            self.assertEqual(first=user.notify_on_message, second=User.NOTIFICATIONS_OFF)
            self.assertEqual(first=user.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_OFF)


    @only_on_speedy_match
    class ActivateSiteProfileViewTestCase(ActivateSiteProfileViewTestCaseMixin, SiteTestCase):
        redirect_url = '/registration-step-2/'

        @unittest.skip
        def test_inactive_user_can_request_activation(self):
            # ~~~~ TODO: check if we need this test
            raise NotImplementedError()

        # ~~~~ TODO: test when the Speedy Net account is also deactivated.


