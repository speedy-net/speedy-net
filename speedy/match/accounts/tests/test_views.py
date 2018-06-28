from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software, exclude_on_speedy_net


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
@exclude_on_speedy_net
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

# from datetime import date
#
# from django.conf import settings
# from django.contrib.sites.models import Site
# from django.core import mail
#
# from speedy.core.accounts.models import Entity, User, UserEmailAddress, SiteProfileBase
# from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
# from speedy.core.accounts.tests.test_factories import ActiveUserFactory, UserEmailAddressFactory, InactiveUserFactory
#
#
# class ActivateSiteProfileViewTestCase(TestCase):
#
#     def test_inactive_user_can_request_activation(self):
#         r = self.client.post(self.page_url)
#         self.assertRedirects(response=r, expected_url='/', target_status_code=302)
#         user = User.objects.get(id=self.user.id)
#         self.assertTrue(expr=user.profile.is_active)
