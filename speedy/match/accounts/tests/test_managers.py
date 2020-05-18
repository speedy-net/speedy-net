from time import sleep

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
            """
            Test that blocked and blocking users don't appear in matches list.
            """
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
            """
            Test that users with non-matching genders don't appear in matches list.
            """
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

        def test_matches_list_sorted_by_speedy_match_last_visit(self):
            """
            Test that SpeedyMatchSiteProfile.objects.get_matches() returns a matches list sorted by Speedy Match last visit time (if all ranks are equal).
            Speedy Net last visit time is ignored.
            """
            sleep(0.2)
            self.user_2.profile.update_last_visit()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertEqual(first=matches_list[:1], second=[self.user_2])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5, 5, 5])
            sleep(0.1)
            self.user_3.speedy_match_profile.update_last_visit()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertEqual(first=matches_list[:2], second=[self.user_3, self.user_2])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5, 5, 5])
            sleep(0.1)
            self.user_4.speedy_net_profile.update_last_visit()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertEqual(first=matches_list[:2], second=[self.user_3, self.user_2])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5, 5, 5])
            sleep(0.1)
            self.user_4.speedy_match_profile.update_last_visit()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_1)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertEqual(first=matches_list, second=[self.user_4, self.user_3, self.user_2, self.user_5])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5, 5, 5])
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertEqual(first=matches_list, second=[self.user_4, self.user_3, self.user_2, self.user_1])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5, 5, 5])

        def test_matches_list_sorted_by_rank(self):
            sleep(0.2)
            self.user_3.speedy_match_profile.update_last_visit()
            self.user_1.diet = User.DIET_VEGAN
            self.user_2.diet = User.DIET_VEGETARIAN
            self.user_3.diet = User.DIET_CARNIST
            self.user_4.diet = User.DIET_VEGAN
            self.user_5.diet = User.DIET_CARNIST
            self.user_1.smoking_status = User.SMOKING_STATUS_NOT_SMOKING
            self.user_2.smoking_status = User.SMOKING_STATUS_NOT_SMOKING
            self.user_3.smoking_status = User.SMOKING_STATUS_NOT_SMOKING
            self.user_4.smoking_status = User.SMOKING_STATUS_SMOKING_OCCASIONALLY
            self.user_5.smoking_status = User.SMOKING_STATUS_SMOKING
            self.user_1.relationship_status = User.RELATIONSHIP_STATUS_SINGLE
            self.user_2.relationship_status = User.RELATIONSHIP_STATUS_DIVORCED
            self.user_3.relationship_status = User.RELATIONSHIP_STATUS_WIDOWED
            self.user_4.relationship_status = User.RELATIONSHIP_STATUS_MARRIED
            self.user_5.relationship_status = User.RELATIONSHIP_STATUS_IN_RELATIONSHIP
            self.user_5.speedy_match_profile.diet_match = {str(User.DIET_VEGAN): 2, str(User.DIET_VEGETARIAN): 4, str(User.DIET_CARNIST): 5}
            self.user_5.speedy_match_profile.smoking_status_match = {str(User.SMOKING_STATUS_NOT_SMOKING): 5, str(User.SMOKING_STATUS_SMOKING_OCCASIONALLY): 1, str(User.SMOKING_STATUS_SMOKING): 0}
            self.user_5.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_3
            self.user_2.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_IN_RELATIONSHIP)] = SpeedyMatchSiteProfile.RANK_2
            self.user_2.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_IN_OPEN_RELATIONSHIP)] = SpeedyMatchSiteProfile.RANK_1
            self.user_2.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_MARRIED)] = SpeedyMatchSiteProfile.RANK_0
            self.user_1.save_user_and_profile()
            self.user_2.save_user_and_profile()
            self.user_3.save_user_and_profile()
            self.user_4.save_user_and_profile()
            self.user_5.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertEqual(first=matches_list, second=[self.user_3, self.user_2, self.user_1, self.user_4])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 4, 2, 1])
            self.user_5.speedy_match_profile.diet_match = {str(User.DIET_VEGAN): 5, str(User.DIET_VEGETARIAN): 4, str(User.DIET_CARNIST): 2}
            self.user_5.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_5)
            self.assertEqual(first=len(matches_list), second=4)
            self.assertEqual(first=matches_list, second=[self.user_1, self.user_2, self.user_3, self.user_4])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 4, 2, 1])
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_2)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertEqual(first=matches_list, second=[self.user_3, self.user_1, self.user_5])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5, 2])
            self.user_5.speedy_match_profile.relationship_status_match[str(User.RELATIONSHIP_STATUS_DIVORCED)] = SpeedyMatchSiteProfile.RANK_0
            self.user_5.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_2)
            self.assertEqual(first=len(matches_list), second=2)
            self.assertEqual(first=matches_list, second=[self.user_3, self.user_1])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5])
            self.user_4.relationship_status = User.RELATIONSHIP_STATUS_IN_OPEN_RELATIONSHIP
            self.user_4.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_2)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertEqual(first=matches_list, second=[self.user_3, self.user_1, self.user_4])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 5, 1])
            self.user_3.relationship_status = User.RELATIONSHIP_STATUS_IN_OPEN_RELATIONSHIP
            self.user_3.save_user_and_profile()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_2)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertEqual(first=matches_list, second=[self.user_1, self.user_3, self.user_4])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 1, 1])
            sleep(0.01)
            self.user_4.speedy_match_profile.update_last_visit()
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.user_2)
            self.assertEqual(first=len(matches_list), second=3)
            self.assertEqual(first=matches_list, second=[self.user_1, self.user_4, self.user_3])
            self.assertEqual(first=[u.speedy_match_profile.rank for u in matches_list], second=[5, 1, 1])

        def test_cannot_delete_site_profiles_with_queryset_delete(self):
            with self.assertRaises(NotImplementedError) as cm:
                SpeedyMatchSiteProfile.objects.all().delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                SpeedyMatchSiteProfile.objects.filter(pk=1).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")


