from django.conf import settings as django_settings
from django.test.client import RequestFactory
from django.views import generic

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.accounts.tests.test_views import RedirectMeMixin
    from speedy.core.profiles.views import UserMixin

    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    class UserMixinTestView(UserMixin, generic.View):
        def get(self, request, *args, **kwargs):
            return self


    class UserMixinTextCaseMixin(object):
        def set_up(self):
            super().set_up()
            self.factory = RequestFactory()
            self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
            self.other_user = ActiveUserFactory()

        def test_find_user_by_exact_slug(self):
            view = UserMixinTestView.as_view()(self.factory.get('/look-at-me/some-page/'), slug='look-at-me')
            self.assertEqual(first=view.get_user().id, second=self.user.id)


    @only_on_sites_with_login
    class LoggedInUserTestCase(RedirectMeMixin, SiteTestCase):
        def set_up(self):
            super().set_up()
            self.factory = RequestFactory()
            self.user = ActiveUserFactory(slug='look-at-me', username='lookatme')
            self.other_user = ActiveUserFactory()

        def test_redirect_to_login_me(self):
            self.assert_me_url_redirects_to_login_url()

        def test_redirect_to_login_me_add_trailing_slash(self):
            r = self.client.get(path='/me')
            self.assertRedirects(response=r, expected_url='/me/', status_code=301, target_status_code=302)
            self.assert_me_url_redirects_to_login_url()

        # ~~~~ TODO: login and test /me/ and user profiles while logged in.


