"""
Test cases for the views of the blocks app of Speedy Core: the list of blocked users and blocking and unblocking users.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.blocks.models import Block


        @only_on_sites_with_login
        class BlockedUsersListViewOnlyEnglishTestCase(SiteTestCase):
            """
            Test view in Speedy Net. Speedy Match should always return 404.
            """
            def set_up(self):
                """
                Creates three active users and builds the blocked-users list page URL for the first user.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.third_user = ActiveUserFactory()
                self.page_url = '/{}/blocked-users/'.format(self.first_user.slug)

            def test_visitor_has_no_access(self):
                """
                Asserts an anonymous visitor is redirected to login on Speedy Net, and gets a 404 on Speedy Match.
                """
                self.client.logout()
                r = self.client.get(path=self.page_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)
                else:
                    self.assertEqual(first=r.status_code, second=404)

            def test_other_user_has_no_access(self):
                """
                Asserts a logged-in user other than the list's owner gets a 403 on Speedy Net, and a 404 on Speedy Match.
                """
                self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.status_code, second=403)
                else:
                    self.assertEqual(first=r.status_code, second=404)

            def test_user_has_access(self):
                """
                Asserts the list owner can access the blocked-users list page on Speedy Net (with the expected template), and gets a 404 on Speedy Match.
                """
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
                    self.assertEqual(first=r.status_code, second=200)
                    self.assertTemplateUsed(response=r, template_name='blocks/block_list.html')
                else:
                    self.assertEqual(first=r.status_code, second=404)


        @only_on_sites_with_login
        class BlockViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the view that lets a logged-in user block another user.

            Methods:
                test_visitor_has_no_access(self): Asserts an anonymous visitor is redirected to login when trying to block a user.
                test_user_cannot_block_self(self): Asserts a user attempting to block himself gets a 403 response.
                test_user_can_block_other_user(self): Asserts a user can block another user, which creates a Block instance and redirects to the blocked user's profile page.
            """
            def set_up(self):
                """
                Creates two active users and builds the block page URL for blocking the second user.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.page_url = '/{}/block/'.format(self.second_user.slug)

            def test_visitor_has_no_access(self):
                """
                Asserts an anonymous visitor is redirected to the login page when trying to block a user.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_cannot_block_self(self):
                """
                Asserts a user attempting to block himself gets a 403 response.
                """
                self.client.login(username=self.second_user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)

            def test_user_can_block_other_user(self):
                """
                Asserts a user can block another user, which creates a Block instance with the expected blocker/blocked and redirects to the blocked user's profile page.
                """
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Block.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=Block.objects.count(), second=1)
                block = Block.objects.first()
                self.assertEqual(first=block.blocker_id, second=self.first_user.id)
                self.assertEqual(first=block.blocked_id, second=self.second_user.id)
                self.assertRedirects(response=r, expected_url='/{}/'.format(self.second_user.slug), status_code=302, target_status_code=404)


        @only_on_sites_with_login
        class UnblockViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the view that lets a logged-in user unblock a previously blocked user.

            Methods:
                test_visitor_has_no_access(self): Asserts an anonymous visitor is redirected to login when trying to unblock a user.
                test_user_can_unblock_other_user(self): Asserts a user can unblock another user, which removes the Block instance and redirects to the unblocked user's profile page.
            """
            def set_up(self):
                """
                Creates two active users and builds the unblock page URL for unblocking the second user.
                """
                super().set_up()
                self.first_user = ActiveUserFactory()
                self.second_user = ActiveUserFactory()
                self.page_url = '/{}/unblock/'.format(self.second_user.slug)

            def test_visitor_has_no_access(self):
                """
                Asserts an anonymous visitor is redirected to the login page when trying to unblock a user.
                """
                self.client.logout()
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url='/login/?next={}'.format(self.page_url), status_code=302, target_status_code=200)

            def test_user_can_unblock_other_user(self):
                """
                Asserts a user can unblock another user, which removes the Block instance and redirects to the unblocked user's profile page.
                """
                self.client.login(username=self.first_user.slug, password=tests_settings.USER_PASSWORD)
                Block.objects.block(blocker=self.first_user, blocked=self.second_user)
                self.assertEqual(first=Block.objects.count(), second=1)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=Block.objects.count(), second=0)
                self.assertRedirects(response=r, expected_url='/{}/'.format(self.second_user.slug), status_code=302, target_status_code=200)


