from speedy.core.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from .models import Block


class BlockListViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.third_user = UserFactory()
        self.page_url = '/{}/blocks/'.format(self.user.slug)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_other_user_has_no_access(self):
        self.client.login(username=self.other_user.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_has_access(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'blocks/block_list.html')


class BlockViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/blocks/block/'.format(self.other_user.slug)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_cannot_block_self(self):
        self.client.login(username=self.other_user.slug, password='111')
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_can_block_other_user(self):
        self.client.login(username=self.user.slug, password='111')
        self.assertEqual(Block.objects.count(), 0)
        r = self.client.post(self.page_url)
        self.assertEqual(Block.objects.count(), 1)
        block = Block.objects.first()
        self.assertEqual(block.blocker_id, self.user.id)
        self.assertEqual(block.blockee_id, self.other_user.id)
        self.assertRedirects(r, '/{}/'.format(self.other_user.slug))


class UnblockViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.page_url = '/{}/blocks/unblock/'.format(self.other_user.slug)

    def test_visitor_has_no_access(self):
        self.client.logout()
        r = self.client.post(self.page_url)
        self.assertRedirects(r, '/login/?next={}'.format(self.page_url))

    def test_user_can_unblock_other_user(self):
        self.client.login(username=self.user.slug, password='111')
        Block.objects.block(self.user, self.other_user)
        self.assertEqual(Block.objects.count(), 1)
        r = self.client.post(self.page_url)
        self.assertEqual(Block.objects.count(), 0)
        self.assertRedirects(r, '/{}/'.format(self.other_user.slug))
