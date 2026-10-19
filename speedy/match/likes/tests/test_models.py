"""
Test cases for the UserLike model of Speedy Match - blocks, genders and like notification emails in all main languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random

        from django.test import override_settings
        from django.core import mail

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match
        from speedy.core.accounts.test.mixins import SpeedyCoreAccountsModelsMixin
        from speedy.match.likes.test.mixins import SpeedyMatchLikesLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.accounts.models import User
        from speedy.core.blocks.models import Block
        from speedy.match.likes.models import UserLike


        @only_on_speedy_match
        class LikeBlocksOnlyEnglishTestCase(SiteTestCase):
            """
            Tests that blocking affects like counters only in the direction of the block (blocker's likes-from counter is reduced, but the blocked user's likes-to counter is unaffected), run only once (in English) since it is language-independent.
            """

            def set_up(self):
                """
                Creates two users (user_1, user_2) along with several likes to and from other users, to use as a baseline for testing block-related like counter changes.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()
                UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory())
                UserLike.objects.add_like(from_user=self.user_1, to_user=ActiveUserFactory())
                UserLike.objects.add_like(from_user=self.user_2, to_user=ActiveUserFactory())
                UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user_1)
                UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user_2)
                UserLike.objects.add_like(from_user=ActiveUserFactory(), to_user=self.user_2)

            def assert_counters(self, user, likes_from_user, likes_to_user):
                """
                Asserts the given user's likes-from and likes-to counters (both via direct queries and related managers) match the expected values.

                :param user: The user whose like counters are checked.
                :type user: speedy.core.accounts.models.User
                :param likes_from_user: The expected number of likes made by the user.
                :type likes_from_user: int
                :param likes_to_user: The expected number of likes received by the user.
                :type likes_to_user: int
                """
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=len(UserLike.objects.filter(from_user=user)), second=likes_from_user)
                self.assertEqual(first=UserLike.objects.filter(from_user=user).count(), second=likes_from_user)
                self.assertEqual(first=user.likes_from_user.count(), second=likes_from_user)
                self.assertEqual(first=len(UserLike.objects.filter(to_user=user)), second=likes_to_user)
                self.assertEqual(first=UserLike.objects.filter(to_user=user).count(), second=likes_to_user)
                self.assertEqual(first=user.likes_to_user.count(), second=likes_to_user)
                self.assertEqual(first=user.speedy_match_profile.likes_to_user_count, second=likes_to_user)

            def test_set_up(self):
                """
                Asserts the initial like counters created by set_up are correct for user_1 and user_2.
                """
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)

            def test_if_no_relation_between_users_nothing_get_affected(self):
                """
                Asserts that blocking and then unblocking two users who have no existing like relation leaves their like counters unchanged.
                """
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)

            def test_if_user1_blocked_user2_like_is_removed(self):
                """
                Asserts that when user_1 blocks user_2, the like from user_1 to user_2 is removed, and it stays removed after unblocking.
                """
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=3, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=3)
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)

            def test_if_user2_blocked_user1_like_isnt_removed(self):
                """
                Asserts that when user_2 blocks user_1, the like from user_1 to user_2 is unaffected, and remains unaffected after unblocking.
                """
                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=3, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=3)
                Block.objects.block(blocker=self.user_2, blocked=self.user_1)
                self.assert_counters(user=self.user_1, likes_from_user=3, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=3)
                Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
                self.assert_counters(user=self.user_1, likes_from_user=3, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=3)


        @only_on_speedy_match
        class LikeGenderOnlyEnglishTestCase(SiteTestCase):
            """
            Tests the SiteProfile.get_like_gender method, which reports the predominant gender of a user's liked/liking users, run only once (in English) since it is language-independent.
            """

            def set_up(self):
                """
                Creates three active users, one of each gender (user_1 female, user_2 male, user_3 other).
                """
                super().set_up()
                self.user_1 = ActiveUserFactory(gender=User.GENDER_FEMALE)
                self.user_2 = ActiveUserFactory(gender=User.GENDER_MALE)
                self.user_3 = ActiveUserFactory(gender=User.GENDER_OTHER)

            def _create_users(self, users_count, gender):
                """
                Creates the given number of active users of the given gender, storing each as a sequentially-numbered instance attribute starting from user_4.

                :param users_count: The number of users to create.
                :type users_count: int
                :param gender: The gender to assign to each created user.
                :type gender: int
                """
                for i in range(users_count):
                    setattr(self, "user_{}".format(4 + i), ActiveUserFactory(gender=gender))

            def test_get_like_gender_if_there_are_no_liked_and_liking_users(self):
                """
                Asserts get_like_gender returns 'other' when a user has no likes, and returns the matched gender's name once gender_to_match is set to a single gender.
                """
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="other")
                for gender in User.GENDER_VALID_VALUES:
                    for user in [self.user_1, self.user_2, self.user_3]:
                        user.speedy_match_profile.gender_to_match = [gender]
                        user.save_user_and_profile()
                        self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second=User.GENDERS_DICT[gender])

            def test_get_like_gender_for_15_liked_and_liking_users(self):
                """
                Asserts get_like_gender correctly reports the predominant gender across various combinations of up to 15 liked/liking users of mixed genders, as likes and user genders change.
                """
                self._create_users(users_count=15, gender=User.GENDER_FEMALE)
                for user in [self.user_1, self.user_2, self.user_3]:
                    user.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE]
                    user.save_user_and_profile()
                    for i in range(8):
                        UserLike.objects.add_like(from_user=user, to_user=getattr(self, "user_{}".format(4 + i)))
                    for i in range(7):
                        UserLike.objects.add_like(from_user=getattr(self, "user_{}".format(4 + 8 + i)), to_user=user)
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_8.gender = random.choice([User.GENDER_MALE, User.GENDER_OTHER])
                self.user_8.save_user_and_profile()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_16.gender = random.choice([User.GENDER_MALE, User.GENDER_OTHER])
                self.user_16.save_user_and_profile()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="other")

                self.user_8.delete()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_16.delete()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                UserLike.objects.add_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="female")

                UserLike.objects.add_like(from_user=self.user_3, to_user=self.user_1)
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="other")

                UserLike.objects.remove_like(from_user=self.user_3, to_user=self.user_1)
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="female")

                UserLike.objects.remove_like(from_user=self.user_1, to_user=self.user_2)
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="female")

                UserLike.objects.add_like(from_user=self.user_3, to_user=self.user_1)
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="female")

                UserLike.objects.remove_like(from_user=self.user_3, to_user=self.user_1)
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="female")

                self.user_1.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="other")

                self.user_1.speedy_match_profile.gender_to_match = [User.GENDER_MALE, User.GENDER_FEMALE]
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="other")

                self.user_1.speedy_match_profile.gender_to_match = [User.GENDER_MALE, User.GENDER_OTHER]
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="other")

                self.user_1.speedy_match_profile.gender_to_match = User.GENDER_VALID_VALUES
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="other")

                self.user_1.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE]
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="female")

            def test_get_like_gender_for_35_liked_and_liking_users(self):
                """
                Asserts get_like_gender correctly reports the predominant gender across various combinations of up to 35 liked/liking users of mixed genders, as likes and user genders change.
                """
                self._create_users(users_count=30, gender=User.GENDER_FEMALE)
                for user in [self.user_1, self.user_2, self.user_3]:
                    user.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE]
                    user.save_user_and_profile()
                    # Users 17 to 21 are both liked and liking users (mutual likes).
                    for i in range(18):
                        UserLike.objects.add_like(from_user=user, to_user=getattr(self, "user_{}".format(4 + i)))
                    for i in range(17):
                        UserLike.objects.add_like(from_user=getattr(self, "user_{}".format(4 + 13 + i)), to_user=user)
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_8.gender = random.choice([User.GENDER_MALE, User.GENDER_OTHER])
                self.user_8.save_user_and_profile()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_12.gender = random.choice([User.GENDER_MALE, User.GENDER_OTHER])
                self.user_12.save_user_and_profile()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_24.gender = random.choice([User.GENDER_MALE, User.GENDER_OTHER])
                self.user_24.save_user_and_profile()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_18.gender = random.choice([User.GENDER_MALE, User.GENDER_OTHER])
                self.user_18.save_user_and_profile()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="other")

                self.user_20.gender = random.choice([User.GENDER_MALE, User.GENDER_OTHER])
                self.user_20.save_user_and_profile()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="other")

                self.user_8.delete()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="other")

                self.user_18.delete()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="other")

                self.user_12.delete()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_20.delete()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_24.delete()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="female")

                self.user_1.speedy_match_profile.gender_to_match = [User.GENDER_MALE]
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="other")

                self.user_1.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="other")

                self.user_1.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE]
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.get_like_gender(), second="female")


        class LikeNotificationsTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyMatchLikesLanguageMixin, TestCaseMixin):
            """
            Tests whether a user gets notified by email when liked, depending on his notify_on_like setting.
            """

            def set_up(self):
                """
                Creates two users (user_1, user_2) with default notification settings.
                """
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()

            def test_user_gets_notified_on_like(self):
                """
                Asserts that when user_2 likes user_1 (who has notify_on_like enabled), an email is sent to user_1 with the expected subject for his gender.
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
                UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second=self._someone_likes_you_on_speedy_match_subject_dict_by_gender[self.user_2.get_gender()])

            def test_user_doesnt_get_notified_on_like(self):
                """
                Asserts that when user_2 likes user_1 (who has disabled notify_on_like), no email is sent.
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
                self.user_1.speedy_match_profile.notify_on_like = User.NOTIFICATIONS_OFF
                self.user_1.save_user_and_profile()
                self.assertEqual(first=self.user_1.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_OFF)
                self.assertEqual(first=self.user_2.speedy_match_profile.notify_on_like, second=User.NOTIFICATIONS_ON)
                UserLike.objects.add_like(from_user=self.user_2, to_user=self.user_1)
                self.assertEqual(first=len(mail.outbox), second=0)


        @only_on_speedy_match
        class LikeNotificationsAllMainLanguagesEnglishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class LikeNotificationsAllMainLanguagesFrenchTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class LikeNotificationsAllMainLanguagesGermanTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class LikeNotificationsAllMainLanguagesSpanishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class LikeNotificationsAllMainLanguagesPortugueseTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class LikeNotificationsAllMainLanguagesItalianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class LikeNotificationsAllMainLanguagesDutchTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ja')
        class LikeNotificationsAllMainLanguagesJapaneseTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ru')
        class LikeNotificationsAllMainLanguagesRussianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='zh')
        class LikeNotificationsAllMainLanguagesChineseTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pl')
        class LikeNotificationsAllMainLanguagesPolishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fa')
        class LikeNotificationsAllMainLanguagesPersianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class LikeNotificationsAllMainLanguagesHebrewTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ko')
        class LikeNotificationsAllMainLanguagesKoreanTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ar')
        class LikeNotificationsAllMainLanguagesArabicTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='id')
        class LikeNotificationsAllMainLanguagesIndonesianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='uk')
        class LikeNotificationsAllMainLanguagesUkrainianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='tr')
        class LikeNotificationsAllMainLanguagesTurkishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='vi')
        class LikeNotificationsAllMainLanguagesVietnameseTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='cs')
        class LikeNotificationsAllMainLanguagesCzechTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sv')
        class LikeNotificationsAllMainLanguagesSwedishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fi')
        class LikeNotificationsAllMainLanguagesFinnishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hu')
        class LikeNotificationsAllMainLanguagesHungarianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='th')
        class LikeNotificationsAllMainLanguagesThaiTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='el')
        class LikeNotificationsAllMainLanguagesGreekTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ms')
        class LikeNotificationsAllMainLanguagesMalayTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sr')
        class LikeNotificationsAllMainLanguagesSerbianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ro')
        class LikeNotificationsAllMainLanguagesRomanianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='bn')
        class LikeNotificationsAllMainLanguagesBengaliTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ca')
        class LikeNotificationsAllMainLanguagesCatalanTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='no')
        class LikeNotificationsAllMainLanguagesNorwegianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='bg')
        class LikeNotificationsAllMainLanguagesBulgarianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='da')
        class LikeNotificationsAllMainLanguagesDanishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sk')
        class LikeNotificationsAllMainLanguagesSlovakTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hi')
        class LikeNotificationsAllMainLanguagesHindiTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='et')
        class LikeNotificationsAllMainLanguagesEstonianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hr')
        class LikeNotificationsAllMainLanguagesCroatianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='az')
        class LikeNotificationsAllMainLanguagesAzerbaijaniTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='zh-yue')
        class LikeNotificationsAllMainLanguagesCantoneseTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='lt')
        class LikeNotificationsAllMainLanguagesLithuanianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sl')
        class LikeNotificationsAllMainLanguagesSlovenianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='eu')
        class LikeNotificationsAllMainLanguagesBasqueTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='hy')
        class LikeNotificationsAllMainLanguagesArmenianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='uz')
        class LikeNotificationsAllMainLanguagesUzbekTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ta')
        class LikeNotificationsAllMainLanguagesTamilTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='lv')
        class LikeNotificationsAllMainLanguagesLatvianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests like email notifications for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


