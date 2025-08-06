from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.accounts.test.user_factories import ActiveUserFactory


        class EditViewBaseMixin(TestCaseMixin):
            def get_page_url(self):
                raise NotImplementedError("This method is not implemented in this mixin.")

            def get_template_name(self):
                raise NotImplementedError("This method is not implemented in this mixin.")

            def set_up(self):
                super().set_up()
                self.user = ActiveUserFactory()
                self.page_url = self.get_page_url()
                self.template_name = self.get_template_name()

            def test_anonymous_has_no_access(self):
                r = self.client.get(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next=' + self.page_url, status_code=302, target_status_code=200)

            def test_user_can_access(self):
                self.client.login(username=self.user.username, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name=self.template_name)


        @only_on_speedy_match
        class EditMatchSettingsViewOnlyEnglishTestCase(EditViewBaseMixin, SiteTestCase):
            def get_page_url(self):
                return '/matches/settings/about-my-match/'

            def get_template_name(self):
                return 'matches/settings/about_my_match.html'


        @only_on_speedy_match
        class EditAboutMeViewOnlyEnglishTestCase(EditViewBaseMixin, SiteTestCase):
            def get_page_url(self):
                return '/matches/settings/about-me/'

            def get_template_name(self):
                return 'matches/settings/about_me.html'


