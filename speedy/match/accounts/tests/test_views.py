from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import json
        import unittest

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.tests.test_views import IndexViewTestCaseMixin, EditProfileNotificationsViewTestCaseMixin, ActivateSiteProfileViewWithInactiveUserTestCaseMixin, ActivateSiteProfileViewWithSpeedyNetInactiveUserTestCaseMixin
        from speedy.core.accounts.test.user_factories import InactiveUserFactory
        from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory
        from speedy.core.uploads.test.factories import UserImageFactory

        from speedy.core.accounts.models import User
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


        @only_on_speedy_match
        class IndexViewOnlyEnglishTestCase(IndexViewTestCaseMixin, SiteTestCase):
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
                    raise NotImplementedError("Invalid random choice.")


        @only_on_speedy_match
        class EditProfileNotificationsViewOnlyEnglishTestCase(EditProfileNotificationsViewTestCaseMixin, SiteTestCase):
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
        class ActivateSiteProfileViewWithInactiveUserOnlyEnglishTestCase(ActivateSiteProfileViewWithInactiveUserTestCaseMixin, SiteTestCase):
            redirect_url = '/registration-step-2/'

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_inactive_user_can_request_activation(self):
                raise NotImplementedError("This test is not implemented in this class.")


        @only_on_speedy_match
        class ActivateSiteProfileViewWithSpeedyNetInactiveUserOnlyEnglishTestCase(ActivateSiteProfileViewWithSpeedyNetInactiveUserTestCaseMixin, SiteTestCase):
            redirect_url = '/welcome/'

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_inactive_user_can_request_activation(self):
                raise NotImplementedError("This test is not implemented in this class.")


        class ActivateSiteProfileViewWizardTestCaseMixin(object):
            """
            Submits real form data through the registration wizard (steps 2-9), instead of bypassing it as
            ActiveUserFactory does. height is the only value which differs between the two test cases below.
            """
            height = 180

            def set_up(self):
                super().set_up()
                self.user = InactiveUserFactory()
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.user.photo = UserImageFactory(owner=self.user, visible_on_website=True)
                self.user.save()
                email = UserEmailAddressFactory(user=self.user, is_confirmed=True)
                email.save()
                email.make_primary()
                self.assertEqual(first=self.user.speedy_match_profile.is_active, second=False)
                self.assertEqual(first=self.user.speedy_match_profile.activation_step, second=2)

            def _post_step(self, step, data, **kwargs):
                return self.client.post(path='/registration-step-{step}/'.format(step=step), data=data, **kwargs)

            def _complete_steps_2_to_8(self):
                r = self._post_step(step=2, data={})
                self.assertRedirects(response=r, expected_url='/registration-step-3/', status_code=302, target_status_code=200)

                r = self._post_step(step=3, data={
                    'profile_description_en': "One two three four five six seven eight nine ten eleven twelve.",
                    'city_en': "Tel Aviv.",
                    'height': self.height,
                })
                self.assertRedirects(response=r, expected_url='/registration-step-4/', status_code=302, target_status_code=200)

                r = self._post_step(step=4, data={
                    'children_en': "One boy.",
                    'more_children_en': "Yes.",
                })
                self.assertRedirects(response=r, expected_url='/registration-step-5/', status_code=302, target_status_code=200)

                r = self._post_step(step=5, data={
                    'diet': User.DIET_VEGAN,
                    'smoking_status': User.SMOKING_STATUS_NOT_SMOKING,
                })
                self.assertRedirects(response=r, expected_url='/registration-step-6/', status_code=302, target_status_code=200)

                r = self._post_step(step=6, data={
                    'relationship_status': User.RELATIONSHIP_STATUS_SINGLE,
                })
                self.assertRedirects(response=r, expected_url='/registration-step-7/', status_code=302, target_status_code=200)

                r = self._post_step(step=7, data={
                    'gender_to_match': User.GENDER_VALID_VALUES,
                    'match_description_en': "One two three four five six seven eight.",
                    'min_age_to_match': 18,
                    'max_age_to_match': 99,
                })
                self.assertRedirects(response=r, expected_url='/registration-step-8/', status_code=302, target_status_code=200)

                r = self._post_step(step=8, data={
                    'diet_match': json.dumps(obj={str(diet): SpeedyMatchSiteProfile.RANK_5 for diet in User.DIET_VALID_VALUES}),
                    'smoking_status_match': json.dumps(obj={str(smoking_status): SpeedyMatchSiteProfile.RANK_5 for smoking_status in User.SMOKING_STATUS_VALID_VALUES}),
                })
                self.assertRedirects(response=r, expected_url='/registration-step-9/', status_code=302, target_status_code=200)

            def _post_step_9(self, **kwargs):
                return self._post_step(step=9, data={
                    'relationship_status_match': json.dumps(obj={str(relationship_status): SpeedyMatchSiteProfile.RANK_5 for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES}),
                }, **kwargs)


        @only_on_speedy_match
        class ActivateSiteProfileViewWizardOnlyEnglishTestCase(ActivateSiteProfileViewWizardTestCaseMixin, SiteTestCase):
            height = 180

            def test_user_can_complete_the_registration_wizard(self):
                self._complete_steps_2_to_8()
                r = self._post_step_9(follow=True)
                self.assertRedirects(response=r, expected_url='/matches/', status_code=302, target_status_code=200)
                messages_list = list(r.context['messages'])
                self.assertEqual(first=len(messages_list), second=1)
                self.assertIn(member="Welcome to", container=str(messages_list[0]))
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.speedy_match_profile.activation_step, second=10)
                self.assertEqual(first=user.speedy_match_profile.not_allowed_to_use_speedy_match, second=False)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active_and_valid, second=True)


        class ActivateSiteProfileViewWizardWithUnmatchableHeightTestCaseMixin(ActivateSiteProfileViewWizardTestCaseMixin):
            """
            self.height is a valid value for the height field itself (within MIN/MAX_HEIGHT_ALLOWED), but it's
            outside the matchable range (MIN/MAX_HEIGHT_TO_MATCH), so the user is not allowed to use Speedy Match.
            """
            def test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(self):
                self._complete_steps_2_to_8()
                r = self._post_step_9(follow=True)
                self.assertRedirects(response=r, expected_url='/registration-step-9/', status_code=302, target_status_code=200)
                messages_list = list(r.context['messages'])
                self.assertEqual(first=len(messages_list), second=1)
                self.assertIn(member="not authorized", container=str(messages_list[0]))
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=user.speedy_match_profile.activation_step, second=9)
                self.assertEqual(first=user.speedy_match_profile.not_allowed_to_use_speedy_match, second=True)
                self.assertEqual(first=user.speedy_match_profile.is_active, second=False)


        @only_on_speedy_match
        class ActivateSiteProfileViewWizardWithHeightTooSmallOnlyEnglishTestCase(ActivateSiteProfileViewWizardWithUnmatchableHeightTestCaseMixin, SiteTestCase):
            height = 10


        @only_on_speedy_match
        class ActivateSiteProfileViewWizardWithInvalidHeightOnlyEnglishTestCase(ActivateSiteProfileViewWizardWithUnmatchableHeightTestCaseMixin, SiteTestCase):
            height = 50


        @only_on_speedy_match
        class ActivateSiteProfileViewWizardWithHeightTooBigOnlyEnglishTestCase(ActivateSiteProfileViewWizardWithUnmatchableHeightTestCaseMixin, SiteTestCase):
            height = 330


        @only_on_speedy_match
        class ActivateSiteProfileViewWizardWithHeightWayTooBigOnlyEnglishTestCase(ActivateSiteProfileViewWizardWithUnmatchableHeightTestCaseMixin, SiteTestCase):
            height = 400


