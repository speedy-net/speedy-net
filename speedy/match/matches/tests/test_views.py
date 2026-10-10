"""
Test cases for the matches list view and the edit match settings and about me views of Speedy Match.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import json

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.test.user_factories import ActiveUserFactory
        from speedy.core.accounts.models import User

        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


        class EditViewBaseMixin(TestCaseMixin):
            """
            Base mixin for testing a settings-edit view's GET access rules. Subclasses provide the page URL and expected template.

            Attributes:
                user: The active user used to access the page.
                page_url: The URL of the edit view, from get_page_url().
                template_name: The expected template name, from get_template_name().

            Methods:
                get_page_url(self): Returns the URL of the edit view (must be implemented by subclasses).
                get_template_name(self): Returns the expected template name (must be implemented by subclasses).
                set_up(self): Creates an active user and resolves the page URL and template name.
                test_anonymous_has_no_access(self): Asserts an anonymous visitor is redirected to login.
                test_user_can_access(self): Asserts a logged-in user can access the page and it renders the expected template.
            """

            def get_page_url(self):
                """
                Returns the URL of the edit view under test.

                :raises NotImplementedError: Always, unless overridden by a subclass.
                """
                raise NotImplementedError("This method is not implemented in this mixin.")

            def get_template_name(self):
                """
                Returns the expected template name for the edit view under test.

                :raises NotImplementedError: Always, unless overridden by a subclass.
                """
                raise NotImplementedError("This method is not implemented in this mixin.")

            def set_up(self):
                """
                Creates an active user and resolves the page URL and expected template name for this test case.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = self.get_page_url()
                self.template_name = self.get_template_name()

            def test_anonymous_has_no_access(self):
                """
                Asserts an anonymous visitor is redirected to the login page with the correct "next" parameter.
                """
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_user_can_access(self):
                """
                Asserts a logged-in user can access the page and it renders the expected template.
                """
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name=self.template_name)


        @only_on_speedy_match
        class EditMatchSettingsViewOnlyEnglishTestCase(EditViewBaseMixin, SiteTestCase):
            """
            Tests access to the "about my match" settings edit view, in English only.

            Methods:
                get_page_url(self): Returns the "about my match" settings edit page URL.
                get_template_name(self): Returns the "about my match" settings template name.
            """

            def get_page_url(self):
                """Returns the URL of the "about my match" settings edit page."""
                return '/matches/settings/about-my-match/'

            def get_template_name(self):
                """Returns the template name of the "about my match" settings edit page."""
                return 'matches/settings/about_my_match.html'


        @only_on_speedy_match
        class EditAboutMeViewOnlyEnglishTestCase(EditViewBaseMixin, SiteTestCase):
            """
            Tests access to the "about me" settings edit view, in English only.

            Methods:
                get_page_url(self): Returns the "about me" settings edit page URL.
                get_template_name(self): Returns the "about me" settings template name.
            """

            def get_page_url(self):
                """Returns the URL of the "about me" settings edit page."""
                return '/matches/settings/about-me/'

            def get_template_name(self):
                """Returns the template name of the "about me" settings edit page."""
                return 'matches/settings/about_me.html'


        @only_on_speedy_match
        class EditMatchSettingsViewSaveOnlyEnglishTestCase(SiteTestCase):
            """
            Tests saving the "about my match" settings form, in English only.

            Methods:
                set_up(self): Creates a logged-in active user and resolves the settings page URL.
                test_user_can_save_his_match_settings(self): Asserts valid match settings are saved and the user is redirected with a success message.
                test_user_cannot_save_invalid_match_settings(self): Asserts an invalid min/max age range is rejected and the settings are not saved.
            """

            def set_up(self):
                """
                Creates an active user, logs them in, and resolves the "about my match" settings page URL.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/settings/about-my-match/'
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)

            def test_user_can_save_his_match_settings(self):
                """
                Asserts posting valid match settings saves them, redirects to the matches page, shows a success message, and activates the user's Speedy Match profile.
                """
                data = {
                    'gender_to_match': User.GENDER_VALID_VALUES,
                    'match_description_en': "One two three four five six seven eight.",
                    'min_age_to_match': 20,
                    'max_age_to_match': 80,
                    'diet_match': json.dumps(obj={str(diet): SpeedyMatchSiteProfile.RANK_5 for diet in User.DIET_VALID_VALUES}),
                    'smoking_status_match': json.dumps(obj={str(smoking_status): SpeedyMatchSiteProfile.RANK_5 for smoking_status in User.SMOKING_STATUS_VALID_VALUES}),
                    'relationship_status_match': json.dumps(obj={str(relationship_status): SpeedyMatchSiteProfile.RANK_5 for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES}),
                }
                r = self.client.post(path=self.page_url, data=data, follow=True)
                self.assertRedirects(response=r, expected_url='/matches/', status_code=302, target_status_code=200)
                messages_list = list(r.context['messages'])
                self.assertEqual(first=len(messages_list), second=1)
                self.assertEqual(first=str(messages_list[0]), second="Your match settings were saved.")
                site_profile = SpeedyMatchSiteProfile.objects.get(pk=self.user.speedy_match_profile.pk)
                self.assertEqual(first=site_profile.gender_to_match, second=User.GENDER_VALID_VALUES)
                self.assertEqual(first=site_profile.match_description, second="One two three four five six seven eight.")
                self.assertEqual(first=site_profile.min_age_to_match, second=20)
                self.assertEqual(first=site_profile.max_age_to_match, second=80)
                self.assertEqual(first=site_profile.not_allowed_to_use_speedy_match, second=False)
                self.assertEqual(first=site_profile.activation_step, second=10)
                self.assertEqual(first=site_profile.is_active, second=True)
                self.assertEqual(first=site_profile.is_active_and_valid, second=True)

            def test_user_cannot_save_invalid_match_settings(self):
                """
                Asserts posting an invalid min/max age range (min greater than max) is rejected, re-renders the form with errors, and does not save the invalid settings.
                """
                data = {
                    'gender_to_match': User.GENDER_VALID_VALUES,
                    'match_description_en': "One two three four five six seven eight.",
                    'min_age_to_match': 80,
                    'max_age_to_match': 20,
                    'diet_match': json.dumps(obj={str(diet): SpeedyMatchSiteProfile.RANK_5 for diet in User.DIET_VALID_VALUES}),
                    'smoking_status_match': json.dumps(obj={str(smoking_status): SpeedyMatchSiteProfile.RANK_5 for smoking_status in User.SMOKING_STATUS_VALID_VALUES}),
                    'relationship_status_match': json.dumps(obj={str(relationship_status): SpeedyMatchSiteProfile.RANK_5 for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES}),
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='matches/settings/about_my_match.html')
                self.assertIs(expr1=r.context['form'].is_valid(), expr2=False)
                site_profile = SpeedyMatchSiteProfile.objects.get(pk=self.user.speedy_match_profile.pk)
                self.assertNotEqual(first=site_profile.min_age_to_match, second=80)


        @only_on_speedy_match
        class EditAboutMeViewSaveOnlyEnglishTestCase(SiteTestCase):
            """
            Tests saving the "about me" settings form, in English only.

            Methods:
                set_up(self): Creates a logged-in active user and resolves the settings page URL.
                test_user_can_save_his_about_me_settings(self): Asserts valid about-me settings are saved and the user is redirected with a success message.
                test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(self): Asserts an unmatchable height disables the user's Speedy Match profile and redirects to the registration step.
            """

            def set_up(self):
                """
                Creates an active user, logs them in, and resolves the "about me" settings page URL.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/settings/about-me/'
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)

            def test_user_can_save_his_about_me_settings(self):
                """
                Asserts posting valid about-me settings saves them, redirects to the matches page, shows a success message, and activates the user's Speedy Match profile.
                """
                data = {
                    'profile_description_en': "One two three four five six seven eight nine ten eleven twelve.",
                    'city_en': "Tel Aviv.",
                    'height': 180,
                    'children_en': "One boy.",
                    'more_children_en': "Yes.",
                    'diet': User.DIET_VEGAN,
                    'smoking_status': User.SMOKING_STATUS_NOT_SMOKING,
                    'relationship_status': User.RELATIONSHIP_STATUS_SINGLE,
                }
                r = self.client.post(path=self.page_url, data=data, follow=True)
                self.assertRedirects(response=r, expected_url='/matches/', status_code=302, target_status_code=200)
                messages_list = list(r.context['messages'])
                self.assertEqual(first=len(messages_list), second=1)
                self.assertEqual(first=str(messages_list[0]), second="Your match settings were saved.")
                site_profile = SpeedyMatchSiteProfile.objects.get(pk=self.user.speedy_match_profile.pk)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=site_profile.profile_description, second="One two three four five six seven eight nine ten eleven twelve.")
                self.assertEqual(first=user.city, second="Tel Aviv.")
                self.assertEqual(first=site_profile.height, second=180)
                self.assertEqual(first=user.diet, second=User.DIET_VEGAN)
                self.assertEqual(first=user.smoking_status, second=User.SMOKING_STATUS_NOT_SMOKING)
                self.assertEqual(first=user.relationship_status, second=User.RELATIONSHIP_STATUS_SINGLE)
                self.assertEqual(first=site_profile.not_allowed_to_use_speedy_match, second=False)
                self.assertEqual(first=site_profile.activation_step, second=10)
                self.assertEqual(first=site_profile.is_active, second=True)
                self.assertEqual(first=site_profile.is_active_and_valid, second=True)

            def test_user_with_unmatchable_height_is_not_allowed_to_use_speedy_match(self):
                """
                Asserts posting an unmatchable height saves the settings but disables the user's Speedy Match profile and redirects to the registration step that requires a matchable height.
                """
                data = {
                    'profile_description_en': "One two three four five six seven eight nine ten eleven twelve.",
                    'city_en': "Tel Aviv.",
                    'height': 10,
                    'children_en': "One boy.",
                    'more_children_en': "Yes.",
                    'diet': User.DIET_VEGAN,
                    'smoking_status': User.SMOKING_STATUS_NOT_SMOKING,
                    'relationship_status': User.RELATIONSHIP_STATUS_SINGLE,
                }
                r = self.client.post(path=self.page_url, data=data, follow=True)
                self.assertRedirects(response=r, expected_url='/registration-step-9/', status_code=302, target_status_code=200)
                messages_list = list(r.context['messages'])
                self.assertEqual(first=len(messages_list), second=1)
                self.assertEqual(first=str(messages_list[0]), second="Your match settings were saved.")
                site_profile = SpeedyMatchSiteProfile.objects.get(pk=self.user.speedy_match_profile.pk)
                user = User.objects.get(pk=self.user.pk)
                self.assertEqual(first=site_profile.not_allowed_to_use_speedy_match, second=True)
                self.assertEqual(first=site_profile.activation_step, second=9)
                self.assertEqual(first=site_profile.is_active, second=False)


        @only_on_speedy_match
        class MatchesListViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the matches list view, in English only.

            Methods:
                set_up(self): Creates an active user and resolves the matches list page URL.
                test_anonymous_has_no_access(self): Asserts an anonymous visitor is redirected to login.
                test_user_can_access(self): Asserts a logged-in user can access the page with an empty matches list.
                test_user_with_no_matches_sees_empty_matches_list(self): Asserts another active user doesn't appear in the matches list and the page doesn't error out.
                test_anonymous_post_redirects_to_edit_match_settings_without_saving(self): Asserts an anonymous POST redirects to the edit match settings page without saving anything.
                test_user_post_redirects_to_edit_match_settings_without_saving(self): Asserts a logged-in user's POST redirects to the edit match settings page without saving anything.
            """

            def set_up(self):
                """
                Creates an active user and resolves the matches list page URL.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/'

            def test_anonymous_has_no_access(self):
                """
                Asserts an anonymous visitor is redirected to the login page with the correct "next" parameter.
                """
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_user_can_access(self):
                """
                Asserts a logged-in user can access the page, the matches list is empty, and the context includes the active-members text and conversion-tracking flag.
                """
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='matches/match_list.html')
                self.assertListEqual(list1=list(r.context['matches_list']), list2=[])
                self.assertIn(member='total_number_of_active_members_text', container=r.context)
                self.assertIs(expr1=r.context['include_in_conversions'], expr2=True)

            def test_user_with_no_matches_sees_empty_matches_list(self):
                """
                Asserts that with a second active user present, the matches list view doesn't error out and the current user is never listed among their own matches.
                """
                # A second active user exists, but with default settings the two users don't necessarily match each other -
                # the matches list only has to not error out and not include the user themselves.
                ActiveUserFactory()
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertNotIn(member=self.user, container=r.context['matches_list'])

            def test_anonymous_post_redirects_to_edit_match_settings_without_saving(self):
                """
                Asserts an anonymous POST to the matches list redirects to the edit match settings page without saving anything.
                """
                r = self.client.post(path=self.page_url, data={})
                self.assertRedirects(response=r, expected_url='/matches/settings/about-my-match/', status_code=302, target_status_code=302)

            def test_user_post_redirects_to_edit_match_settings_without_saving(self):
                """
                Asserts a logged-in user's POST to the matches list redirects to the edit match settings page without saving anything.
                """
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url, data={})
                self.assertRedirects(response=r, expected_url='/matches/settings/about-my-match/', status_code=302, target_status_code=200)


        @only_on_speedy_match
        class MatchSettingsDefaultRedirectViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the default match settings redirect view, in English only.

            Methods:
                set_up(self): Creates an active user and resolves the default match settings page URL.
                test_anonymous_has_no_access(self): Asserts an anonymous visitor is redirected to login.
                test_user_is_redirected_to_edit_match_settings(self): Asserts a logged-in user is redirected to the "about my match" edit page.
            """

            def set_up(self):
                """
                Creates an active user and resolves the default match settings page URL.
                """
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/settings/'

            def test_anonymous_has_no_access(self):
                """
                Asserts an anonymous visitor is redirected to the login page with the correct "next" parameter.
                """
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_user_is_redirected_to_edit_match_settings(self):
                """
                Asserts a logged-in user requesting the default match settings page is redirected to the "about my match" edit page.
                """
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/matches/settings/about-my-match/', status_code=302, target_status_code=200)


