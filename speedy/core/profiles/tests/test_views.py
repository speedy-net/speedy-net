import random
from datetime import date

from django.conf import settings as django_settings
from django.test import override_settings
from django.test.client import RequestFactory
from django.views import generic
from django.utils.html import escape

from friendship.models import Friend

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.accounts.models import UserAccessField, User
    from speedy.core.accounts.tests.test_views import RedirectMeMixin
    from speedy.core.profiles.views import UserMixin

    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    class UserMixinTestView(UserMixin, generic.View):
        def get(self, request, *args, **kwargs):
            return self


    class UserMixinTextCaseMixin(object):
        def set_up(self):
            super().set_up()
            self.factory = RequestFactory()
            self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
            self.other_user = ActiveUserFactory()

        def test_find_user_by_exact_slug(self):
            view = UserMixinTestView.as_view()(self.factory.get('/look-at-me/some-page/'), slug='look-at-me')
            self.assertEqual(first=view.get_user().id, second=self.user.id)


    @only_on_sites_with_login
    class LoggedInUserTestCase(RedirectMeMixin, SiteTestCase):
        def set_up(self):
            super().set_up()
            self.factory = RequestFactory()
            self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
            self.other_user = ActiveUserFactory()

        def test_redirect_to_login_me(self):
            self.assert_me_url_redirects_to_login_url()

        def test_redirect_to_login_me_add_trailing_slash(self):
            r = self.client.get(path='/me')
            self.assertRedirects(response=r, expected_url='/me/', status_code=301, target_status_code=302)
            self.assert_me_url_redirects_to_login_url()

        # ~~~~ TODO: login and test /me/ and user profiles while logged in.


    class UserDetailViewTestCaseMixin(object):
        def set_up(self):
            super().set_up()
            self.random_choice = random.choice([1, 2])
            if (self.random_choice == 1):
                self.user = ActiveUserFactory(first_name_en="Corrin", last_name_en="Gideon", slug="corrin-gideon", date_of_birth=date(year=1992, month=9, day=12), gender=User.GENDER_FEMALE)
                self.user.first_name_he = "קורין"
                self.user.last_name_he = "גדעון"
            elif (self.random_choice == 2):
                self.user = ActiveUserFactory(first_name_en="Jennifer", last_name_en="Connelly", slug="jennifer-connelly", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_FEMALE)
                self.user.first_name_he = "ג'ניפר"
                self.user.last_name_he = "קונלי"
            else:
                raise NotImplementedError()
            self.user.save()
            self.user_profile_url = '/{}/'.format(self.user.slug)
            self.other_user = ActiveUserFactory()

        def deactivate_user(self):
            self.user.is_active = False
            self.user.save()

        def test_user_profile_not_logged_in(self):
            r = self.client.get(path=self.user_profile_url)
            if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                # First, check if the date of birth is not visible.
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member=escape(self.full_name), container=r.content.decode())
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                self.assertNotIn(member=escape(self.birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(self.birth_year), container=r.content.decode())
                self.assertNotIn(member=escape(self.user_birth_date), container=r.content.decode())
                # Now, check if the date of birth is visible.
                self.user.access_dob_day_month = UserAccessField.ACCESS_ANYONE
                self.user.access_dob_year = UserAccessField.ACCESS_ANYONE
                self.user.save()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(self.birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(self.birth_year), container=r.content.decode())
                self.assertIn(member=escape(self.user_birth_year), container=r.content.decode())
                self.assertIn(member=escape(self.user_birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(self.not_user_birth_date), container=r.content.decode())
            elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                expected_url = '/login/?next={}'.format(self.user_profile_url)
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
            else:
                raise NotImplementedError()
            self.deactivate_user()
            r = self.client.get(path=self.user_profile_url)
            if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                self.assertEqual(first=r.status_code, second=404)
                self.assertNotIn(member="<title>", container=r.content.decode())
            elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                expected_url = '/login/?next={}'.format(self.user_profile_url)
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
            else:
                raise NotImplementedError()

        def test_user_own_profile_logged_in(self):
            self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.user_profile_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertIn(member=escape(self.first_name), container=r.content.decode())
            if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                self.assertIn(member=escape(self.full_name), container=r.content.decode())
            elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                self.assertNotIn(member=escape(self.full_name), container=r.content.decode())
            else:
                raise NotImplementedError()
            self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
            self.assertIn(member=escape(self.birth_date), container=r.content.decode())
            self.assertNotIn(member=escape(self.birth_year), container=r.content.decode())
            self.assertIn(member=escape(self.user_birth_year), container=r.content.decode())
            self.assertIn(member=escape(self.user_birth_date), container=r.content.decode())
            self.assertNotIn(member=escape(self.not_user_birth_date), container=r.content.decode())
            self.deactivate_user()
            r = self.client.get(path=self.user_profile_url)
            if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                # ~~~~ TODO: should redirect to '/welcome/'.
                self.assertEqual(first=r.status_code, second=404)
                self.assertNotIn(member="<title>", container=r.content.decode())
            elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                expected_url = '/welcome/'
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
            else:
                raise NotImplementedError()

        def test_user_profile_month_day_format_from_friend(self):
            # First, check if only the day and month are visible.
            self.user.access_dob_day_month = UserAccessField.ACCESS_FRIENDS
            self.user.save()
            Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
            self.assertTrue(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
            self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.user_profile_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertIn(member=escape(self.first_name), container=r.content.decode())
            if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                self.assertIn(member=escape(self.full_name), container=r.content.decode())
            elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                self.assertNotIn(member=escape(self.full_name), container=r.content.decode())
            else:
                raise NotImplementedError()
            self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
            self.assertIn(member=escape(self.birth_date), container=r.content.decode())
            self.assertNotIn(member=escape(self.birth_year), container=r.content.decode())
            self.assertIn(member=escape(self.user_birth_month_day), container=r.content.decode())
            self.assertNotIn(member=escape(self.user_birth_date), container=r.content.decode())
            self.assertNotIn(member=escape(self.not_user_birth_month_day), container=r.content.decode())
            self.assertNotIn(member=escape(self.not_user_birth_date), container=r.content.decode())
            # Then, check if all the birth date is visible.
            self.user.access_dob_year = UserAccessField.ACCESS_FRIENDS
            self.user.save()
            r = self.client.get(path=self.user_profile_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
            self.assertIn(member=escape(self.birth_date), container=r.content.decode())
            self.assertNotIn(member=escape(self.birth_year), container=r.content.decode())
            self.assertIn(member=escape(self.user_birth_month_day), container=r.content.decode())
            self.assertIn(member=escape(self.user_birth_year), container=r.content.decode())
            self.assertIn(member=escape(self.user_birth_date), container=r.content.decode())
            self.assertNotIn(member=escape(self.not_user_birth_month_day), container=r.content.decode())
            self.assertNotIn(member=escape(self.not_user_birth_date), container=r.content.decode())
            # Then, check if only the year is visible.
            self.user.access_dob_day_month = UserAccessField.ACCESS_ME
            self.user.save()
            r = self.client.get(path=self.user_profile_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
            self.assertNotIn(member=escape(self.birth_date), container=r.content.decode())
            self.assertIn(member=escape(self.birth_year), container=r.content.decode())
            self.assertNotIn(member=escape(self.user_birth_month_day), container=r.content.decode())
            self.assertIn(member=escape(self.user_birth_year), container=r.content.decode())
            self.assertNotIn(member=escape(self.user_birth_date), container=r.content.decode())
            self.assertNotIn(member=escape(self.not_user_birth_month_day), container=r.content.decode())
            self.assertNotIn(member=escape(self.not_user_birth_date), container=r.content.decode())
            # Then logout and check that nothing from the date of birth is visible on Speedy Net.
            # On Speedy Match, the profile is not visible to visitors at all.
            self.client.logout()
            r = self.client.get(path=self.user_profile_url)
            if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                self.assertNotIn(member=escape(self.birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(self.birth_year), container=r.content.decode())
                self.assertNotIn(member=escape(self.user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(self.user_birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(self.not_user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(self.not_user_birth_date), container=r.content.decode())
                # And then, check if only the day and month are visible again.
                self.user.access_dob_day_month = UserAccessField.ACCESS_ANYONE
                self.user.save()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(self.birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(self.birth_year), container=r.content.decode())
                self.assertIn(member=escape(self.user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(self.user_birth_date), container=r.content.decode())
                self.assertNotIn(member=escape(self.not_user_birth_month_day), container=r.content.decode())
                self.assertNotIn(member=escape(self.not_user_birth_date), container=r.content.decode())
            elif (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                expected_url = '/login/?next={}'.format(self.user_profile_url)
                self.assertRedirects(response=r, expected_url=expected_url, status_code=302, target_status_code=200)
            else:
                raise NotImplementedError()
            self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
            if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                self.other_user.speedy_match_profile.min_age_to_match = 80
                self.other_user.save_user_and_profile()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=404)
                self.assertNotIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_title_no_match[self.site.id])), container=r.content.decode())
                self.other_user.speedy_match_profile.min_age_to_match = 36
                self.other_user.save_user_and_profile()
                r = self.client.get(path=self.user_profile_url)
                if (self.random_choice == 1):
                    self.assertEqual(first=self.user.slug, second="corrin-gideon")
                    self.assertEqual(first=r.status_code, second=404)
                    self.assertNotIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member="<title>{}</title>".format(escape(self.expected_title_no_match[self.site.id])), container=r.content.decode())
                elif (self.random_choice == 2):
                    self.assertEqual(first=self.user.slug, second="jennifer-connelly")
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertNotIn(member="<title>{}</title>".format(escape(self.expected_title_no_match[self.site.id])), container=r.content.decode())
                    self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                else:
                    raise NotImplementedError()
                self.other_user.speedy_match_profile.min_age_to_match = 12
                self.other_user.save_user_and_profile()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertNotIn(member="<title>{}</title>".format(escape(self.expected_title_no_match[self.site.id])), container=r.content.decode())
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
            self.deactivate_user()
            r = self.client.get(path=self.user_profile_url)
            self.assertEqual(first=r.status_code, second=404)
            self.assertNotIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
            if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                self.assertNotIn(member="<title>{}</title>".format(escape(self.expected_title_no_match[self.site.id])), container=r.content.decode())
            self.assertNotIn(member="<title>", container=r.content.decode())

        def test_user_profile_deactivated_user_from_friend(self):
            Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
            self.assertTrue(expr=Friend.objects.are_friends(user1=self.user, user2=self.other_user))
            self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
            self.deactivate_user()
            r = self.client.get(path=self.user_profile_url)
            self.assertEqual(first=r.status_code, second=404)
            self.assertNotIn(member="<title>", container=r.content.decode())

    @only_on_sites_with_login
    class UserDetailViewEnglishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
        def set_up(self):
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
                    django_settings.SPEEDY_MATCH_SITE_ID: "Corrin / Speedy Match [alpha]",
                }
                self.expected_title_no_match = {
                    django_settings.SPEEDY_MATCH_SITE_ID: "corrin-gideon / Speedy Match [alpha]",
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
                    django_settings.SPEEDY_MATCH_SITE_ID: "Jennifer / Speedy Match [alpha]",
                }
                self.expected_title_no_match = {
                    django_settings.SPEEDY_MATCH_SITE_ID: "jennifer-connelly / Speedy Match [alpha]",
                }
            else:
                raise NotImplementedError()

        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')
            self.assertDictEqual(d1=self.expected_title, d2={
                django_settings.SPEEDY_NET_SITE_ID: "{} / Speedy Net [alpha]".format(self.full_name),
                django_settings.SPEEDY_MATCH_SITE_ID: "{} / Speedy Match [alpha]".format(self.first_name),
            })


    @only_on_sites_with_login
    @override_settings(LANGUAGE_CODE='he')
    class UserDetailViewHebrewTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
        def set_up(self):
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
                raise NotImplementedError()

        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')
            self.assertDictEqual(d1=self.expected_title, d2={
                django_settings.SPEEDY_NET_SITE_ID: "{} / ספידי נט [אלפא]".format(self.full_name),
                django_settings.SPEEDY_MATCH_SITE_ID: "{} / ספידי מץ' [אלפא]".format(self.first_name),
            })


