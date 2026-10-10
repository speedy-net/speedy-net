"""
Test cases for the user mixin of the Speedy Match profiles views.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.profiles.tests.test_views import UserMixinTestCaseMixin


        @only_on_speedy_match
        class UserMixinOnlyEnglishTestCase(UserMixinTestCaseMixin, SiteTestCase):
            """
            Tests that anonymous visitors are redirected to login when requesting a user's profile on Speedy Match, in English only, whether or not the username's slug exists.

            Methods:
                test_redirect_to_login_user_by_username(self): Asserts an anonymous visitor requesting an existing user's profile by username is redirected to login.
                test_redirect_to_login_user_slug_doesnt_exist(self): Asserts an anonymous visitor requesting a profile with a non-existent slug is still redirected to login.
            """
            def test_redirect_to_login_user_by_username(self):
                """
                Asserts an anonymous visitor requesting a user's profile page by username is redirected to the login page with the correct "next" parameter.
                """
                r = self.client.get(path='/l-o-o-k_a_t_m-e/')
                self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e/', status_code=302, target_status_code=200)

            def test_redirect_to_login_user_slug_doesnt_exist(self):
                """
                Asserts an anonymous visitor requesting a profile page with a non-existent slug is still redirected to the login page, before any "user not found" check occurs.
                """
                r = self.client.get(path='/l-o-o-k_a_t_m-e-1/')
                self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e-1/', status_code=302, target_status_code=200)


