from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, only_on_speedy_match


@only_on_speedy_match
class IndexViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()

    def test_visitor_gets_registration_page(self):
        r = self.client.get('/')
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='accounts/registration.html')

    def test_user_gets_redirected_to_his_profile(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get('/')
        self.assertRedirects(response=r, expected_url='/matches/', target_status_code=200)


# @only_on_speedy_match
# class ActivateSiteProfileViewTestCase(TestCase):
#
#     def test_inactive_user_can_request_activation(self):
#         r = self.client.post(self.page_url)
#         self.assertRedirects(response=r, expected_url='/', target_status_code=302)
#         user = User.objects.get(id=self.user.id)
#         self.assertTrue(expr=user.profile.is_active)
