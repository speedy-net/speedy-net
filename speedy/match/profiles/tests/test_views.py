from django.test.client import RequestFactory

from speedy.core.base.test import TestCase, only_on_speedy_match
from speedy.core.accounts.tests.test_factories import ActiveUserFactory


@only_on_speedy_match
class UserMixinTextCase(TestCase):
    def set_up(self):
        self.factory = RequestFactory()
        self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
        self.other_user = ActiveUserFactory()

    def test_redirect_to_login_user_by_username(self):
        r = self.client.get(path='/l-o-o-k_a_t_m-e/')
        self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e/', status_code=302)

    def test_redirect_to_login_user_slug_doesnt_exist(self):
        r = self.client.get(path='/l-o-o-k_a_t_m-e-1/')
        self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e-1/', status_code=302)


