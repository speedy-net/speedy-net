from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_match
from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory


class EditViewBaseMixin(object):
    def get_page_url(self):
        raise NotImplementedError()

    def get_template_name(self):
        raise NotImplementedError()

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.page_url = self.get_page_url()
        self.template_name = self.get_template_name()

    def test_anonymous_has_no_access(self):
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url)

    def test_user_can_access(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name=self.template_name)


@only_on_speedy_match
class EditMatchSettingsViewTestCase(EditViewBaseMixin, SiteTestCase):
    def get_page_url(self):
        return '/matches/settings/'

    def get_template_name(self):
        return 'matches/settings/matches.html'


@only_on_speedy_match
class EditAboutMeViewTestCase(EditViewBaseMixin, SiteTestCase):
    def get_page_url(self):
        return '/matches/settings/about-me/'

    def get_template_name(self):
        return 'matches/settings/about_me.html'


