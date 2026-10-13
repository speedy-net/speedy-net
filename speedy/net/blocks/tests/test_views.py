"""
Test cases for the views of the blocks app of Speedy Net: the list of blocked users.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test import tests_settings
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_speedy_net

    from speedy.core.accounts.test.user_factories import ActiveUserFactory

    from speedy.core.blocks.models import Block


    @only_on_speedy_net
    class BlockedUsersListViewOnlyEnglishTestCase(SiteTestCase):
        """
        Tests the content and pagination of the blocked users list page of Speedy Net.

        Methods:
            set_up(self): Creates three active users and builds the blocked users list page URL for the first user.
            test_empty_list_when_user_is_not_blocking_anybody(self): Asserts the list is empty when the user is not blocking anybody.
            test_list_contains_only_users_blocked_by_the_user(self): Asserts the list contains only the users blocked by the list's owner.
            test_blocked_users_list_is_paginated(self): Asserts the list is paginated, with 24 blocked users in the first page.
        """

        def set_up(self):
            """
            Creates three active users and builds the blocked users list page URL for the first user.
            """
            super().set_up()
            self.first_user = ActiveUserFactory()
            self.second_user = ActiveUserFactory()
            self.third_user = ActiveUserFactory()
            self.page_url = '/{}/blocked-users/'.format(self.first_user.slug)

        def test_empty_list_when_user_is_not_blocking_anybody(self):
            """
            Asserts the blocked users list page of a user who is not blocking anybody renders successfully, with an empty list.
            """
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertTemplateUsed(response=r, template_name='blocks/block_list.html')
            self.assertEqual(first=len(r.context['block_list']), second=0)

        def test_list_contains_only_users_blocked_by_the_user(self):
            """
            Asserts the blocked users list contains only the users blocked by the list's owner, and not users blocked by other users or users who blocked the owner.
            """
            Block.objects.block(blocker=self.first_user, blocked=self.second_user)
            Block.objects.block(blocker=self.third_user, blocked=self.second_user)
            Block.objects.block(blocker=self.third_user, blocked=self.first_user)
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertListEqual(list1=[block.blocked_id for block in r.context['block_list']], list2=[self.second_user.id])
            self.assertListEqual(list1=[block.blocker_id for block in r.context['block_list']], list2=[self.first_user.id])

        def test_blocked_users_list_is_paginated(self):
            """
            Asserts the blocked users list is paginated, with 24 blocked users in the first page and the remaining blocked user in the second page.
            """
            blocked_users = [ActiveUserFactory() for _i in range(25)]
            for blocked_user in blocked_users:
                Block.objects.block(blocker=self.first_user, blocked=blocked_user)
            self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
            r = self.client.get(path=self.page_url)
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['block_list']), second=24)
            self.assertIs(expr1=r.context['is_paginated'], expr2=True)
            r = self.client.get(path=self.page_url, data={'page': 2})
            self.assertEqual(first=r.status_code, second=200)
            self.assertEqual(first=len(r.context['block_list']), second=1)


