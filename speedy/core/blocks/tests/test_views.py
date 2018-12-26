from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login
from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from ..models import Block


@only_on_sites_with_login
class BlockListViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.third_user = ActiveUserFactory()
        self.page_url = '/{}/blocks/'.format(self.user.slug)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_other_user_has_no_access(self):
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        r = self.client.get(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_has_access(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='blocks/block_list.html')


@only_on_sites_with_login
class BlockViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.page_url = '/{}/blocks/block/'.format(self.other_user.slug)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_cannot_block_self(self):
        self.client.login(username=self.other_user.slug, password=USER_PASSWORD)
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_block_other_user(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Block.objects.count(), second=0)
        r = self.client.post(path=self.page_url)
        self.assertEqual(first=Block.objects.count(), second=1)
        block = Block.objects.first()
        self.assertEqual(first=block.blocker_id, second=self.user.id)
        self.assertEqual(first=block.blocked_id, second=self.other_user.id)
        self.assertRedirects(response=r, expected_url='/{}/'.format(self.other_user.slug), target_status_code=404)


@only_on_sites_with_login
class UnblockViewTestCase(SiteTestCase):
    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.page_url = '/{}/blocks/unblock/'.format(self.other_user.slug)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(path=self.page_url)
        self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url))

    def test_user_can_unblock_other_user(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        Block.objects.block(blocker=self.user, blocked=self.other_user)
        self.assertEqual(first=Block.objects.count(), second=1)
        r = self.client.post(path=self.page_url)
        self.assertEqual(first=Block.objects.count(), second=0)
        self.assertRedirects(response=r, expected_url='/{}/'.format(self.other_user.slug))


