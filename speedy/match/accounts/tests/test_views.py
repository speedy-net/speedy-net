"""
Test cases for the views of the Speedy Match accounts app (index, profile notifications and the profile activation wizard).
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import json
        import unittest

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
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
            """
            Tests that the index view redirects users based on their account/profile activation state, run only once (in English) since it is language-independent.

            Methods:
                test_user_gets_redirected_to_his_matches(self): Asserts the index view redirects to matches, registration step 2, or welcome, depending on the user's random activation state.
            """
            def test_user_gets_redirected_to_his_matches(self):
                """
                Asserts the index view redirects to the matches list, registration step 2, or the welcome page, depending on the user's random activation state.
                """
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
            """
            Tests saving the Speedy Match profile notification settings, run only once (in English) since it is language-independent.

            Methods:
                test_user_can_save_his_settings(self): Asserts the user can turn off message and like notifications via the settings form.
            """
            def test_user_can_save_his_settings(self):
                """
                Asserts the user can turn off message and like notifications via the settings form, and the changes persist.
                """
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
            """
            Tests the activation view with an inactive user; this test is irrelevant in Speedy Match and is skipped.

            Methods:
                test_inactive_user_can_request_activation(self): Skipped - not implemented in this class.
            """
            redirect_url = '/registration-step-2/'

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_inactive_user_can_request_activation(self):
                """
                Skipped. This test is irrelevant in Speedy Match.
                """
                raise NotImplementedError("This test is not implemented in this class.")


        @only_on_speedy_match
        class ActivateSiteProfileViewWithSpeedyNetInactiveUserOnlyEnglishTestCase(ActivateSiteProfileViewWithSpeedyNetInactiveUserTestCaseMixin, SiteTestCase):
            """
            Tests the activation view with a Speedy Net inactive user; this test is irrelevant in Speedy Match and is skipped.

            Methods:
                test_inactive_user_can_request_activation(self): Skipped - not implemented in this class.
            """
            redirect_url = '/welcome/'

            @unittest.skip(reason="This test is irrelevant in Speedy Match.")
            def test_inactive_user_can_request_activation(self):
                """
                Skipped. This test is irrelevant in Speedy Match.
                """
                raise NotImplementedError("This test is not implemented in this class.")


        class ActivateSiteProfileViewWizardTestCaseMixin(TestCaseMixin):
            """
            Submits real form data through the registration wizard (steps 2-9), instead of bypassing it as
            ActiveUserFactory does.
            """

            def set_up(self):
                """
                Creates an inactive user with a visible photo and a confirmed primary email address, ready to start the registration wizard at step 2.
                """
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
                """
                Posts data to a given registration wizard step.

                :param step: The registration step number to post to.
                :type step: int
                :param data: The form data to post for this step.
                :type data: dict
                :param kwargs: Additional keyword arguments passed to the test client's post method.
                :return: The HTTP response.
                :rtype: django.http.HttpResponse
                """
                return self.client.post(path='/registration-step-{step}/'.format(step=step), data=data, **kwargs)

            def _complete_steps_2_to_8(self, height):
                """
                Submits valid form data for registration wizard steps 2 through 8 (profile, children, diet/smoking, relationship status, matching preferences, diet/smoking match ranks), asserting each redirects to the next step.

                :param height: The height value to submit at step 3.
                :type height: int
                """
                r = self._post_step(step=2, data={})
                self.assertRedirects(response=r, expected_url='/registration-step-3/', status_code=302, target_status_code=200)

                r = self._post_step(step=3, data={
                    'profile_description_en': "One two three four five six seven eight nine ten eleven twelve.",
                    'city_en': "Tel Aviv.",
                    'height': height,
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
                """
                Posts valid relationship-status matching ranks to complete registration wizard step 9.

                :param kwargs: Additional keyword arguments passed to the test client's post method.
                :return: The HTTP response.
                :rtype: django.http.HttpResponse
                """
                return self._post_step(step=9, data={
                    'relationship_status_match': json.dumps(obj={str(relationship_status): SpeedyMatchSiteProfile.RANK_5 for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES}),
                }, **kwargs)

            def run_test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(self, height):
                """
                height is a valid value for the height field itself (within MIN/MAX_HEIGHT_ALLOWED), but it's
                outside the matchable range (MIN/MAX_HEIGHT_TO_MATCH), so the user is not allowed to use Speedy
                Match.

                :param height: The height to submit in the registration wizard.
                :type height: int
                """
                self._complete_steps_2_to_8(height=height)
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
        class ActivateSiteProfileViewWizardOnlyEnglishTestCase(ActivateSiteProfileViewWizardTestCaseMixin, SiteTestCase):
            """
            Tests completing the Speedy Match registration wizard, including the unmatchable-height edge cases, run only once (in English) since it is language-independent.

            Methods:
                test_user_can_complete_the_registration_wizard(self): Asserts a user with a matchable height completes the wizard and is redirected to the matches list.
                test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_1(self): Tests an unmatchable height just above the minimum allowed height.
                test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_2(self): Tests an unmatchable height below the minimum height to match.
                test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_3(self): Tests an unmatchable height above the maximum height to match.
                test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_4(self): Tests an unmatchable height just below the maximum allowed height.
            """
            def test_user_can_complete_the_registration_wizard(self):
                """
                Asserts a user with a matchable height completes the registration wizard and is redirected to the matches list, with the profile active and valid.
                """
                height = 180
                self._complete_steps_2_to_8(height=height)
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

            def test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_1(self):
                """
                Tests that a height of 10 (valid but not matchable) is not allowed to use Speedy Match.
                """
                height = 10
                self.run_test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(height=height)

            def test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_2(self):
                """
                Tests that a height of 50 (valid but not matchable) is not allowed to use Speedy Match.
                """
                height = 50
                self.run_test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(height=height)

            def test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_3(self):
                """
                Tests that a height of 330 (valid but not matchable) is not allowed to use Speedy Match.
                """
                height = 330
                self.run_test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(height=height)

            def test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match_4(self):
                """
                Tests that a height of 400 (valid but not matchable) is not allowed to use Speedy Match.
                """
                height = 400
                self.run_test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(height=height)


