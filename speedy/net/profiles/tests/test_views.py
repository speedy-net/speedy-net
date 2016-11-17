from speedy.core.test import TestCase
from django.test.client import RequestFactory
from django.views import generic

from speedy.net.accounts.tests.test_factories import UserFactory
from ..views import UserMixin


class UserMixinTestView(UserMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return self


class UserMixinTextCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory(slug='look-at-me',
                                username='lookatme')
        self.other_user = UserFactory()

    def test_find_user_by_exact_slug(self):
        view = UserMixinTestView.as_view()(self.factory.get('/look-at-me/some-page/'), slug='look-at-me')
        self.assertEqual(view.get_user().id, self.user.id)

    def test_find_user_by_username(self):
        r = self.client.get('/l-o-o-k_a_t_m-e/')
        self.assertRedirects(r, '/look-at-me/')
