from django.conf import settings as django_settings
from django.test.client import RequestFactory

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.tests.test_factories import ActiveUserFactory


@only_on_speedy_match
class UserMixinTextCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.factory = RequestFactory()
        self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
        self.other_user = ActiveUserFactory()

    def test_redirect_to_login_user_by_username(self):
        r = self.client.get(path='/l-o-o-k_a_t_m-e/')
        self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e/', status_code=302)

    def test_redirect_to_login_user_slug_doesnt_exist(self):
        r = self.client.get(path='/l-o-o-k_a_t_m-e-1/')
        self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e-1/', status_code=302)


