from speedy.core.base.test import TestCase, only_on_speedy_match
from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory


@only_on_speedy_match
class IndexViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()

    def test_user_gets_redirected_to_his_matches(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.get('/')
        self.assertRedirects(response=r, expected_url='/matches/', target_status_code=200)


