from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from speedy.core.base.test import TestCase, only_on_speedy_net


@only_on_speedy_net
class IndexViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()

    def test_user_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.get('/')
        self.assertRedirects(response=r, expected_url='/me/', target_status_code=302)


