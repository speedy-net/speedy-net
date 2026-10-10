"""
Test cases for the like, unlike and like list views of Speedy Match, in all main languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random
        from time import sleep

        from django.test import override_settings
        from django.core import mail

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin
        from speedy.match.likes.test.mixins import SpeedyMatchLikesLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.blocks.models import Block
        from speedy.core.accounts.models import User
        from speedy.match.likes.models import UserLike


        class LikeViewTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyMatchLikesLanguageMixin, TestCaseMixin):
            """
            Tests the like view, including permission checks and the notification email sent to the liked user.

            Methods:
                set_up(self): Creates two users (user_1, user_2) and the like page URL for user_2.
                test_user_can_like_and_other_user_gets_notified_on_like(self): Asserts a user can like another user and an email notification is sent.
                test_user_can_like_and_other_user_doesnt_get_notified_on_like(self): Asserts a user can like another user who has disabled like notifications, and no email is sent.
                test_user_cannot_like_self(self): Asserts a user cannot like himself.
                test_user_cannot_like_other_user_if_blocked(self): Asserts a user cannot like another user he has blocked.
                test_user_cannot_like_other_user_if_blocking(self): Asserts a user cannot like another user who has blocked him.
                test_user_cannot_like_twice(self): Asserts a user cannot like another user he already likes.
            """
            def set_up(self):
                """
                Creates two users (user_1, user_2) and builds the like page URL for liking user_2.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.page_url = '/{}/likes/like/'.format(self.user_2.slug)

            def test_user_can_like_and_other_user_gets_notified_on_like(self):
                """
                Asserts user_1 can like user_2 (who has like notifications enabled) and that an email is sent to user_2 with the expected subject for user_1's gender.
                """
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2,
                    confirmed_email_address_count=2,
                    unconfirmed_email_address_count=0,
                )
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_1,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.user_2 = User.objects.get(pk=self.user_2.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_2,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assertEqual(first=len(mail.outbox), second=0)
                self.assertEqual(first=self.user_1.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
                self.assertEqual(first=self.user_2.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.user_2.get_absolute_url(), status_code=302, target_status_code=200)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                like = UserLike.objects.first()
                self.assertEqual(first=like.from_user.id, second=self.user_1.id)
                self.assertEqual(first=like.to_user.id, second=self.user_2.id)
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second=self._someone_likes_you_on_speedy_match_subject_dict_by_gender[self.user_1.get_gender()])

            def test_user_can_like_and_other_user_doesnt_get_notified_on_like(self):
                """
                Asserts user_1 can like user_2, and when user_2 has disabled like notifications, no email is sent.
                """
                self.assert_models_count(
                    entity_count=2,
                    user_count=2,
                    user_email_address_count=2,
                    confirmed_email_address_count=2,
                    unconfirmed_email_address_count=0,
                )
                self.user_1 = User.objects.get(pk=self.user_1.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_1,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.user_2 = User.objects.get(pk=self.user_2.pk)
                self.assert_user_email_addresses_count(
                    user=self.user_2,
                    user_email_addresses_count=1,
                    user_primary_email_addresses_count=1,
                    user_confirmed_email_addresses_count=1,
                    user_unconfirmed_email_addresses_count=0,
                )
                self.assertEqual(first=len(mail.outbox), second=0)
                self.user_2.speedy_match_profile.notify_on_like = User.NOTIFICATIONS_OFF
                self.user_2.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
                self.assertEqual(first=self.user_2.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_OFF)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.user_2.get_absolute_url(), status_code=302, target_status_code=200)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                like = UserLike.objects.first()
                self.assertEqual(first=like.from_user.id, second=self.user_1.id)
                self.assertEqual(first=like.to_user.id, second=self.user_2.id)
                self.assertEqual(first=len(mail.outbox), second=0)

            def test_user_cannot_like_self(self):
                """
                Asserts a user cannot like himself; the view returns 403 and no like is created.
                """
                self.client.login(username=self.user_2.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_cannot_like_other_user_if_blocked(self):
                """
                Asserts a user cannot like another user he has blocked; the view returns 403 and no like is created.
                """
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_cannot_like_other_user_if_blocking(self):
                """
                Asserts a user cannot like another user who has blocked him; the view returns 403 and no like is created.
                """
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_cannot_like_twice(self):
                """
                Asserts a user cannot like another user he already likes; the second attempt returns 403 and no additional like is created.
                """
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.user_2.get_absolute_url(), status_code=302, target_status_code=200)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                like = UserLike.objects.first()
                self.assertEqual(first=like.from_user.id, second=self.user_1.id)
                self.assertEqual(first=like.to_user.id, second=self.user_2.id)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=UserLike.objects.count(), second=1)


        @only_on_speedy_match
        class LikeViewAllMainLanguagesEnglishTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class LikeViewAllMainLanguagesFrenchTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class LikeViewAllMainLanguagesGermanTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class LikeViewAllMainLanguagesSpanishTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class LikeViewAllMainLanguagesPortugueseTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class LikeViewAllMainLanguagesItalianTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class LikeViewAllMainLanguagesDutchTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class LikeViewAllMainLanguagesHebrewTestCase(LikeViewTestCaseMixin, SiteTestCase):
            """
            Tests the like view for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_speedy_match
        class UnlikeViewOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the unlike view, run only once (in English) since it is language-independent.

            Methods:
                set_up(self): Creates two users (user_1, user_2) and the unlike page URL for user_2.
                test_user_can_unlike(self): Asserts a user can unlike a user he likes.
                test_user_cannot_unlike_if_doesnt_like(self): Asserts a user cannot unlike a user he doesn't like.
                test_user_cannot_unlike_twice(self): Asserts a user cannot unlike a user twice in a row.
            """
            def set_up(self):
                """
                Creates two users (user_1, user_2) and builds the unlike page URL for unliking user_2.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.page_url = '/{}/likes/unlike/'.format(self.user_2.slug)

            def test_user_can_unlike(self):
                """
                Asserts a user who likes another user can successfully unlike him, removing the UserLike record.
                """
                self.client.login(username=self.user_1.slug,  password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.user_2.get_absolute_url(), status_code=302, target_status_code=200)
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_cannot_unlike_if_doesnt_like(self):
                """
                Asserts a user cannot unlike a user he doesn't currently like; the view returns 403.
                """
                self.client.login(username=self.user_1.slug,  password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=UserLike.objects.count(), second=0)

            def test_user_cannot_unlike_twice(self):
                """
                Asserts a user can unlike a user he likes once, but a second unlike attempt returns 403.
                """
                self.client.login(username=self.user_1.slug,  password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=UserLike.objects.count(), second=1)
                r = self.client.post(path=self.page_url)
                self.assertRedirects(response=r, expected_url=self.user_2.get_absolute_url(), status_code=302, target_status_code=200)
                self.assertEqual(first=UserLike.objects.count(), second=0)
                r = self.client.post(path=self.page_url)
                self.assertEqual(first=r.status_code, second=403)
                self.assertEqual(first=UserLike.objects.count(), second=0)


        class LikeListViewsTestCaseMixin(SpeedyMatchLikesLanguageMixin, TestCaseMixin):
            """
            Tests the like-list views (people I like, people who like me, mutual likes), including ordering, blocking, gender-based titles, and deletion protections.

            Methods:
                set_up(self): Creates 5 users with a mix of likes between them and builds the like-list page URLs.
                _test_all_like_list_views_contain_strings(self, strings): Asserts each like-list view returns 200, has the expected object count, and contains all the given strings.
                test_visitor_has_no_access(self): Asserts a logged-out visitor is redirected away from all like-list pages.
                test_default_redirect(self): Asserts the default likes URL redirects to the "people I like" page.
                test_user_can_see_who_they_like(self): Asserts the "people I like" view lists the correct users, in the correct (last-visit) order, excluding blocked users.
                test_user_can_see_who_likes_them(self): Asserts the "people who like me" view lists the correct users, in the correct (last-visit) order, excluding blocked users.
                test_user_can_see_mutual_likes(self): Asserts the "mutual likes" view lists only users with a mutual like, in the correct (last-visit) order, excluding blocked users.
                test_like_list_views_titles(self): Asserts the like-list view titles reflect the correct gender-specific wording based on the current user's gender_to_match and the liked/liking users' genders.
                test_like_list_views_titles_with_empty_lists(self): Asserts the like-list view titles reflect the correct gender-specific wording even when the like lists are empty.
                test_cannot_delete_users_with_queryset_delete(self): Asserts deleting users or the current user via a queryset raises NotImplementedError.
                test_cannot_delete_likes_with_queryset_delete(self): Asserts deleting likes via a queryset raises NotImplementedError.
            """
            def set_up(self):
                """
                Creates 5 users (user_1 through user_5) plus several other users, with a mix of likes to and from user_1 (including mutual likes), builds the like-list page URLs, logs in as user_1, and staggers each user's last-visit time to establish a known ordering.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                self.user_3 = ActiveUserFactory()
                self.user_4 = ActiveUserFactory()
                self.user_5 = ActiveUserFactory()
                self.default_url = '/{}/likes/'.format(self.user_1.slug)
                self.to_url = '/{}/likes/people-i-like/'.format(self.user_1.slug)
                self.from_url = '/{}/likes/people-who-like-me/'.format(self.user_1.slug)
                self.mutual_url = '/{}/likes/mutual/'.format(self.user_1.slug)
                UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory(slug="user-99"))
                UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory(slug="user-98"))
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_3)
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_5)
                UserLike.objects.add_like(from_user=ActiveUserFactory(slug="user-97"), to_user=self.user_1)
                UserLike.objects.add_like(from_user=ActiveUserFactory(slug="user-96"), to_user=self.user_1)
                UserLike.objects.add_like(from_user=self.user_5, to_user=self.user_1)
                UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
                self.to_likes = {
                    User.objects.get(slug="user-99"),
                    User.objects.get(slug="user-98"),
                    self.user_3,
                    self.user_2,
                    self.user_5,
                }
                self.from_likes = {
                    User.objects.get(slug="user-97"),
                    User.objects.get(slug="user-96"),
                    self.user_2,
                    self.user_5,
                }
                self.mutual_likes = {
                    self.user_2,
                    self.user_5,
                }
                self.client.login(username=self.user_1.slug, password=tests_settings.USER_PASSWORD)
                sleep(0.02)
                self.user_5.profile.update_last_visit()
                sleep(0.01)
                self.user_4.profile.update_last_visit()
                sleep(0.01)
                self.user_2.profile.update_last_visit()
                sleep(0.01)
                self.user_3.profile.update_last_visit()
                self.assertEqual(first=UserLike.objects.count(), second=9)

            def _test_all_like_list_views_contain_strings(self, strings):
                """
                Asserts each of the three like-list views (to, from, mutual) returns 200, has the expected object count for the current state, and contains every given string in its rendered content.

                :param strings: The strings expected to appear in each view's rendered content (typically the page titles).
                :type strings: list
                """
                r = self.client.get(path=self.to_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=len(self.to_likes))
                for string in strings:
                    self.assertIn(member=string, container=r.content.decode())
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=len(self.from_likes))
                for string in strings:
                    self.assertIn(member=string, container=r.content.decode())
                r = self.client.get(path=self.mutual_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=len(self.mutual_likes))
                for string in strings:
                    self.assertIn(member=string, container=r.content.decode())

            def test_visitor_has_no_access(self):
                """
                Asserts a logged-out visitor is redirected away (302) from all three like-list pages.
                """
                self.client.logout()
                self.assertEqual(first=self.client.get(path=self.to_url).status_code, second=302)
                self.assertEqual(first=self.client.get(path=self.from_url).status_code, second=302)
                self.assertEqual(first=self.client.get(path=self.mutual_url).status_code, second=302)

            def test_default_redirect(self):
                """
                Asserts the default likes URL redirects to the "people I like" page.
                """
                r = self.client.get(path=self.default_url)
                self.assertRedirects(response=r, expected_url=self.to_url, status_code=302, target_status_code=200)

            def test_user_can_see_who_they_like(self):
                """
                Asserts the "people I like" view lists exactly the users user_1 likes, ordered by last visit, updates as new likes are added, and excludes a user who blocks or is blocked by user_1.
                """
                r = self.client.get(path=self.to_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=5)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.to_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2={self.user_1})
                to_likes = set(self.to_likes)
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_4)
                to_likes.add(self.user_4)
                self.assertEqual(first=UserLike.objects.count(), second=10)
                r = self.client.get(path=self.to_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=6)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.to_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=to_likes)
                self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_3)
                sleep(0.01)
                self.user_4.profile.update_last_visit()
                r = self.client.get(path=self.to_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=6)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.to_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=to_likes)
                self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_4)
                Block.objects.block(blocker=self.user_4, blocked=self.user_1)
                r = self.client.get(path=self.to_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=6)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.to_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=to_likes)
                Block.objects.block(blocker=self.user_1, blocked=self.user_4)
                r = self.client.get(path=self.to_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=5)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=to_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.to_likes)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_4)
                r = self.client.get(path=self.to_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=5)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=to_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.to_likes)

            def test_user_can_see_who_likes_them(self):
                """
                Asserts the "people who like me" view lists exactly the users who like user_1, ordered by last visit, updates as new likes are added, and excludes a user who blocks or is blocked by user_1.
                """
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=4)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=self.from_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2={self.user_1})
                from_likes = set(self.from_likes)
                UserLike.objects.add_like(from_user=self.user_4, to_user=self.user_1)
                from_likes.add(self.user_4)
                self.assertEqual(first=UserLike.objects.count(), second=10)
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=5)
                self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=self.from_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=from_likes)
                self.assertEqual(first=r.context['object_list'][0].from_user, second=self.user_2)
                sleep(0.01)
                self.user_4.profile.update_last_visit()
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=5)
                self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=self.from_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=from_likes)
                self.assertEqual(first=r.context['object_list'][0].from_user, second=self.user_4)
                Block.objects.block(blocker=self.user_1, blocked=self.user_4)
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=4)
                self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=from_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=self.from_likes)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_4)
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=5)
                self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=self.from_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=from_likes)
                Block.objects.block(blocker=self.user_4, blocked=self.user_1)
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=4)
                self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=from_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=self.from_likes)
                Block.objects.unblock(blocker=self.user_4, blocked=self.user_1)
                r = self.client.get(path=self.from_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=4)
                self.assertNotEqual(first={like.from_user for like in r.context['object_list']}, second=from_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2=self.from_likes)

            def test_user_can_see_mutual_likes(self):
                """
                Asserts the "mutual likes" view lists exactly the users who have a mutual like with user_1, ordered by last visit, updates as new mutual likes are added, and excludes a user who blocks or is blocked by user_1.
                """
                r = self.client.get(path=self.mutual_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=2)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.mutual_likes)
                self.assertSetEqual(set1={like.from_user for like in r.context['object_list']}, set2={self.user_1})
                mutual_likes = set(self.mutual_likes)
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_4)
                UserLike.objects.add_like(from_user=self.user_4, to_user=self.user_1)
                mutual_likes.add(self.user_4)
                self.assertEqual(first=UserLike.objects.count(), second=11)
                r = self.client.get(path=self.mutual_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=3)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.mutual_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=mutual_likes)
                self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_2)
                sleep(0.01)
                self.user_4.profile.update_last_visit()
                r = self.client.get(path=self.mutual_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=3)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=self.mutual_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=mutual_likes)
                self.assertEqual(first=r.context['object_list'][0].to_user, second=self.user_4)
                Block.objects.block(blocker=self.user_4, blocked=self.user_1)
                r = self.client.get(path=self.mutual_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=2)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=mutual_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.mutual_likes)
                Block.objects.unblock(blocker=self.user_4, blocked=self.user_1)
                r = self.client.get(path=self.mutual_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertEqual(first=len(r.context['object_list']), second=2)
                self.assertNotEqual(first={like.to_user for like in r.context['object_list']}, second=mutual_likes)
                self.assertSetEqual(set1={like.to_user for like in r.context['object_list']}, set2=self.mutual_likes)

            def test_like_list_views_titles(self):
                """
                Asserts the like-list view titles use the correct gender-specific wording, varying the current user's gender_to_match and the liked/liking users' genders across all combinations.
                """
                self._test_all_like_list_views_contain_strings(strings=[
                    self._list_to_title_dict_by_gender[User.GENDER_OTHER_STRING],
                    self._list_from_title_dict_by_gender[User.GENDER_OTHER_STRING],
                    self._list_mutual_title,
                ])
                user_99 = User.objects.get(slug="user-99")
                user_97 = User.objects.get(slug="user-97")
                gender_count_dict = {
                    User.GENDER_FEMALE_STRING: 0,
                    User.GENDER_MALE_STRING: 0,
                    User.GENDER_OTHER_STRING: 0,
                }
                for gender in User.GENDER_VALID_VALUES:
                    for user in [self.user_3, self.user_2, self.user_5, User.objects.get(slug="user-98"), User.objects.get(slug="user-96")]:
                        user.gender = gender
                        user.save_user_and_profile()
                    if (gender == User.GENDER_OTHER):
                        two_genders = [random.choice([User.GENDER_FEMALE, User.GENDER_MALE]), gender]
                    else:
                        two_genders = [User.GENDER_FEMALE, User.GENDER_MALE]
                    for gender_to_match in [User.GENDER_VALID_VALUES, [gender], two_genders]:
                        self.user_1.speedy_match_profile.gender_to_match = gender_to_match
                        self.user_1.save_user_and_profile()
                        for gender_99 in User.GENDER_VALID_VALUES:
                            for gender_97 in User.GENDER_VALID_VALUES:
                                user_99.gender = gender_99
                                user_97.gender = gender_97
                                user_99.save_user_and_profile()
                                user_97.save_user_and_profile()
                                if ((gender in [User.GENDER_FEMALE, User.GENDER_MALE]) and (gender_to_match == [gender]) and (len({user_99.gender, user_97.gender, self.user_2.gender}) == 1)):
                                    gender_string = self.user_2.get_gender()
                                    self.assertIn(member=gender_string, container=[User.GENDER_FEMALE_STRING, User.GENDER_MALE_STRING])
                                    self.assertEqual(first=gender_string, second=User.GENDERS_DICT.get(gender))
                                else:
                                    gender_string = User.GENDER_OTHER_STRING
                                    self.assertEqual(first=gender_string, second=User.GENDERS_DICT.get(User.GENDER_OTHER))
                                self._test_all_like_list_views_contain_strings(strings=[
                                    self._list_to_title_dict_by_gender[gender_string],
                                    self._list_from_title_dict_by_gender[gender_string],
                                    self._list_mutual_title,
                                ])
                                gender_count_dict[gender_string] += 1
                expected_gender_count_dict = {
                    User.GENDER_FEMALE_STRING: 1,
                    User.GENDER_MALE_STRING: 1,
                    User.GENDER_OTHER_STRING: 79,
                }
                self.assertDictEqual(d1=gender_count_dict, d2=expected_gender_count_dict)

            def test_like_list_views_titles_with_empty_lists(self):
                """
                Asserts the like-list view titles use the correct gender-specific wording even when all other users are deleted and the like lists are empty, across all gender_to_match combinations.
                """
                for user in User.objects.all().exclude(pk=self.user_1.pk):
                    user.delete()
                self.user_2 = None
                self.user_3 = None
                self.user_4 = None
                self.user_5 = None
                self.to_likes = set()
                self.from_likes = set()
                self.mutual_likes = set()
                self.assertEqual(first=UserLike.objects.count(), second=0)
                self._test_all_like_list_views_contain_strings(strings=[
                    self._list_to_title_dict_by_gender[User.GENDER_OTHER_STRING],
                    self._list_from_title_dict_by_gender[User.GENDER_OTHER_STRING],
                    self._list_mutual_title,
                ])
                gender_count_dict = {
                    User.GENDER_FEMALE_STRING: 0,
                    User.GENDER_MALE_STRING: 0,
                    User.GENDER_OTHER_STRING: 0,
                }
                for gender in User.GENDER_VALID_VALUES:
                    if (gender == User.GENDER_OTHER):
                        two_genders = [random.choice([User.GENDER_FEMALE, User.GENDER_MALE]), gender]
                    else:
                        two_genders = [User.GENDER_FEMALE, User.GENDER_MALE]
                    for gender_to_match in [User.GENDER_VALID_VALUES, [gender], two_genders]:
                        self.user_1.speedy_match_profile.gender_to_match = gender_to_match
                        self.user_1.save_user_and_profile()
                        if ((gender in [User.GENDER_FEMALE, User.GENDER_MALE]) and (gender_to_match == [gender])):
                            gender_string = User.GENDERS_DICT.get(gender)
                            self.assertIn(member=gender_string, container=[User.GENDER_FEMALE_STRING, User.GENDER_MALE_STRING])
                        else:
                            gender_string = User.GENDER_OTHER_STRING
                            self.assertEqual(first=gender_string, second=User.GENDERS_DICT.get(User.GENDER_OTHER))
                        self._test_all_like_list_views_contain_strings(strings=[
                            self._list_to_title_dict_by_gender[gender_string],
                            self._list_from_title_dict_by_gender[gender_string],
                            self._list_mutual_title,
                        ])
                        gender_count_dict[gender_string] += 1
                expected_gender_count_dict = {
                    User.GENDER_FEMALE_STRING: 1,
                    User.GENDER_MALE_STRING: 1,
                    User.GENDER_OTHER_STRING: 7,
                }
                self.assertDictEqual(d1=gender_count_dict, d2=expected_gender_count_dict)

            def test_cannot_delete_users_with_queryset_delete(self):
                """
                Asserts that calling delete() on a User queryset (filtered or not) always raises NotImplementedError.
                """
                with self.assertRaises(NotImplementedError) as cm:
                    User.objects.all().exclude(pk=self.user_1.pk).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    User.objects.delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    User.objects.all().delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    User.objects.all().filter(pk=1).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")

            def test_cannot_delete_likes_with_queryset_delete(self):
                """
                Asserts that calling delete() on a UserLike queryset (filtered or not) always raises NotImplementedError.
                """
                with self.assertRaises(NotImplementedError) as cm:
                    UserLike.objects.delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    UserLike.objects.all().delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    UserLike.objects.filter(from_user=self.user_1, to_user=self.user_3).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    UserLike.objects.all().exclude(pk=2).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")


        @only_on_speedy_match
        class LikeListViewsAllMainLanguagesEnglishTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class LikeListViewsAllMainLanguagesFrenchTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class LikeListViewsAllMainLanguagesGermanTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class LikeListViewsAllMainLanguagesSpanishTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class LikeListViewsAllMainLanguagesPortugueseTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class LikeListViewsAllMainLanguagesItalianTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class LikeListViewsAllMainLanguagesDutchTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class LikeListViewsAllMainLanguagesHebrewTestCase(LikeListViewsTestCaseMixin, SiteTestCase):
            """
            Tests the like-list views (likes-to, likes-by, mutual-likes) for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


