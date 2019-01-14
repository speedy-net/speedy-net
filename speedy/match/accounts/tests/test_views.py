from django.conf import settings as django_settings

from speedy.core.base.test import tests_settings
from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.factories  import ActiveUserFactory


@only_on_speedy_match
class IndexViewTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user = ActiveUserFactory()

    def test_user_gets_redirected_to_his_matches(self):
        self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
        r = self.client.get(path='/')
        self.assertRedirects(response=r, expected_url='/matches/', target_status_code=200)


