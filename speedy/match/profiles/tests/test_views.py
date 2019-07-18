from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match

if (django_settings.LOGIN_ENABLED):
    from speedy.core.profiles.tests.test_views import UserMixinTextCaseMixin


    @only_on_speedy_match
    class UserMixinTextCase(UserMixinTextCaseMixin, SiteTestCase):
        def test_redirect_to_login_user_by_username(self):
            r = self.client.get(path='/l-o-o-k_a_t_m-e/')
            self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e/', status_code=302, target_status_code=200)

        def test_redirect_to_login_user_slug_doesnt_exist(self):
            r = self.client.get(path='/l-o-o-k_a_t_m-e-1/')
            self.assertRedirects(response=r, expected_url='/login/?next=/l-o-o-k_a_t_m-e-1/', status_code=302, target_status_code=200)


