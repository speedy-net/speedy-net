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

            Methods:
                set_up(self): Creates two users (user_1, user_2) and several likes to/from other users.
                assert_counters(self, user, likes_from_user, likes_to_user): Asserts a user's likes-from and likes-to counters match the given expected values.
                test_set_up(self): Asserts the initial like counters set up in set_up are correct.
                test_if_no_relation_between_users_nothing_get_affected(self): Asserts blocking/unblocking two users who have no like relation doesn't change their like counters.
                test_if_user1_blocked_user2_like_is_removed(self): Asserts that when user_1 blocks user_2, their mutual like is removed, and stays removed after unblocking.
                test_if_user2_blocked_user1_like_isnt_removed(self): Asserts that when user_2 blocks user_1, the like from user_1 to user_2 is unaffected.
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

            Methods:
                set_up(self): Creates three users, one of each gender.
                _create_users(self, users_count, gender): Creates a number of users of the given gender, stored as sequentially-numbered instance attributes.
                test_get_like_gender_if_there_are_no_liked_and_liking_users(self): Asserts get_like_gender returns 'other' with no likes, and the matched gender once gender_to_match is set.
                test_get_like_gender_for_15_liked_and_liking_users(self): Asserts get_like_gender correctly reports the predominant gender across a range of liked/liking user combinations, with up to 15 users of mixed genders.
                test_get_like_gender_for_35_liked_and_liking_users(self): Asserts get_like_gender correctly reports the predominant gender across a range of liked/liking user combinations, with up to 35 users of mixed genders.
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

            Methods:
                set_up(self): Creates two users (user_1, user_2).
                test_user_gets_notified_on_like(self): Asserts an email is sent when a user with notify_on_like enabled is liked.
                test_user_doesnt_get_notified_on_like(self): Asserts no email is sent when a user with notify_on_like disabled is liked.
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
        class LikeNotificationsAllMainLanguagesFrenchTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (French).

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
        class LikeNotificationsAllMainLanguagesGermanTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (German).

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
        class LikeNotificationsAllMainLanguagesSpanishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Spanish).

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
        class LikeNotificationsAllMainLanguagesPortugueseTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Portuguese).

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
        class LikeNotificationsAllMainLanguagesItalianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Italian).

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
        class LikeNotificationsAllMainLanguagesDutchTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Dutch).

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
        class LikeNotificationsAllMainLanguagesHebrewTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            """
            Tests like email notifications for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


