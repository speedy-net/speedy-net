"""
Test cases for the user mixin of the Speedy Net profiles views.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net

        from speedy.core.profiles.tests.test_views import UserMixinTestCaseMixin


        @only_on_speedy_net
        class UserMixinOnlyEnglishTestCase(UserMixinTestCaseMixin, SiteTestCase):
            """
            Test resolving user profile pages by slug on Speedy Net (English only, slug resolution doesn't depend on the language).

            Methods:
                test_find_user_by_username(self): Verify a user can be found and redirected to the canonical slug by username.
                test_find_user_by_username_with_dots(self): Verify a user can be found and redirected to the canonical slug when the requested slug contains extra underscores and dots.
                test_redirect_different_slug_with_extra_slashes_and_dots(self): Verify extra slashes are stripped first, then the slug is normalized to the canonical one.
                test_redirect_same_slug_with_extra_slashes(self): Verify extra slashes around an already-canonical slug redirect to the canonical path.
                test_find_user_by_upper_case_username(self): Verify a user can be found and redirected to the canonical slug by an upper-case username.
                test_add_trailing_slash(self): Verify a path missing the trailing slash redirects to the canonical path with a trailing slash.
                test_user_slug_doesnt_exist_returns_404(self): Verify a non-existent user slug returns a 404 response.
                test_user_slug_with_invalid_characters_doesnt_work(self): Verify slugs containing invalid characters return a 404 response.
            """

            def test_find_user_by_username(self):
                """
                Verify a user can be found and redirected to the canonical slug by username.
                """
                r = self.client.get(path='/l-o-o-k_a_t_m-e/')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_find_user_by_username_with_dots(self):
                """
                Verify a user can be found and redirected to the canonical slug when the requested slug contains extra underscores and dots.
                """
                r = self.client.get(path='/__l-o-o-k_a_t_m-e.../')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_redirect_different_slug_with_extra_slashes_and_dots(self):
                """
                Verify extra slashes are stripped first, then the slug is normalized to the canonical one.
                """
                r = self.client.get(path='///__l-o-o-k_a_t_m-e...///')
                self.assertRedirects(response=r, expected_url='/__l-o-o-k_a_t_m-e.../', status_code=301, target_status_code=301)
                r = self.client.get(path='/__l-o-o-k_a_t_m-e.../')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_redirect_same_slug_with_extra_slashes(self):
                """
                Verify extra slashes around an already-canonical slug redirect to the canonical path.
                """
                r = self.client.get(path='///look-at-me///')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_find_user_by_upper_case_username(self):
                """
                Verify a user can be found and redirected to the canonical slug by an upper-case username.
                """
                r = self.client.get(path='/LOOK-AT-ME/')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_add_trailing_slash(self):
                """
                Verify a path missing the trailing slash redirects to the canonical path with a trailing slash.
                """
                r = self.client.get(path='/look-at-me')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_user_slug_doesnt_exist_returns_404(self):
                """
                Verify a non-existent user slug returns a 404 response.
                """
                r = self.client.get(path='/l-o-o-k_a_t_m-e-1/')
                self.assertEqual(first=r.status_code, second=404)

            def test_user_slug_with_invalid_characters_doesnt_work(self):
                """
                Verify slugs containing invalid characters return a 404 response.
                """
                paths_to_test = ['/look-at-me,/', '/look-at-me(/', '/look-at-me)/', '/look-at-me=/', '/look-at-me$/']
                for path in paths_to_test:
                    r = self.client.get(path=path)
                    self.assertEqual(first=r.status_code, second=404, msg="{} didn't return 404.".format(path))


