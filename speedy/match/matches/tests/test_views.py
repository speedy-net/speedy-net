from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from speedy.core.base.test import TestCase, only_on_speedy_match


@only_on_speedy_match
class EditMatchSettingsViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.page_url = '/matches/settings/'

    def test_anonymous_has_no_access(self):
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_access(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='matches/settings/matches.html')


@only_on_speedy_match
class EditMatchSettingsViewTestCase(TestCase):
    def setUp(self):
        self.user = ActiveUserFactory()
        self.page_url = '/matches/settings/about-me/'

    def test_anonymous_has_no_access(self):
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_access(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='matches/settings/about_me.html')


