from speedy.core.base.test import TestCase, only_on_speedy_match
from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory


class EditViewBaseMixin(object):
    def set_up(self):
        self.user = ActiveUserFactory()

    def test_anonymous_has_no_access(self):
        r = self.client.get(self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_access(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name=self.template_name)


@only_on_speedy_match
class EditMatchSettingsViewTestCase(EditViewBaseMixin, TestCase):
    def set_up(self):
        super().set_up()
        self.page_url = '/matches/settings/'
        self.template_name = 'matches/settings/matches.html'


@only_on_speedy_match
class EditAboutMeViewTestCase(EditViewBaseMixin, TestCase):
    def set_up(self):
        super().set_up()
        self.page_url = '/matches/settings/about-me/'
        self.template_name = 'matches/settings/about_me.html'


