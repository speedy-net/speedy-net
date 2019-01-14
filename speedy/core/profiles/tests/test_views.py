from django.conf import settings as django_settings
from django.test.client import RequestFactory
from django.views import generic

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login, exclude_on_speedy_match
from speedy.core.accounts.tests.test_views import RedirectMeMixin
from speedy.core.profiles.views import UserMixin

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


class UserMixinTestView(UserMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return self


@only_on_sites_with_login
@exclude_on_speedy_match  # 404s - has to be a match
class UserMixinTextCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.factory = RequestFactory()
        self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
        self.other_user = ActiveUserFactory()

    def test_find_user_by_exact_slug(self):
        view = UserMixinTestView.as_view()(self.factory.get('/look-at-me/some-page/'), slug='look-at-me')
        self.assertEqual(first=view.get_user().id, second=self.user.id)

    def test_find_user_by_username(self):
        r = self.client.get(path='/l-o-o-k_a_t_m-e/')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_redirect_different_slug_with_extra_slashes(self):
        r = self.client.get(path='///__l-o-o-k_a_t_m-e...///')
        self.assertRedirects(response=r, expected_url='/__l-o-o-k_a_t_m-e.../', status_code=301, target_status_code=301)
        r = self.client.get(path='/__l-o-o-k_a_t_m-e.../')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_redirect_same_slug_with_extra_slashes(self):
        r = self.client.get(path='///look-at-me///')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_find_user_by_upper_case_username(self):
        r = self.client.get(path='/LOOK-AT-ME/')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_add_trailing_slash(self):
        r = self.client.get(path='/look-at-me')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_user_slug_doesnt_exist_returns_404(self):
        r = self.client.get(path='/l-o-o-k_a_t_m-e-1/')
        self.assertEqual(first=r.status_code, second=404)


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


