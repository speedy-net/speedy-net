from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_speedy_match
    from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
    from speedy.core.accounts.models import User
    from speedy.core.accounts.test.user_factories import ActiveUserFactory
    from speedy.core.blocks.models import Block


    @only_on_speedy_match
    class ManagerBlocksTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory()
            self.user_2 = ActiveUserFactory()
            self.user_3 = ActiveUserFactory(gender=User.GENDER_FEMALE)
            self.user_4 = ActiveUserFactory(gender=User.GENDER_MALE)
            self.user_5 = ActiveUserFactory(gender=User.GENDER_OTHER)

        def test_set_up(self):
            self.assertEqual(first=User.objects.count(), second=5)

        def test_blocked_users_dont_appear_in_matches_list(self):
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertTrue(self.user_2 in matches_list)
            Block.objects.block(blocker=self.user_1, blocked=self.user_2)
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertTrue(self.user_2 not in matches_list)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertTrue(self.user_2 in matches_list)
            Block.objects.block(blocker=self.user_2, blocked=self.user_1)
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertTrue(self.user_2 not in matches_list)
            Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertTrue(self.user_2 in matches_list)
            Block.objects.block(blocker=self.user_1, blocked=self.user_2)
            Block.objects.block(blocker=self.user_2, blocked=self.user_1)
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertTrue(self.user_2 not in matches_list)
            Block.objects.unblock(blocker=self.user_1, blocked=self.user_2)
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertTrue(self.user_2 not in matches_list)
            Block.objects.unblock(blocker=self.user_2, blocked=self.user_1)
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertTrue(self.user_2 in matches_list)


    @only_on_speedy_match
    class ManagerMatchesTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.user_1 = ActiveUserFactory(gender=User.GENDER_FEMALE)
            self.user_2 = ActiveUserFactory(gender=User.GENDER_MALE)
            self.user_3 = ActiveUserFactory(gender=User.GENDER_FEMALE)
            self.user_4 = ActiveUserFactory(gender=User.GENDER_MALE)
            self.user_5 = ActiveUserFactory(gender=User.GENDER_OTHER)

        def test_set_up(self):
            self.assertEqual(first=User.objects.count(), second=5)

        def test_gender_doesnt_match_profile_in_matches_list(self):
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertTrue(self.user_4 in matches_list)
            self.user_4.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE, User.GENDER_MALE]
            self.user_4.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertTrue(0 < len(matches_list) < 4)
            self.assertTrue(self.user_4 not in matches_list)
            self.user_4.speedy_match_profile.gender_to_match = User.GENDER_VALID_VALUES
            self.user_4.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertTrue(self.user_4 in matches_list)
            self.user_5.speedy_match_profile.gender_to_match = [User.GENDER_OTHER]
            self.user_5.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=0)
            self.assertTrue(self.user_4 not in matches_list)
            self.user_5.speedy_match_profile.gender_to_match = User.GENDER_VALID_VALUES
            self.user_5.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertTrue(self.user_4 in matches_list)
            self.user_5.speedy_match_profile.gender_to_match = [User.GENDER_FEMALE]
            self.user_5.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=2)
            self.assertTrue(self.user_1 in matches_list)
            self.assertTrue(self.user_2 not in matches_list)
            self.assertTrue(self.user_3 in matches_list)
            self.assertTrue(self.user_4 not in matches_list)


