"""
Test cases for the views of the Speedy Core profiles app (the UserMixin, the redirect to the current user's profile and the user detail view).
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random
        from datetime import date

        from django.test import override_settings
        from django.test.client import RequestFactory
        from django.views import generic
        from django.utils.html import escape
        from django.contrib.auth.models import AnonymousUser

        from friendship.models import Friend

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.tests.test_views import RedirectMeMixin

        from speedy.core.accounts.models import User
        from speedy.core.accounts.fields import UserAccessField
        from speedy.core.profiles.views import UserMixin


        class UserMixinTestView(UserMixin, generic.View):
            """
            Minimal view combining UserMixin with generic.View, used to test UserMixin's user-resolution logic in isolation.
            """

            def get(self, request, *args, **kwargs):
                """
                Return the view instance itself (instead of an HTTP response), so tests can inspect it directly.

                :param request: The current HTTP request.
                :type request: django.http.HttpRequest
                :param args: Additional positional arguments.
                :param kwargs: Additional keyword arguments.
                :return: The view instance.
                :rtype: UserMixinTestView
                """
                return self


        class UserMixinTestCaseMixin(TestCaseMixin):
            """
            Tests UserMixin's ability to resolve a user by an exact slug match.
            """

            def set_up(self):
                """
                Creates a request factory and two active users, one with a known slug and username.
                """
                super().set_up()
                self.factory = RequestFactory()
                self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
                self.other_user = ActiveUserFactory()

            def test_find_user_by_exact_slug(self):
                """
                Asserts UserMixin.get_user resolves the user whose slug exactly matches the 'slug' URL keyword argument.
                """
                request = self.factory.get('/look-at-me/some-page/')
                request.user = AnonymousUser()
                view = UserMixinTestView.as_view()(request=request, slug='look-at-me')
                self.assertEqual(first=view.get_user().id, second=self.user.id)


        @only_on_sites_with_login
        class LoggedInUserOnlyEnglishTestCase(RedirectMeMixin, SiteTestCase):
            """
            Tests that anonymous visitors requesting the /me/ URL are redirected to login (English only, since the behaviour doesn't depend on the language).
            """

            def set_up(self):
                """
                Creates two active users, one with a known slug and username.
                """
                super().set_up()
                self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
                self.other_user = ActiveUserFactory()

            def test_redirect_to_login_me(self):
                """
                Asserts an anonymous visitor requesting /me/ is redirected to the login page.
                """
                self.assert_me_url_redirects_to_login_url()

            def test_redirect_to_login_me_add_trailing_slash(self):
                """
                Asserts an anonymous visitor requesting /me (without a trailing slash) is redirected to /me/, and then to the login page.
                """
                r = self.client.get(path='/me')
                self.assertRedirects(response=r, expected_url='/me/', status_code=301, target_status_code=302)
                self.assert_me_url_redirects_to_login_url()

            # ~~~~ TODO: login and test /me/ and user profiles while logged in.


        class UserDetailViewTestCaseMixin(TestCaseMixin):
            """
            Tests the user detail view's visibility rules for the profile owner's name, date of birth and 404 behaviour, across active/deactivated users, friends/non-friends, and (on Speedy Match) match eligibility.
            """

            def set_up(self):
                """
                Creates a user with a fixed name, slug, date of birth and gender (chosen at random from a small set of profiles, in a language-specific alphabet when applicable), builds the user's profile URL, and creates another active user.
                """
                super().set_up()
                self.random_choice = random.choice([1, 2])
                if (self.random_choice == 1):
                    if (self.language_code in {'en', 'he', 'fr', 'de'}):
                        # Check names in English alphabet and in Hebrew alphabet.
                        self.user = ActiveUserFactory(first_name_en="Corrin", last_name_en="Gideon", slug="corrin-gideon", date_of_birth=date(year=1992, month=9, day=12), gender=User.GENDER_FEMALE)
                        self.user.first_name_he = "קורין"
                        self.user.last_name_he = "גדעון"
                    elif (self.language_code in {'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'ja', 'ru', 'zh', 'pl', 'fa', 'ar', 'id', 'uk', 'tr', 'vi', 'cs', 'hu', 'th', 'el', 'ms', 'sr', 'ro', 'bn', 'ca', 'no', 'bg', 'da', 'sk', 'hi', 'et', 'hr', 'az', 'zh-yue', 'lt', 'sl', 'eu', 'hy', 'uz', 'ta', 'lv'}):
                        # Check names in English alphabet.
                        self.user = ActiveUserFactory(first_name_en="Bar", last_name_en="Refaeli", slug="bar-refaeli", date_of_birth=date(year=1992, month=9, day=12), gender=User.GENDER_FEMALE)
                    else:
                        raise NotImplementedError("Unsupported language_code.")
                elif (self.random_choice == 2):
                    if (self.language_code in {'en', 'he'}):
                        # Check names in English alphabet and in Hebrew alphabet.
                        self.user = ActiveUserFactory(first_name_en="Jennifer", last_name_en="Connelly", slug="jennifer-connelly", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_FEMALE)
                        self.user.first_name_he = "ג'ניפר"
                        self.user.last_name_he = "קונלי"
                    elif (self.language_code == 'fr'):
                        # Check names in French alphabet.
                        self.user = ActiveUserFactory(first_name_en="Alizée", last_name_en="Jacotey", slug="aliz-e-jacotey", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_FEMALE)
                    elif (self.language_code == 'es'):
                        # Check names in Spanish alphabet.
                        self.user = ActiveUserFactory(first_name_en="Lionel", last_name_en="Messi", slug="lionel-messi", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_MALE)
                    elif (self.language_code == 'pt'):
                        # Check names in Portuguese alphabet.
                        self.user = ActiveUserFactory(first_name_en="Cristiano", last_name_en="Ronaldo", slug="cristiano-ronaldo", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_MALE)
                    elif (self.language_code == 'it'):
                        # Check names in Italian alphabet.
                        self.user = ActiveUserFactory(first_name_en="Andrea", last_name_en="Bocelli", slug="andrea-bocelli", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_MALE)
                    elif (self.language_code in {'de', 'nl', 'sv', 'ko', 'fi', 'ja', 'ru', 'zh', 'pl', 'fa', 'ar', 'id', 'uk', 'tr', 'vi', 'cs', 'hu', 'th', 'el', 'ms', 'sr', 'ro', 'bn', 'ca', 'no', 'bg', 'da', 'sk', 'hi', 'et', 'hr', 'az', 'zh-yue', 'lt', 'sl', 'eu', 'hy', 'uz', 'ta', 'lv'}):
                        # Check names in English alphabet.
                        self.user = ActiveUserFactory(first_name_en="Doron", last_name_en="Matalon", slug="doron-matalon", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_FEMALE)
                    else:
                        raise NotImplementedError("Unsupported language_code.")
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.user.save()
                self.user_profile_url = '/{}/'.format(self.user.slug)
                self.other_user = ActiveUserFactory()

            def deactivate_user(self):
                """
                Deactivate the profile's user.
                """
                self.user.is_active = False
                self.user.save()

            def test_user_profile_not_logged_in(self):
                """
                Asserts an anonymous visitor sees the profile (on Speedy Net, with date of birth visibility controlled by access settings) or is redirected to login (on Speedy Match), and gets a 404 once the user is deactivated (redirected to login on Speedy Match).
                """
                r = self.client.get(path=self.user_profile_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    # First, check if the date of birth is not visible.
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertIn(member=escape(text=self.full_name), container=r.content.decode())
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.birth_date), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.birth_year), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                    # Now, check if the date of birth is visible.
                    self.user.access_dob_day_month = UserAccessField.ACCESS_ANYONE
                    self.user.access_dob_year = UserAccessField.ACCESS_ANYONE
                    self.user.save()
                    r = self.client.get(path=self.user_profile_url)
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member=escape(text=self.birth_date), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.birth_year), container=r.content.decode())
                    self.assertIn(member=escape(text=self.user_birth_year), container=r.content.decode())
                    self.assertIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.not_user_birth_date), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    expected_url = '/login/?next={}'.format(self.user_profile_url)
                    self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.deactivate_user()
                r = self.client.get(path=self.user_profile_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.status_code, second=404)
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_404_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member=escape(text=self.expected_404_speedy_is_sorry), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    expected_url = '/login/?next={}'.format(self.user_profile_url)
                    self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_user_own_profile_logged_in(self):
                """
                Asserts the profile owner, logged in, sees their own full profile including name and date of birth, and gets a 404 (Speedy Net) or is redirected to /welcome/ (Speedy Match) once deactivated.
                """
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member=escape(text=self.first_name), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertIn(member=escape(text=self.full_name), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotIn(member=escape(text=self.full_name), container=r.content.decode())
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(text=self.birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.birth_year), container=r.content.decode())
                self.assertIn(member=escape(text=self.user_birth_year), container=r.content.decode())
                self.assertIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.not_user_birth_date), container=r.content.decode())
                self.deactivate_user()
                r = self.client.get(path=self.user_profile_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    # ~~~~ TODO: should redirect to '/welcome/'.
                    self.assertEqual(first=r.status_code, second=404)
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_404_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member=escape(text=self.expected_404_speedy_is_sorry), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    expected_url = '/welcome/'
                    self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")

            def test_user_profile_month_day_format_from_friend(self):
                """
                Asserts a friend viewing the profile sees the date of birth formatted according to the owner's day/month and year access settings (day/month only, full date, year only, or nothing), and that it's hidden again when logged out, and that match eligibility (on Speedy Match) further gates visibility of the profile.
                """
                # First, check if only the day and month are visible.
                self.user.access_dob_day_month = UserAccessField.ACCESS_FRIENDS
                self.user.save()
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.user, user2=self.other_user), expr2=True)
                self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member=escape(text=self.first_name), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertIn(member=escape(text=self.full_name), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotIn(member=escape(text=self.full_name), container=r.content.decode())
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(text=self.birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.birth_year), container=r.content.decode())
                self.assertIn(member=escape(text=self.user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.not_user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.not_user_birth_date), container=r.content.decode())
                # Then, check if all the birth date is visible.
                self.user.access_dob_year = UserAccessField.ACCESS_FRIENDS
                self.user.save()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(text=self.birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.birth_year), container=r.content.decode())
                self.assertIn(member=escape(text=self.user_birth_month_day), container=r.content.decode())
                self.assertIn(member=escape(text=self.user_birth_year), container=r.content.decode())
                self.assertIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.not_user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.not_user_birth_date), container=r.content.decode())
                # Then, check if only the year is visible.
                self.user.access_dob_day_month = UserAccessField.ACCESS_ME
                self.user.save()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.birth_date), container=r.content.decode())
                self.assertIn(member=escape(text=self.birth_year), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.user_birth_month_day), container=r.content.decode())
                self.assertIn(member=escape(text=self.user_birth_year), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.not_user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(text=self.not_user_birth_date), container=r.content.decode())
                # Then logout and check that nothing from the date of birth is visible on Speedy Net.
                # On Speedy Match, the profile is not visible to visitors at all.
                self.client.logout()
                r = self.client.get(path=self.user_profile_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.birth_date), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.birth_year), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.user_birth_month_day), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.not_user_birth_month_day), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.not_user_birth_date), container=r.content.decode())
                    # And then, check if only the day and month are visible again.
                    self.user.access_dob_day_month = UserAccessField.ACCESS_ANYONE
                    self.user.save()
                    r = self.client.get(path=self.user_profile_url)
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member=escape(text=self.birth_date), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.birth_year), container=r.content.decode())
                    self.assertIn(member=escape(text=self.user_birth_month_day), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.user_birth_date), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.not_user_birth_month_day), container=r.content.decode())
                    self.assertNotIn(member=escape(text=self.not_user_birth_date), container=r.content.decode())
                elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    expected_url = '/login/?next={}'.format(self.user_profile_url)
                    self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
                else:
                    raise NotImplementedError("Unsupported SITE_ID.")
                self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
                if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.other_user.speedy_match_profile.min_age_to_match = 80
                    self.other_user.save_user_and_profile()
                    r = self.client.get(path=self.user_profile_url)
                    self.assertEqual(first=r.status_code, second=404)
                    self.assertNotIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title_no_match[self.site.id])), container=r.content.decode())
                    self.other_user.speedy_match_profile.min_age_to_match = 36
                    self.other_user.save_user_and_profile()
                    r = self.client.get(path=self.user_profile_url)
                    if (self.random_choice == 1):
                        if (self.language_code in {'en', 'he', 'fr', 'de'}):
                            self.assertEqual(first=self.user.slug, second="corrin-gideon")
                        elif (self.language_code in {'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi', 'ja', 'ru', 'zh', 'pl', 'fa', 'ar', 'id', 'uk', 'tr', 'vi', 'cs', 'hu', 'th', 'el', 'ms', 'sr', 'ro', 'bn', 'ca', 'no', 'bg', 'da', 'sk', 'hi', 'et', 'hr', 'az', 'zh-yue', 'lt', 'sl', 'eu', 'hy', 'uz', 'ta', 'lv'}):
                            self.assertEqual(first=self.user.slug, second="bar-refaeli")
                        else:
                            raise NotImplementedError("Unsupported language_code.")
                        self.assertEqual(first=r.status_code, second=404)
                        self.assertNotIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                        self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title_no_match[self.site.id])), container=r.content.decode())
                    elif (self.random_choice == 2):
                        if (self.language_code in {'en', 'he'}):
                            self.assertEqual(first=self.user.slug, second="jennifer-connelly")
                        elif (self.language_code == 'fr'):
                            self.assertEqual(first=self.user.slug, second="aliz-e-jacotey")
                        elif (self.language_code == 'es'):
                            self.assertEqual(first=self.user.slug, second="lionel-messi")
                        elif (self.language_code == 'pt'):
                            self.assertEqual(first=self.user.slug, second="cristiano-ronaldo")
                        elif (self.language_code == 'it'):
                            self.assertEqual(first=self.user.slug, second="andrea-bocelli")
                        elif (self.language_code in {'de', 'nl', 'sv', 'ko', 'fi', 'ja', 'ru', 'zh', 'pl', 'fa', 'ar', 'id', 'uk', 'tr', 'vi', 'cs', 'hu', 'th', 'el', 'ms', 'sr', 'ro', 'bn', 'ca', 'no', 'bg', 'da', 'sk', 'hi', 'et', 'hr', 'az', 'zh-yue', 'lt', 'sl', 'eu', 'hy', 'uz', 'ta', 'lv'}):
                            self.assertEqual(first=self.user.slug, second="doron-matalon")
                        else:
                            raise NotImplementedError("Unsupported language_code.")
                        self.assertEqual(first=r.status_code, second=200)
                        self.assertNotIn(member="<title>{}</title>".format(escape(text=self.expected_title_no_match[self.site.id])), container=r.content.decode())
                        self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                    else:
                        raise NotImplementedError("Invalid random choice.")
                    self.other_user.speedy_match_profile.min_age_to_match = 12
                    self.other_user.save_user_and_profile()
                    r = self.client.get(path=self.user_profile_url)
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertNotIn(member="<title>{}</title>".format(escape(text=self.expected_title_no_match[self.site.id])), container=r.content.decode())
                    self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                self.deactivate_user()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=404)
                self.assertNotIn(member="<title>{}</title>".format(escape(text=self.expected_title[self.site.id])), container=r.content.decode())
                if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                    self.assertNotIn(member="<title>{}</title>".format(escape(text=self.expected_title_no_match[self.site.id])), container=r.content.decode())
                self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_404_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(text=self.expected_404_speedy_is_sorry), container=r.content.decode())

            def test_user_profile_deactivated_user_from_friend(self):
                """
                Asserts a friend of a deactivated user gets a 404 (with the expected title and message) when viewing that user's profile.
                """
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.user, user2=self.other_user), expr2=True)
                self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
                self.deactivate_user()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=404)
                self.assertIn(member="<title>{}</title>".format(escape(text=self.expected_404_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(text=self.expected_404_speedy_is_sorry), container=r.content.decode())


        @only_on_sites_with_login
        class UserDetailViewAllMainLanguagesEnglishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (English).
            """

            def set_up(self):
                """
                Sets up the English date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Birth Date"
                self.birth_year = "Birth Year"
                if (self.random_choice == 1):
                    self.first_name = "Corrin"
                    self.last_name = "Gideon"
                    self.full_name = "Corrin Gideon"
                    self.user_birth_date = "12 September 1992"
                    self.user_birth_month_day = "12 September"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 September 1990"
                    self.not_user_birth_month_day = "21 September"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Corrin Gideon / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Corrin / Speedy Match",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "corrin-gideon / Speedy Match",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Jennifer"
                    self.last_name = "Connelly"
                    self.full_name = "Jennifer Connelly"
                    self.user_birth_date = "31 January 1978"
                    self.user_birth_month_day = "31 January"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 January 1990"
                    self.not_user_birth_month_day = "30 January"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Jennifer Connelly / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Jennifer / Speedy Match",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "jennifer-connelly / Speedy Match",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Page Not Found / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Page Not Found / Speedy Match",
                }
                self.expected_404_speedy_is_sorry = 'Speedy is sorry, but the page is not found.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en' and the expected titles use the English format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alpha]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class UserDetailViewAllMainLanguagesFrenchTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (French).
            """

            def set_up(self):
                """
                Sets up the French date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Date de naissance"
                self.birth_year = "Année de naissance"
                if (self.random_choice == 1):
                    self.first_name = "Corrin"
                    self.last_name = "Gideon"
                    self.full_name = "Corrin Gideon"
                    self.user_birth_date = "12 septembre 1992"
                    self.user_birth_month_day = "12 septembre"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 septembre 1990"
                    self.not_user_birth_month_day = "21 septembre"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Corrin Gideon / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Corrin / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "corrin-gideon / Speedy Match [alpha]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Alizée"
                    self.last_name = "Jacotey"
                    self.full_name = "Alizée Jacotey"
                    self.user_birth_date = "31 janvier 1978"
                    self.user_birth_month_day = "31 janvier"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 janvier 1990"
                    self.not_user_birth_month_day = "30 janvier"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Alizée Jacotey / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Alizée / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "aliz-e-jacotey / Speedy Match [alpha]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Page Non Trouvée / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Page Non Trouvée / Speedy Match [alpha]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy est désolée, mais la page n’a pas été trouvée.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr' and the expected titles use the French format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alpha]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class UserDetailViewAllMainLanguagesGermanTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (German).
            """

            def set_up(self):
                """
                Sets up the German date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Geburtsdatum"
                self.birth_year = "Geburtsjahr"
                if (self.random_choice == 1):
                    self.first_name = "Corrin"
                    self.last_name = "Gideon"
                    self.full_name = "Corrin Gideon"
                    self.user_birth_date = "12. September 1992"
                    self.user_birth_month_day = "12. September"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. September 1990"
                    self.not_user_birth_month_day = "21. September"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Corrin Gideon / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Corrin / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "corrin-gideon / Speedy Match [alpha]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. Januar 1978"
                    self.user_birth_month_day = "31. Januar"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. Januar 1990"
                    self.not_user_birth_month_day = "30. Januar"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alpha]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Seite Nicht Gefunden / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Seite Nicht Gefunden / Speedy Match [alpha]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy tut es leid, aber die Seite kann nicht gefunden werden.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de' and the expected titles use the German format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alpha]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class UserDetailViewAllMainLanguagesSpanishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (Spanish).
            """

            def set_up(self):
                """
                Sets up the Spanish date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Fecha de nacimiento"
                self.birth_year = "Año de nacimiento"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 de septiembre de 1992"
                    self.user_birth_month_day = "12 de septiembre"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 de septiembre de 1990"
                    self.not_user_birth_month_day = "21 de septiembre"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Lionel"
                    self.last_name = "Messi"
                    self.full_name = "Lionel Messi"
                    self.user_birth_date = "31 de enero de 1978"
                    self.user_birth_month_day = "31 de enero"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 de enero de 1990"
                    self.not_user_birth_month_day = "30 de enero"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Lionel Messi / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Lionel / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "lionel-messi / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Página No Encontrada / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Página No Encontrada / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy lo siente, pero no se encuentra la página.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es' and the expected titles use the Spanish format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class UserDetailViewAllMainLanguagesPortugueseTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (Portuguese).
            """

            def set_up(self):
                """
                Sets up the Portuguese date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Data de nascimento"
                self.birth_year = "Ano de nascimento"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 de Setembro de 1992"
                    self.user_birth_month_day = "12 de Setembro"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 de Setembro de 1990"
                    self.not_user_birth_month_day = "21 de Setembro"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Cristiano"
                    self.last_name = "Ronaldo"
                    self.full_name = "Cristiano Ronaldo"
                    self.user_birth_date = "31 de Janeiro de 1978"
                    self.user_birth_month_day = "31 de Janeiro"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 de Janeiro de 1990"
                    self.not_user_birth_month_day = "30 de Janeiro"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Cristiano Ronaldo / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Cristiano / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "cristiano-ronaldo / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Página Não Encontrada / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Página Não Encontrada / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'A Speedy lamenta, mas a página não foi encontrada.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt' and the expected titles use the Portuguese format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class UserDetailViewAllMainLanguagesItalianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (Italian).
            """

            def set_up(self):
                """
                Sets up the Italian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Data di nascita"
                self.birth_year = "Anno di nascita"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Settembre 1992"
                    self.user_birth_month_day = "12 Settembre"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Settembre 1990"
                    self.not_user_birth_month_day = "21 Settembre"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Andrea"
                    self.last_name = "Bocelli"
                    self.full_name = "Andrea Bocelli"
                    self.user_birth_date = "31 Gennaio 1978"
                    self.user_birth_month_day = "31 Gennaio"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Gennaio 1990"
                    self.not_user_birth_month_day = "30 Gennaio"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Andrea Bocelli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Andrea / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "andrea-bocelli / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Pagina Non Trovata / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Pagina Non Trovata / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy è spiacente, ma la pagina non è stata trovata.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it' and the expected titles use the Italian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class UserDetailViewAllMainLanguagesDutchTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (Dutch).
            """

            def set_up(self):
                """
                Sets up the Dutch date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Geboortedatum"
                self.birth_year = "Geboortejaar"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 september 1992"
                    self.user_birth_month_day = "12 september"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 september 1990"
                    self.not_user_birth_month_day = "21 september"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 januari 1978"
                    self.user_birth_month_day = "31 januari"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 januari 1990"
                    self.not_user_birth_month_day = "30 januari"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Pagina Niet Gevonden / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Pagina Niet Gevonden / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Het spijt Speedy, maar de pagina is niet gevonden.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl' and the expected titles use the Dutch format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class UserDetailViewAllMainLanguagesJapaneseTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Japanese).
            """

            def set_up(self):
                """
                Sets up the Japanese date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "生年月日"
                self.birth_year = "誕生年"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "1992年9月12日"
                    self.user_birth_month_day = "9月12日"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "1990年9月12日"
                    self.not_user_birth_month_day = "9月21日"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [アルファ]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [アルファ]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [アルファ]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "1978年1月31日"
                    self.user_birth_month_day = "1月31日"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "1990年1月31日"
                    self.not_user_birth_month_day = "1月30日"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [アルファ]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [アルファ]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [アルファ]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "ページが見つかりません / Speedy Net [アルファ]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "ページが見つかりません / Speedy Match [アルファ]",
                }
                self.expected_404_speedy_is_sorry = "Speedy 申し訳ありませんが、ページが見つかりませんでした。"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja' and the expected titles use the Japanese format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [アルファ]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [アルファ]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [アルファ]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class UserDetailViewAllMainLanguagesRussianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Russian).
            """

            def set_up(self):
                """
                Sets up the Russian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Дата рождения"
                self.birth_year = "Год рождения"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 сентября 1992 г."
                    self.user_birth_month_day = "12 Сентябрь"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 сентября 1990 г."
                    self.not_user_birth_month_day = "21 Сентябрь"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [альфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [альфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [альфа]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 января 1978 г."
                    self.user_birth_month_day = "31 Январь"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 января 1990 г."
                    self.not_user_birth_month_day = "30 Январь"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [альфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [альфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [альфа]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Страница Не Найдена / Speedy Net [альфа]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Страница Не Найдена / Speedy Match [альфа]",
                }
                self.expected_404_speedy_is_sorry = "Спиди сожалеет, но страница не найдена. Speedy"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru' and the expected titles use the Russian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [альфа]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [альфа]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [альфа]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class UserDetailViewAllMainLanguagesChineseTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Chinese).
            """

            def set_up(self):
                """
                Sets up the Chinese date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "出生日期"
                self.birth_year = "出生年份"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 九月 1992"
                    self.user_birth_month_day = "12 九月"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 九月 1990"
                    self.not_user_birth_month_day = "21 九月"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [阿爾法]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [阿爾法]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [阿爾法]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 一月 1978"
                    self.user_birth_month_day = "31 一月"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 一月 1990"
                    self.not_user_birth_month_day = "30 一月"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [阿爾法]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [阿爾法]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [阿爾法]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "頁面未找到 / Speedy Net [阿爾法]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "頁面未找到 / Speedy Match [阿爾法]",
                }
                self.expected_404_speedy_is_sorry = "Speedy很抱歉，找不到該頁面。"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh' and the expected titles use the Chinese format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [阿爾法]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [阿爾法]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [阿爾法]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class UserDetailViewAllMainLanguagesPolishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Polish).
            """

            def set_up(self):
                """
                Sets up the Polish date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Data urodzenia"
                self.birth_year = "Rok urodzenia"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 września 1992"
                    self.user_birth_month_day = "12 września"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 września 1990"
                    self.not_user_birth_month_day = "21 września"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 stycznia 1978"
                    self.user_birth_month_day = "31 stycznia"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 stycznia 1990"
                    self.not_user_birth_month_day = "30 stycznia"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Nie Znaleziono Strony / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Nie Znaleziono Strony / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy przeprasza, ale strona nie została znaleziona."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl' and the expected titles use the Polish format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class UserDetailViewAllMainLanguagesPersianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Persian).
            """

            def set_up(self):
                """
                Sets up the Persian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "تاریخ تولد"
                self.birth_year = "سال تولد"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 سپتامبر 1992"
                    self.user_birth_month_day = "12 سپتامبر"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 سپتامبر 1990"
                    self.not_user_birth_month_day = "21 سپتامبر"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [آلفا]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [آلفا]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [آلفا]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 ژانویه 1978"
                    self.user_birth_month_day = "31 ژانویه"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 ژانویه 1990"
                    self.not_user_birth_month_day = "30 ژانویه"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [آلفا]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [آلفا]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [آلفا]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "صفحه پیدا نشد / Speedy Net [آلفا]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "صفحه پیدا نشد / Speedy Match [آلفا]",
                }
                self.expected_404_speedy_is_sorry = "Speedy متاسفم، اما صفحه یافت نشد."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa' and the expected titles use the Persian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [آلفا]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [آلفا]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [آلفا]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class UserDetailViewAllMainLanguagesHebrewTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            """
            Tests the user detail view for all main languages (Hebrew).
            """

            def set_up(self):
                """
                Sets up the Hebrew date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "תאריך לידה"
                self.birth_year = "שנת לידה"
                if (self.random_choice == 1):
                    self.first_name = "קורין"
                    self.last_name = "גדעון"
                    self.full_name = "קורין גדעון"
                    self.user_birth_date = "12 בספטמבר 1992"
                    self.user_birth_month_day = "12 בספטמבר"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 בספטמבר 1990"
                    self.not_user_birth_month_day = "21 בספטמבר"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "קורין גדעון / ספידי נט [אלפא]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "קורין / ספידי מץ' [אלפא]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "corrin-gideon / ספידי מץ' [אלפא]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "ג'ניפר"
                    self.last_name = "קונלי"
                    self.full_name = "ג'ניפר קונלי"
                    self.user_birth_date = "31 בינואר 1978"
                    self.user_birth_month_day = "31 בינואר"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 בינואר 1990"
                    self.not_user_birth_month_day = "30 בינואר"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "ג'ניפר קונלי / ספידי נט [אלפא]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "ג'ניפר / ספידי מץ' [אלפא]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "jennifer-connelly / ספידי מץ' [אלפא]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "הדף לא נמצא / ספידי נט [אלפא]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "הדף לא נמצא / ספידי מץ' [אלפא]",
                }
                self.expected_404_speedy_is_sorry = 'ספידי מצטערת, אבל הדף לא נמצא.'

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he' and the expected titles use the Hebrew format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / ספידי נט [אלפא]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / ספידי מץ' [אלפא]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / ספידי מץ' [אלפא]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class UserDetailViewAllMainLanguagesKoreanTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Korean).
            """

            def set_up(self):
                """
                Sets up the Korean date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "생일"
                self.birth_year = "생년"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "1992년 9월 12일"
                    self.user_birth_month_day = "9월 12일"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "1990년 9월 12일"
                    self.not_user_birth_month_day = "9월 21일"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [알파]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [알파]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [알파]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "1978년 1월 31일"
                    self.user_birth_month_day = "1월 31일"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "1990년 1월 31일"
                    self.not_user_birth_month_day = "1월 30일"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [알파]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [알파]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [알파]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "페이지를 찾을 수 없습니다. / Speedy Net [알파]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "페이지를 찾을 수 없습니다. / Speedy Match [알파]",
                }
                self.expected_404_speedy_is_sorry = "Speedy에서 죄송하게 생각합니다만, 해당 페이지를 찾을 수 없습니다."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko' and the expected titles use the Korean format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [알파]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [알파]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [알파]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class UserDetailViewAllMainLanguagesArabicTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Arabic).
            """

            def set_up(self):
                """
                Sets up the Arabic date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "تاريخ الميلاد"
                self.birth_year = "سنة الميلاد"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 سبتمبر، 1992"
                    self.user_birth_month_day = "12 سبتمبر"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 سبتمبر، 1990"
                    self.not_user_birth_month_day = "21 سبتمبر"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [ألفا]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [ألفا]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [ألفا]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 يناير، 1978"
                    self.user_birth_month_day = "31 يناير"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 يناير، 1990"
                    self.not_user_birth_month_day = "30 يناير"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [ألفا]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [ألفا]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [ألفا]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "لم يتم العثور على الصفحة / Speedy Net [ألفا]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "لم يتم العثور على الصفحة / Speedy Match [ألفا]",
                }
                self.expected_404_speedy_is_sorry = "سبيدي آسف، ولكن لم يتم العثور على الصفحة. Speedy"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar' and the expected titles use the Arabic format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [ألفا]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [ألفا]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [ألفا]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class UserDetailViewAllMainLanguagesIndonesianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Indonesian).
            """

            def set_up(self):
                """
                Sets up the Indonesian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Tanggal Lahir"
                self.birth_year = "Tahun Lahir"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Sep. 1992"
                    self.user_birth_month_day = "12 September"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Sep. 1990"
                    self.not_user_birth_month_day = "21 September"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 Jan. 1978"
                    self.user_birth_month_day = "31 Januari"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Jan. 1990"
                    self.not_user_birth_month_day = "30 Januari"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Halaman Tidak Ditemukan / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Halaman Tidak Ditemukan / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy minta maaf, tapi halamannya tidak ditemukan."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id' and the expected titles use the Indonesian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class UserDetailViewAllMainLanguagesUkrainianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Ukrainian).
            """

            def set_up(self):
                """
                Sets up the Ukrainian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Дата народження"
                self.birth_year = "Рік народження"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 вересня 1992 р."
                    self.user_birth_month_day = "12 Вересень"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 вересня 1990 р."
                    self.not_user_birth_month_day = "21 Вересень"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [альфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [альфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [альфа]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 січня 1978 р."
                    self.user_birth_month_day = "31 Січень"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 січня 1990 р."
                    self.not_user_birth_month_day = "30 Січень"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [альфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [альфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [альфа]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Сторінка Не Знайдена / Speedy Net [альфа]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Сторінка Не Знайдена / Speedy Match [альфа]",
                }
                self.expected_404_speedy_is_sorry = "Спіді вибачте, але сторінка не знайдена. Speedy"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk' and the expected titles use the Ukrainian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [альфа]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [альфа]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [альфа]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class UserDetailViewAllMainLanguagesTurkishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Turkish).
            """

            def set_up(self):
                """
                Sets up the Turkish date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Doğum Tarihi"
                self.birth_year = "Doğum Yılı"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Eylül 1992"
                    self.user_birth_month_day = "12 Eylül"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Eylül 1990"
                    self.not_user_birth_month_day = "21 Eylül"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 Ocak 1978"
                    self.user_birth_month_day = "31 Ocak"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Ocak 1990"
                    self.not_user_birth_month_day = "30 Ocak"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Sayfa Bulunamadı / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Sayfa Bulunamadı / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy üzgün ama sayfa bulunamadı."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr' and the expected titles use the Turkish format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class UserDetailViewAllMainLanguagesVietnameseTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Vietnamese).
            """

            def set_up(self):
                """
                Sets up the Vietnamese date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Ngày sinh"
                self.birth_year = "Năm sinh"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "Ngày 12 tháng 9 năm 1992"
                    self.user_birth_month_day = "12 Tháng 9"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "Ngày 12 tháng 9 năm 1990"
                    self.not_user_birth_month_day = "21 Tháng 9"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alpha]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "Ngày 31 tháng 1 năm 1978"
                    self.user_birth_month_day = "31 Tháng 1"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "Ngày 31 tháng 1 năm 1990"
                    self.not_user_birth_month_day = "30 Tháng 1"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alpha]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Không Tìm Thấy Trang / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Không Tìm Thấy Trang / Speedy Match [alpha]",
                }
                self.expected_404_speedy_is_sorry = "Rất tiếc, Speedy không tìm thấy trang này."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi' and the expected titles use the Vietnamese format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alpha]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class UserDetailViewAllMainLanguagesCzechTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Czech).
            """

            def set_up(self):
                """
                Sets up the Czech date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Datum narození"
                self.birth_year = "Rok narození"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. září 1992"
                    self.user_birth_month_day = "12. září"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. září 1990"
                    self.not_user_birth_month_day = "21. září"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. ledna 1978"
                    self.user_birth_month_day = "31. leden"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. ledna 1990"
                    self.not_user_birth_month_day = "30. leden"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Stránka Nenalezena / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Stránka Nenalezena / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy se omlouvám, ale stránka nebyla nalezena."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs' and the expected titles use the Czech format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class UserDetailViewAllMainLanguagesSwedishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Swedish).
            """

            def set_up(self):
                """
                Sets up the Swedish date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Födelsedatum"
                self.birth_year = "Födelseår"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 september 1992"
                    self.user_birth_month_day = "12 september"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 september 1990"
                    self.not_user_birth_month_day = "21 september"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 januari 1978"
                    self.user_birth_month_day = "31 januari"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 januari 1990"
                    self.not_user_birth_month_day = "30 januari"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Sidan Kunde Inte Hittas / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Sidan Kunde Inte Hittas / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy beklagar, men sidan har inte hittats."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv' and the expected titles use the Swedish format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class UserDetailViewAllMainLanguagesFinnishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Finnish).
            """

            def set_up(self):
                """
                Sets up the Finnish date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Syntymäpäivä"
                self.birth_year = "Syntymävuosi"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. syyskuuta 1992"
                    self.user_birth_month_day = "12. syyskuu"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. syyskuuta 1990"
                    self.not_user_birth_month_day = "21. syyskuu"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. tammikuuta 1978"
                    self.user_birth_month_day = "31. tammikuu"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. tammikuuta 1990"
                    self.not_user_birth_month_day = "30. tammikuu"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Sivua Ei Löydy / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Sivua Ei Löydy / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy pahoittelee, mutta sivua ei löydy."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi' and the expected titles use the Finnish format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class UserDetailViewAllMainLanguagesHungarianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Hungarian).
            """

            def set_up(self):
                """
                Sets up the Hungarian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Születési dátum"
                self.birth_year = "Születési év"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "1992. szeptember 12."
                    self.user_birth_month_day = "szeptember 12."
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "1990. szeptember 12."
                    self.not_user_birth_month_day = "szeptember 21."
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "1978. január 31."
                    self.user_birth_month_day = "január 31."
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "1990. január 31."
                    self.not_user_birth_month_day = "január 30."
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Az Oldal Nem Található / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Az Oldal Nem Található / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy sajnálja, de az oldal nem található."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu' and the expected titles use the Hungarian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class UserDetailViewAllMainLanguagesThaiTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Thai).
            """

            def set_up(self):
                """
                Sets up the Thai date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "วันเกิด"
                self.birth_year = "ปีเกิด"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 กันยายน 1992"
                    self.user_birth_month_day = "12 กันยายน"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 กันยายน 1990"
                    self.not_user_birth_month_day = "21 กันยายน"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [อัลฟา]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [อัลฟา]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [อัลฟา]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 มกราคม 1978"
                    self.user_birth_month_day = "31 มกราคม"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 มกราคม 1990"
                    self.not_user_birth_month_day = "30 มกราคม"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [อัลฟา]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [อัลฟา]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [อัลฟา]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "ไม่พบหน้า / Speedy Net [อัลฟา]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "ไม่พบหน้า / Speedy Match [อัลฟา]",
                }
                self.expected_404_speedy_is_sorry = "Speedy ขออภัย ไม่พบหน้าดังกล่าว"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th' and the expected titles use the Thai format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [อัลฟา]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [อัลฟา]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [อัลฟา]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class UserDetailViewAllMainLanguagesGreekTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Greek).
            """

            def set_up(self):
                """
                Sets up the Greek date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Ημερομηνία γέννησης"
                self.birth_year = "Έτος γέννησης"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12/09/1992"
                    self.user_birth_month_day = "12 Σεπτέμβριος"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12/09/1990"
                    self.not_user_birth_month_day = "21 Σεπτέμβριος"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [άλφα]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [άλφα]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [άλφα]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31/01/1978"
                    self.user_birth_month_day = "31 Ιανουάριος"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31/01/1990"
                    self.not_user_birth_month_day = "30 Ιανουάριος"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [άλφα]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [άλφα]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [άλφα]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Η Σελίδα Δεν Βρέθηκε / Speedy Net [άλφα]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Η Σελίδα Δεν Βρέθηκε / Speedy Match [άλφα]",
                }
                self.expected_404_speedy_is_sorry = "Ο Speedy λυπάται, αλλά η σελίδα δεν βρέθηκε."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el' and the expected titles use the Greek format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [άλφα]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [άλφα]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [άλφα]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class UserDetailViewAllMainLanguagesMalayTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Malay).
            """

            def set_up(self):
                """
                Sets up the Malay date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Tarikh Lahir"
                self.birth_year = "Tahun Lahir"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Sep 1992"
                    self.user_birth_month_day = "12 September"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Sep 1990"
                    self.not_user_birth_month_day = "21 September"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 Jan 1978"
                    self.user_birth_month_day = "31 Januari"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Jan 1990"
                    self.not_user_birth_month_day = "30 Januari"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Halaman Tidak Ditemui / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Halaman Tidak Ditemui / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy minta maaf, tetapi halaman tidak ditemui."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms' and the expected titles use the Malay format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class UserDetailViewAllMainLanguagesSerbianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Serbian).
            """

            def set_up(self):
                """
                Sets up the Serbian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Датум рођења"
                self.birth_year = "Година рођења"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. септембар 1992."
                    self.user_birth_month_day = "12. септембар"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. септембар 1990."
                    self.not_user_birth_month_day = "21. септембар"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [алфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [алфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [алфа]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. јануар 1978."
                    self.user_birth_month_day = "31. јануар"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. јануар 1990."
                    self.not_user_birth_month_day = "30. јануар"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [алфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [алфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [алфа]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Страница Није Пронађена / Speedy Net [алфа]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Страница Није Пронађена / Speedy Match [алфа]",
                }
                self.expected_404_speedy_is_sorry = "Speedy се извињава, али страница није пронађена."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr' and the expected titles use the Serbian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [алфа]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [алфа]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [алфа]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class UserDetailViewAllMainLanguagesRomanianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Romanian).
            """

            def set_up(self):
                """
                Sets up the Romanian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Data de naștere"
                self.birth_year = "Anul nașterii"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Septembrie 1992"
                    self.user_birth_month_day = "12 Septembrie"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Septembrie 1990"
                    self.not_user_birth_month_day = "21 Septembrie"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 Ianuarie 1978"
                    self.user_birth_month_day = "31 Ianuarie"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Ianuarie 1990"
                    self.not_user_birth_month_day = "30 Ianuarie"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Pagina Nu A Fost Găsită / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Pagina Nu A Fost Găsită / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy regretă, dar pagina nu a fost găsită."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro' and the expected titles use the Romanian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class UserDetailViewAllMainLanguagesBengaliTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Bengali).
            """

            def set_up(self):
                """
                Sets up the Bengali date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "জন্ম তারিখ"
                self.birth_year = "জন্ম বছর"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 সেপ্টেম্বর, 1992"
                    self.user_birth_month_day = "12 সেপ্টেম্বর"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 সেপ্টেম্বর, 1990"
                    self.not_user_birth_month_day = "21 সেপ্টেম্বর"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [আলফা]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [আলফা]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [আলফা]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 জানুয়ারি, 1978"
                    self.user_birth_month_day = "31 জানুয়ারি"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 জানুয়ারি, 1990"
                    self.not_user_birth_month_day = "30 জানুয়ারি"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [আলফা]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [আলফা]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [আলফা]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "পৃষ্ঠাটি খুঁজে পাওয়া যায়নি / Speedy Net [আলফা]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "পৃষ্ঠাটি খুঁজে পাওয়া যায়নি / Speedy Match [আলফা]",
                }
                self.expected_404_speedy_is_sorry = "Speedy দুঃখিত, কিন্তু পৃষ্ঠাটি খুঁজে পাওয়া যায়নি।"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn' and the expected titles use the Bengali format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [আলফা]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [আলফা]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [আলফা]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class UserDetailViewAllMainLanguagesCatalanTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Catalan).
            """

            def set_up(self):
                """
                Sets up the Catalan date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Data de naixement"
                self.birth_year = "Any de naixement"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 setembre de 1992"
                    self.user_birth_month_day = "12 setembre"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 setembre de 1990"
                    self.not_user_birth_month_day = "21 setembre"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 gener de 1978"
                    self.user_birth_month_day = "31 gener"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 gener de 1990"
                    self.not_user_birth_month_day = "30 gener"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "No S'Ha Trobat La Pàgina / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "No S'Ha Trobat La Pàgina / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy ho sent, però no s'ha trobat la pàgina."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca' and the expected titles use the Catalan format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class UserDetailViewAllMainLanguagesNorwegianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Norwegian).
            """

            def set_up(self):
                """
                Sets up the Norwegian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Fødselsdato"
                self.birth_year = "Fødselsår"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 september 1992"
                    self.user_birth_month_day = "12 september"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 september 1990"
                    self.not_user_birth_month_day = "21 september"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 januar 1978"
                    self.user_birth_month_day = "31 januar"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 januar 1990"
                    self.not_user_birth_month_day = "30 januar"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Siden Ble Ikke Funnet / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Siden Ble Ikke Funnet / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy beklager, men siden ble ikke funnet."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no' and the expected titles use the Norwegian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class UserDetailViewAllMainLanguagesBulgarianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Bulgarian).
            """

            def set_up(self):
                """
                Sets up the Bulgarian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Дата на раждане"
                self.birth_year = "Година на раждане"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Септември 1992"
                    self.user_birth_month_day = "12 Септември"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Септември 1990"
                    self.not_user_birth_month_day = "21 Септември"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [алфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [алфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [алфа]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 Януари 1978"
                    self.user_birth_month_day = "31 Януари"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Януари 1990"
                    self.not_user_birth_month_day = "30 Януари"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [алфа]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [алфа]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [алфа]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Страницата Не Е Намерена / Speedy Net [алфа]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Страницата Не Е Намерена / Speedy Match [алфа]",
                }
                self.expected_404_speedy_is_sorry = "Speedy се извинява, но страницата не е намерена."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg' and the expected titles use the Bulgarian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [алфа]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [алфа]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [алфа]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class UserDetailViewAllMainLanguagesDanishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Danish).
            """

            def set_up(self):
                """
                Sets up the Danish date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Fødselsdato"
                self.birth_year = "Fødselsår"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. september 1992"
                    self.user_birth_month_day = "12. september"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. september 1990"
                    self.not_user_birth_month_day = "21. september"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. januar 1978"
                    self.user_birth_month_day = "31. januar"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. januar 1990"
                    self.not_user_birth_month_day = "30. januar"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Siden Blev Ikke Fundet / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Siden Blev Ikke Fundet / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy beklager, men siden blev ikke fundet."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da' and the expected titles use the Danish format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class UserDetailViewAllMainLanguagesSlovakTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Slovak).
            """

            def set_up(self):
                """
                Sets up the Slovak date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Dátum narodenia"
                self.birth_year = "Rok narodenia"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. september 1992"
                    self.user_birth_month_day = "12. september"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. september 1990"
                    self.not_user_birth_month_day = "21. september"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. január 1978"
                    self.user_birth_month_day = "31. január"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. január 1990"
                    self.not_user_birth_month_day = "30. január"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Stránka Sa Nenašla / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Stránka Sa Nenašla / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy sa ospravedlňuje, ale stránka sa nenašla."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk' and the expected titles use the Slovak format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class UserDetailViewAllMainLanguagesHindiTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Hindi).
            """

            def set_up(self):
                """
                Sets up the Hindi date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "जन्म तिथि"
                self.birth_year = "जन्म वर्ष"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 सितमबर 1992"
                    self.user_birth_month_day = "12 सितमबर"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 सितमबर 1990"
                    self.not_user_birth_month_day = "21 सितमबर"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [अल्फा]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [अल्फा]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [अल्फा]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 जनवरी 1978"
                    self.user_birth_month_day = "31 जनवरी"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 जनवरी 1990"
                    self.not_user_birth_month_day = "30 जनवरी"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [अल्फा]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [अल्फा]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [अल्फा]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "पृष्ठ नहीं मिला / Speedy Net [अल्फा]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "पृष्ठ नहीं मिला / Speedy Match [अल्फा]",
                }
                self.expected_404_speedy_is_sorry = "Speedy को खेद है, लेकिन यह पेज नहीं मिला।"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi' and the expected titles use the Hindi format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [अल्फा]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [अल्फा]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [अल्फा]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class UserDetailViewAllMainLanguagesEstonianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Estonian).
            """

            def set_up(self):
                """
                Sets up the Estonian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Sünnikuupäev"
                self.birth_year = "Sünniaasta"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. september 1992"
                    self.user_birth_month_day = "12. september"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. september 1990"
                    self.not_user_birth_month_day = "21. september"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. jaanuar 1978"
                    self.user_birth_month_day = "31. jaanuar"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. jaanuar 1990"
                    self.not_user_birth_month_day = "30. jaanuar"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Lehte Ei Leitud / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Lehte Ei Leitud / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Vabandame Speedy, kuid lehte ei leitud."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et' and the expected titles use the Estonian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class UserDetailViewAllMainLanguagesCroatianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Croatian).
            """

            def set_up(self):
                """
                Sets up the Croatian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Datum rođenja"
                self.birth_year = "Godina rođenja"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. rujna 1992."
                    self.user_birth_month_day = "12. Rujan"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. rujna 1990."
                    self.not_user_birth_month_day = "21. Rujan"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. siječnja 1978."
                    self.user_birth_month_day = "31. Siječanj"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. siječnja 1990."
                    self.not_user_birth_month_day = "30. Siječanj"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Stranica Nije Pronađena / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Stranica Nije Pronađena / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy se ispričava, ali stranica nije pronađena."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr' and the expected titles use the Croatian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class UserDetailViewAllMainLanguagesAzerbaijaniTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Azerbaijani).
            """

            def set_up(self):
                """
                Sets up the Azerbaijani date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Doğum tarixi"
                self.birth_year = "Doğum ili"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Sentyabr 1992"
                    self.user_birth_month_day = "12 Sentyabr"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Sentyabr 1990"
                    self.not_user_birth_month_day = "21 Sentyabr"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 Yanvar 1978"
                    self.user_birth_month_day = "31 Yanvar"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Yanvar 1990"
                    self.not_user_birth_month_day = "30 Yanvar"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Səhifə Tapılmadı / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Səhifə Tapılmadı / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy üzr istəyir, lakin səhifə tapılmadı."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az' and the expected titles use the Azerbaijani format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class UserDetailViewAllMainLanguagesCantoneseTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Cantonese).
            """

            def set_up(self):
                """
                Sets up the Cantonese date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "出生日期"
                self.birth_year = "出生年份"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 九月 1992"
                    self.user_birth_month_day = "12 九月"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 九月 1990"
                    self.not_user_birth_month_day = "21 九月"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [阿爾法]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [阿爾法]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [阿爾法]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 一月 1978"
                    self.user_birth_month_day = "31 一月"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 一月 1990"
                    self.not_user_birth_month_day = "30 一月"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [阿爾法]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [阿爾法]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [阿爾法]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "頁面未找到 / Speedy Net [阿爾法]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "頁面未找到 / Speedy Match [阿爾法]",
                }
                self.expected_404_speedy_is_sorry = "Speedy 很抱歉，找不到此頁面。"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue' and the expected titles use the Cantonese format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [阿爾法]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [阿爾法]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [阿爾法]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class UserDetailViewAllMainLanguagesLithuanianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Lithuanian).
            """

            def set_up(self):
                """
                Sets up the Lithuanian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Gimimo data"
                self.birth_year = "Gimimo metai"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "1992 m. rugsėjo 12 d."
                    self.user_birth_month_day = "rugsėjo 12 d."
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "1990 m. rugsėjo 12 d."
                    self.not_user_birth_month_day = "rugsėjo 21 d."
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "1978 m. sausio 31 d."
                    self.user_birth_month_day = "sausio 31 d."
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "1990 m. sausio 31 d."
                    self.not_user_birth_month_day = "sausio 30 d."
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Puslapis Nerastas / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Puslapis Nerastas / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy atsiprašo, bet puslapis nerastas."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt' and the expected titles use the Lithuanian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class UserDetailViewAllMainLanguagesSlovenianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Slovenian).
            """

            def set_up(self):
                """
                Sets up the Slovenian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Datum rojstva"
                self.birth_year = "Leto rojstva"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12. september 1992"
                    self.user_birth_month_day = "12. september"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12. september 1990"
                    self.not_user_birth_month_day = "21. september"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31. januar 1978"
                    self.user_birth_month_day = "31. januar"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31. januar 1990"
                    self.not_user_birth_month_day = "30. januar"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Stran Ni Bila Najdena / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Stran Ni Bila Najdena / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy se opravičuje, vendar stran ni bila najdena."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl' and the expected titles use the Slovenian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class UserDetailViewAllMainLanguagesBasqueTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Basque).
            """

            def set_up(self):
                """
                Sets up the Basque date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Jaiotza-data"
                self.birth_year = "Jaiotza-urtea"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "1992ko ira. 12a"
                    self.user_birth_month_day = "irailaren 12a"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "1990ko ira. 12a"
                    self.not_user_birth_month_day = "irailaren 21a"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "1978ko urt. 31a"
                    self.user_birth_month_day = "urtarrilaren 31a"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "1990ko urt. 31a"
                    self.not_user_birth_month_day = "urtarrilaren 30a"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Orria Ez Da Aurkitu / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Orria Ez Da Aurkitu / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy-k barkamena eskatzen du, baina orria ez da aurkitu."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu' and the expected titles use the Basque format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class UserDetailViewAllMainLanguagesArmenianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Armenian).
            """

            def set_up(self):
                """
                Sets up the Armenian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Ծննդյան ամսաթիվ"
                self.birth_year = "Ծննդյան տարեթիվ"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 Սեպտեմբեր 1992"
                    self.user_birth_month_day = "12 Սեպտեմբեր"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 Սեպտեմբեր 1990"
                    self.not_user_birth_month_day = "21 Սեպտեմբեր"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [ալֆա]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [ալֆա]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [ալֆա]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 Հունվար 1978"
                    self.user_birth_month_day = "31 Հունվար"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 Հունվար 1990"
                    self.not_user_birth_month_day = "30 Հունվար"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [ալֆա]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [ալֆա]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [ալֆա]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Էջը Գտնված Չէ / Speedy Net [ալֆա]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Էջը Գտնված Չէ / Speedy Match [ալֆա]",
                }
                self.expected_404_speedy_is_sorry = "Speedy-ն ցավում է, բայց էջը չի գտնվել։"

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy' and the expected titles use the Armenian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [ալֆա]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [ալֆա]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [ալֆա]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class UserDetailViewAllMainLanguagesUzbekTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Uzbek).
            """

            def set_up(self):
                """
                Sets up the Uzbek date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Tug'ilgan kun sanasi"
                self.birth_year = "Tug'ilgan yili"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12-Sentabr, 1992-yil"
                    self.user_birth_month_day = "12-Sentabr"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12-Sentabr, 1990-yil"
                    self.not_user_birth_month_day = "21-Sentabr"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alpha]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31-Yanvar, 1978-yil"
                    self.user_birth_month_day = "31-Yanvar"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31-Yanvar, 1990-yil"
                    self.not_user_birth_month_day = "30-Yanvar"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alpha]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alpha]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alpha]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Sahifa Topilmadi / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Sahifa Topilmadi / Speedy Match [alpha]",
                }
                self.expected_404_speedy_is_sorry = "Speedy uzr so'raydi, lekin sahifa topilmadi."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz' and the expected titles use the Uzbek format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alpha]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class UserDetailViewAllMainLanguagesTamilTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Tamil).
            """

            def set_up(self):
                """
                Sets up the Tamil date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "பிறந்த தேதி"
                self.birth_year = "பிறந்த ஆண்டு"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "12 செப்டம்பர், 1992"
                    self.user_birth_month_day = "12 செப்டம்பர்"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "12 செப்டம்பர், 1990"
                    self.not_user_birth_month_day = "21 செப்டம்பர்"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [ஆல்பா]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [ஆல்பா]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [ஆல்பா]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "31 ஜனவரி, 1978"
                    self.user_birth_month_day = "31 ஜனவரி"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "31 ஜனவரி, 1990"
                    self.not_user_birth_month_day = "30 ஜனவரி"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [ஆல்பா]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [ஆல்பா]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [ஆல்பா]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "பக்கத்தைக் காணவில்லை / Speedy Net [ஆல்பா]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "பக்கத்தைக் காணவில்லை / Speedy Match [ஆல்பா]",
                }
                self.expected_404_speedy_is_sorry = "Speedy வருந்துகிறது, ஆனால் அந்தப் பக்கம் கிடைக்கவில்லை."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta' and the expected titles use the Tamil format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [ஆல்பா]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [ஆல்பா]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [ஆல்பா]".format(self.user.slug),
                })


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class UserDetailViewAllMainLanguagesLatvianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the user detail view for all main languages (Latvian).
            """

            def set_up(self):
                """
                Sets up the Latvian date-of-birth labels, name/date-of-birth/title expectations for the randomly chosen profile, and the expected 404 title/message.
                """
                super().set_up()
                self.birth_date = "Dzimšanas datums"
                self.birth_year = "Dzimšanas gads"
                if (self.random_choice == 1):
                    self.first_name = "Bar"
                    self.last_name = "Refaeli"
                    self.full_name = "Bar Refaeli"
                    self.user_birth_date = "1992. gada 12. septembris"
                    self.user_birth_month_day = "12. septembris"
                    self.user_birth_year = "1992"
                    self.not_user_birth_date = "1990. gada 12. septembris"
                    self.not_user_birth_month_day = "21. septembris"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Bar Refaeli / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Bar / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "bar-refaeli / Speedy Match [alfa]",
                    }
                elif (self.random_choice == 2):
                    self.first_name = "Doron"
                    self.last_name = "Matalon"
                    self.full_name = "Doron Matalon"
                    self.user_birth_date = "1978. gada 31. janvāris"
                    self.user_birth_month_day = "31. janvāris"
                    self.user_birth_year = "1978"
                    self.not_user_birth_date = "1990. gada 31. janvāris"
                    self.not_user_birth_month_day = "30. janvāris"
                    self.expected_title = {
                        django_settings.SPEEDY_NET_SITE_ID: "Doron Matalon / Speedy Net [alfa]",
                        django_settings.SPEEDY_MATCH_SITE_ID: "Doron / Speedy Match [alfa]",
                    }
                    self.expected_title_no_match = {
                        django_settings.SPEEDY_MATCH_SITE_ID: "doron-matalon / Speedy Match [alfa]",
                    }
                else:
                    raise NotImplementedError("Invalid random choice.")
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Lapa Nav Atrasta / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Lapa Nav Atrasta / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = "Speedy atvainojas, bet lapa nav atrasta."

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv' and the expected titles use the Latvian format.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alfa]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alfa]".format(self.user.slug),
                })


