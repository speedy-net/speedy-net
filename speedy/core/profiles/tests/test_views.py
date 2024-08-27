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
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.tests.test_views import RedirectMeMixin

        from speedy.core.accounts.models import User
        from speedy.core.accounts.fields import UserAccessField
        from speedy.core.profiles.views import UserMixin


        class UserMixinTestView(UserMixin, generic.View):
            def get(self, request, *args, **kwargs):
                return self


        class UserMixinTestCaseMixin(object):
            def set_up(self):
                super().set_up()
                self.factory = RequestFactory()
                self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
                self.other_user = ActiveUserFactory()

            def test_find_user_by_exact_slug(self):
                request = self.factory.get('/look-at-me/some-page/')
                request.user = AnonymousUser()
                view = UserMixinTestView.as_view()(request=request, slug='look-at-me')
                self.assertEqual(first=view.get_user().id, second=self.user.id)


        @only_on_sites_with_login
        class LoggedInUserOnlyEnglishTestCase(RedirectMeMixin, SiteTestCase):
            def set_up(self):
                super().set_up()
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
                    if (self.language_code in {'en', 'he', 'fr', 'de'}):
                        # Check names in English alphabet and in Hebrew alphabet.
                        self.user = ActiveUserFactory(first_name_en="Corrin", last_name_en="Gideon", slug="corrin-gideon", date_of_birth=date(year=1992, month=9, day=12), gender=User.GENDER_FEMALE)
                        self.user.first_name_he = "קורין"
                        self.user.last_name_he = "גדעון"
                    elif (self.language_code in {'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi'}):
                        # Check names in English alphabet.
                        self.user = ActiveUserFactory(first_name_en="Bar", last_name_en="Refaeli", slug="bar-refaeli", date_of_birth=date(year=1992, month=9, day=12), gender=User.GENDER_FEMALE)
                    else:
                        raise NotImplementedError()
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
                    elif (self.language_code in {'de', 'nl', 'sv', 'ko', 'fi'}):
                        # Check names in English alphabet.
                        self.user = ActiveUserFactory(first_name_en="Doron", last_name_en="Matalon", slug="doron-matalon", date_of_birth=date(year=1978, month=1, day=31), gender=User.GENDER_FEMALE)
                    else:
                        raise NotImplementedError()
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
                    self.assertIn(member="<title>{}</title>".format(escape(self.expected_404_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member=escape(self.expected_404_speedy_is_sorry), container=r.content.decode())
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
                    self.assertIn(member="<title>{}</title>".format(escape(self.expected_404_title[self.site.id])), container=r.content.decode())
                    self.assertIn(member=escape(self.expected_404_speedy_is_sorry), container=r.content.decode())
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
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.user, user2=self.other_user), expr2=True)
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
                        if (self.language_code in {'en', 'he', 'fr', 'de'}):
                            self.assertEqual(first=self.user.slug, second="corrin-gideon")
                        elif (self.language_code in {'es', 'pt', 'it', 'nl', 'sv', 'ko', 'fi'}):
                            self.assertEqual(first=self.user.slug, second="bar-refaeli")
                        else:
                            raise NotImplementedError()
                        self.assertEqual(first=r.status_code, second=404)
                        self.assertNotIn(member="<title>{}</title>".format(escape(self.expected_title[self.site.id])), container=r.content.decode())
                        self.assertIn(member="<title>{}</title>".format(escape(self.expected_title_no_match[self.site.id])), container=r.content.decode())
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
                        elif (self.language_code in {'de', 'nl', 'sv', 'ko', 'fi'}):
                            self.assertEqual(first=self.user.slug, second="doron-matalon")
                        else:
                            raise NotImplementedError()
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
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_404_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(self.expected_404_speedy_is_sorry), container=r.content.decode())

            def test_user_profile_deactivated_user_from_friend(self):
                Friend.objects.add_friend(from_user=self.user, to_user=self.other_user).accept()
                self.assertIs(expr1=Friend.objects.are_friends(user1=self.user, user2=self.other_user), expr2=True)
                self.client.login(username=self.other_user.slug, password=tests_settings.USER_PASSWORD)
                self.deactivate_user()
                r = self.client.get(path=self.user_profile_url)
                self.assertEqual(first=r.status_code, second=404)
                self.assertIn(member="<title>{}</title>".format(escape(self.expected_404_title[self.site.id])), container=r.content.decode())
                self.assertIn(member=escape(self.expected_404_speedy_is_sorry), container=r.content.decode())


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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Page Not Found / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Page Not Found / Speedy Match",
                }
                self.expected_404_speedy_is_sorry = 'Speedy is sorry, but the page is not found.'

            def validate_all_values(self):
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
        class UserDetailViewFrenchTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Page Non Trouvée / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Page Non Trouvée / Speedy Match [alpha]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy est désolée, mais la page n’a pas été trouvée.'

            def validate_all_values(self):
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
        class UserDetailViewGermanTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Seite Nicht Gefunden / Speedy Net [alpha]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Seite Nicht Gefunden / Speedy Match [alpha]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy tut es leid, aber die Seite kann nicht gefunden werden.'

            def validate_all_values(self):
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
        class UserDetailViewSpanishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Página No Encontrada / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Página No Encontrada / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy lo siente, pero no se encuentra la página.'

            def validate_all_values(self):
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
        class UserDetailViewPortugueseTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Página Não Encontrada / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Página Não Encontrada / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'A Speedy lamenta, mas a página não foi encontrada.'

            def validate_all_values(self):
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
        class UserDetailViewItalianTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Pagina Non Trovata / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Pagina Non Trovata / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy è spiacente, ma la pagina non è stata trovata.'

            def validate_all_values(self):
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
        class UserDetailViewDutchTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Pagina Niet Gevonden / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Pagina Niet Gevonden / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Het spijt Speedy, maar de pagina is niet gevonden.'

            def validate_all_values(self):
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
        @override_settings(LANGUAGE_CODE='sv')
        class UserDetailViewSwedishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Sidan Kunde Inte Hittas / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Sidan Kunde Inte Hittas / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy beklagar, men sidan har inte hittats.'

            def validate_all_values(self):
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
        @override_settings(LANGUAGE_CODE='ko')
        class UserDetailViewKoreanTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "페이지를 찾을 수 없습니다. / Speedy Net [알파]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "페이지를 찾을 수 없습니다. / Speedy Match [알파]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy에서 죄송하게 생각합니다만, 해당 페이지를 찾을 수 없습니다.'

            def validate_all_values(self):
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
        @override_settings(LANGUAGE_CODE='fi')
        class UserDetailViewFinnishTestCase(UserDetailViewTestCaseMixin, SiteTestCase):
            def set_up(self):
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
                    raise NotImplementedError()
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "Sivua Ei Löydy / Speedy Net [alfa]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "Sivua Ei Löydy / Speedy Match [alfa]",
                }
                self.expected_404_speedy_is_sorry = 'Speedy pahoittelee, mutta sivua ei löydy.'

            def validate_all_values(self):
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
                self.expected_404_title = {
                    django_settings.SPEEDY_NET_SITE_ID: "הדף לא נמצא / ספידי נט [אלפא]",
                    django_settings.SPEEDY_MATCH_SITE_ID: "הדף לא נמצא / ספידי מץ' [אלפא]",
                }
                self.expected_404_speedy_is_sorry = 'ספידי מצטערת, אבל הדף לא נמצא.'

            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')
                self.assertDictEqual(d1=self.expected_title, d2={
                    django_settings.SPEEDY_NET_SITE_ID: "{} / ספידי נט [אלפא]".format(self.full_name),
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / ספידי מץ' [אלפא]".format(self.first_name),
                })
                self.assertDictEqual(d1=self.expected_title_no_match, d2={
                    django_settings.SPEEDY_MATCH_SITE_ID: "{} / ספידי מץ' [אלפא]".format(self.user.slug),
                })


