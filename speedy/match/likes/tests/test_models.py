from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random

        from django.test import override_settings
        from django.core import mail

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
            def set_up(self):
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
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=len(UserLike.objects.filter(from_user=user)), second=likes_from_user)
                self.assertEqual(first=UserLike.objects.filter(from_user=user).count(), second=likes_from_user)
                self.assertEqual(first=user.likes_from_user.count(), second=likes_from_user)
                self.assertEqual(first=len(UserLike.objects.filter(to_user=user)), second=likes_to_user)
                self.assertEqual(first=UserLike.objects.filter(to_user=user).count(), second=likes_to_user)
                self.assertEqual(first=user.likes_to_user.count(), second=likes_to_user)
                self.assertEqual(first=user.speedy_match_profile.likes_to_user_count, second=likes_to_user)

            def test_set_up(self):
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)

            def test_if_no_relation_between_users_nothing_get_affected(self):
                Block.objects.block(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)
                Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
                self.assert_counters(user=self.user_1, likes_from_user=2, likes_to_user=1)
                self.assert_counters(user=self.user_2, likes_from_user=1, likes_to_user=2)

            def test_if_user1_blocked_user2_like_is_removed(self):
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
            def set_up(self):
                super().set_up()
                self.user_1 = ActiveUserFactory(gender=User.GENDER_FEMALE)
                self.user_2 = ActiveUserFactory(gender=User.GENDER_MALE)
                self.user_3 = ActiveUserFactory(gender=User.GENDER_OTHER)

            def _create_users(self, users_count, gender):
                for i in range(users_count):
                    setattr(self, "user_{}".format(4 + i), ActiveUserFactory(gender=gender))

            def test_get_like_gender_if_there_are_no_liked_and_liking_users(self):
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second="other")
                for gender in User.GENDER_VALID_VALUES:
                    for user in [self.user_1, self.user_2, self.user_3]:
                        user.speedy_match_profile.gender_to_match = [gender]
                        user.save_user_and_profile()
                        self.assertEqual(first=user.speedy_match_profile.get_like_gender(), second=User.GENDERS_DICT[gender])

            def test_get_like_gender_for_15_liked_and_liking_users(self):
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


        class LikeNotificationsTestCaseMixin(SpeedyCoreAccountsModelsMixin, SpeedyMatchLikesLanguageMixin):
            def set_up(self):
                super().set_up()
                self.user_1 = ActiveUserFactory()
                self.user_2 = ActiveUserFactory()

            def test_user_gets_notified_on_like(self):
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
        class LikeNotificationsEnglishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class LikeNotificationsFrenchTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class LikeNotificationsGermanTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class LikeNotificationsSpanishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class LikeNotificationsPortugueseTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class LikeNotificationsItalianTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class LikeNotificationsDutchTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sv')
        class LikeNotificationsSwedishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ko')
        class LikeNotificationsKoreanTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fi')
        class LikeNotificationsFinnishTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class LikeNotificationsHebrewTestCase(LikeNotificationsTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


