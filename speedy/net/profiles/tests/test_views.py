from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net

        from speedy.core.profiles.tests.test_views import UserMixinTextCaseMixin


        @only_on_speedy_net
        class UserMixinOnlyEnglishTestCase(UserMixinTextCaseMixin, SiteTestCase):
            def test_find_user_by_username(self):
                r = self.client.get(path='/l-o-o-k_a_t_m-e/')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_find_user_by_username_with_dots(self):
                r = self.client.get(path='/__l-o-o-k_a_t_m-e.../')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_redirect_different_slug_with_extra_slashes_and_dots(self):
                r = self.client.get(path='///__l-o-o-k_a_t_m-e...///')
                self.assertRedirects(response=r, expected_url='/__l-o-o-k_a_t_m-e.../', status_code=301, target_status_code=301)
                r = self.client.get(path='/__l-o-o-k_a_t_m-e.../')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_redirect_same_slug_with_extra_slashes(self):
                r = self.client.get(path='///look-at-me///')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_find_user_by_upper_case_username(self):
                r = self.client.get(path='/LOOK-AT-ME/')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_add_trailing_slash(self):
                r = self.client.get(path='/look-at-me')
                self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301, target_status_code=200)

            def test_user_slug_doesnt_exist_returns_404(self):
                r = self.client.get(path='/l-o-o-k_a_t_m-e-1/')
                self.assertEqual(first=r.status_code, second=404)

            def test_user_slug_with_invalid_characters_doesnt_work(self):
                paths_to_test = ['/look-at-me,/', '/look-at-me(/', '/look-at-me)/', '/look-at-me=/', '/look-at-me$/']
                for path in paths_to_test:
                    r = self.client.get(path=path)
                    self.assertEqual(first=r.status_code, second=404, msg="{} didn't return 404.".format(path))


