from django.test.client import RequestFactory
from django.views import generic

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software, \
    exclude_on_speedy_match
from ..views import UserMixin


class UserMixinTestView(UserMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return self


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
@exclude_on_speedy_match  # 404s - has to be a match
class UserMixinTextCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
        self.other_user = ActiveUserFactory()

    def test_find_user_by_exact_slug(self):
        view = UserMixinTestView.as_view()(self.factory.get('/look-at-me/some-page/'), slug='look-at-me')
        self.assertEqual(first=view.get_user().id, second=self.user.id)

    def test_find_user_by_username(self):
        r = self.client.get('/l-o-o-k_a_t_m-e/')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_redirect_different_slug_with_extra_slashes(self):
        r = self.client.get('///__l-o-o-k_a_t_m-e...///')
        self.assertRedirects(response=r, expected_url='/__l-o-o-k_a_t_m-e.../', status_code=301, target_status_code=301)
        r = self.client.get('/__l-o-o-k_a_t_m-e.../')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_redirect_same_slug_with_extra_slashes(self):
        r = self.client.get('///look-at-me///')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_find_user_by_upper_case_username(self):
        r = self.client.get('/LOOK-AT-ME/')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_add_trailing_slash(self):
        r = self.client.get('/look-at-me')
        self.assertRedirects(response=r, expected_url='/look-at-me/', status_code=301)

    def test_user_slug_doesnt_exist_returns_404(self):
        r = self.client.get('/l-o-o-k_a_t_m-e-1/')
        self.assertEqual(first=r.status_code, second=404)

