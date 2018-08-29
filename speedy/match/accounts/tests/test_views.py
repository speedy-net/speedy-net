from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from speedy.core.base.test import TestCase, only_on_speedy_match


@only_on_speedy_match
class IndexViewTestCase(TestCase):
    def set_up(self):
        self.user = ActiveUserFactory()

    def test_user_gets_redirected_to_his_matches(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.get('/')
        self.assertRedirects(response=r, expected_url='/matches/', target_status_code=200)


# @only_on_speedy_match
# class ActivateSiteProfileViewTestCase(TestCase):
#     def test_inactive_user_can_request_activation(self):
#         r = self.client.post(self.page_url)
#         self.assertRedirects(response=r, expected_url='/', target_status_code=302)
#         user = User.objects.get(id=self.user.id)
#         self.assertTrue(expr=user.profile.is_active)


