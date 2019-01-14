from django.conf import settings as django_settings

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login, exclude_on_speedy_match
from speedy.core.blocks.models import Block

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


@only_on_sites_with_login
class ViewProfileTestCase(SiteTestCase):
    def set_up(self):
        super().set_up()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()

    ##### @exclude_on_speedy_match # ~~~~ TODO: check test on speedy.match
    def test_has_access(self):
        self.assertTrue(expr=self.user.has_perm(perm='accounts.view_profile', obj=self.other_user))
        self.assertTrue(expr=self.other_user.has_perm(perm='accounts.view_profile', obj=self.user))

    ##### @exclude_on_speedy_match # ~~~~ TODO: check test on speedy.match
    def test_has_no_access_if_blocked(self):
        Block.objects.block(blocker=self.other_user, blocked=self.user)
        self.assertFalse(expr=self.user.has_perm(perm='accounts.view_profile', obj=self.other_user))
        self.assertFalse(expr=self.other_user.has_perm(perm='accounts.view_profile', obj=self.user))


