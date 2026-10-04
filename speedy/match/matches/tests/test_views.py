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
            def get_page_url(self):
                raise NotImplementedError("This method is not implemented in this mixin.")

            def get_template_name(self):
                raise NotImplementedError("This method is not implemented in this mixin.")

            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = self.get_page_url()
                self.template_name = self.get_template_name()

            def test_anonymous_has_no_access(self):
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_user_can_access(self):
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name=self.template_name)


        @only_on_speedy_match
        class EditMatchSettingsViewOnlyEnglishTestCase(EditViewBaseMixin, SiteTestCase):
            def get_page_url(self):
                return '/matches/settings/about-my-match/'

            def get_template_name(self):
                return 'matches/settings/about_my_match.html'


        @only_on_speedy_match
        class EditAboutMeViewOnlyEnglishTestCase(EditViewBaseMixin, SiteTestCase):
            def get_page_url(self):
                return '/matches/settings/about-me/'

            def get_template_name(self):
                return 'matches/settings/about_me.html'


        @only_on_speedy_match
        class EditMatchSettingsViewSaveTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/settings/about-my-match/'
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)

            def test_user_can_save_his_match_settings(self):
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

            def test_user_cannot_save_invalid_match_settings(self):
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
        class EditAboutMeViewSaveTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/settings/about-me/'
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)

            def test_user_can_save_his_about_me_settings(self):
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
                self.assertEqual(first=site_profile.profile_description, second="One two three four five six seven eight nine ten eleven twelve.")
                self.assertEqual(first=site_profile.city, second="Tel Aviv.")
                self.assertEqual(first=site_profile.height, second=180)
                self.assertEqual(first=site_profile.diet, second=User.DIET_VEGAN)
                self.assertEqual(first=site_profile.smoking_status, second=User.SMOKING_STATUS_NOT_SMOKING)
                self.assertEqual(first=site_profile.relationship_status, second=User.RELATIONSHIP_STATUS_SINGLE)


        @only_on_speedy_match
        class MatchesListViewOnlyEnglishTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/'

            def test_anonymous_has_no_access(self):
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_user_can_access(self):
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='matches/match_list.html')
                self.assertListEqual(list1=list(r.context['matches_list']), list2=[])
                self.assertIn(member='total_number_of_active_members_text', container=r.context)
                self.assertIs(expr1=r.context['include_in_conversions'], expr2=True)

            def test_user_with_no_matches_sees_empty_matches_list(self):
                # A second active user exists, but with default settings the two users don't necessarily match each other -
                # the matches list only has to not error out and not include the user themselves.
                ActiveUserFactory()
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertNotIn(member=self.user, container=r.context['matches_list'])

            def test_anonymous_post_redirects_to_edit_match_settings_without_saving(self):
                r = self.client.post(path=self.page_url, data={})
                self.assertRedirects(response=r, expected_url='/matches/settings/about-my-match/', status_code=302, target_status_code=302)

            def test_user_post_redirects_to_edit_match_settings_without_saving(self):
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url, data={})
                self.assertRedirects(response=r, expected_url='/matches/settings/about-my-match/', status_code=302, target_status_code=200)


        @only_on_speedy_match
        class MatchSettingsDefaultRedirectViewOnlyEnglishTestCase(SiteTestCase):
            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = '/matches/settings/'

            def test_anonymous_has_no_access(self):
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_user_is_redirected_to_edit_match_settings(self):
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/matches/settings/about-my-match/', status_code=302, target_status_code=200)


