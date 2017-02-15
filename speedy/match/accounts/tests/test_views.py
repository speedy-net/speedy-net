# from datetime import date
#
# from django.conf import settings
# from django.contrib.sites.models import Site
# from django.core import mail
#
# from speedy.core.accounts.models import Entity, User, UserEmailAddress, SiteProfileBase
# from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
# from speedy.core.base.test import exclude_on_speedy_match
# from speedy.core.accounts.tests.test_factories import UserFactory, UserEmailAddressFactory, InactiveUserFactory
#
#
# class ActivateSiteProfileViewTestCase(TestCase):
#
#     def test_inactive_user_can_request_activation(self):
#         r = self.client.post(self.page_url)
#         self.assertRedirects(response=r, expected_url='/', target_status_code=302)
#         user = User.objects.get(id=self.user.id)
#         self.assertTrue(expr=user.profile.is_active)
