from datetime import datetime

from speedy.core.base.test import TestCase
from ..models import SiteProfile
from speedy.core.base.test import exclude_on_speedy_composer, exclude_on_speedy_mail_software, exclude_on_speedy_net
from speedy.core.accounts.tests.test_factories import ActiveUserFactory, User


class SiteProfileTestCase(TestCase):
    def test_get_active_languages(self):
        p = SiteProfile(active_languages='en, he, de')
        self.assertListEqual(list1=p.get_active_languages(), list2=['en', 'he', 'de'])
        p = SiteProfile(active_languages='')
        self.assertListEqual(list1=p.get_active_languages(), list2=[])

    def test_set_active_languages(self):
        p = SiteProfile()
        p._set_active_languages(['en', 'he'])
        self.assertSetEqual(set1=set(p.get_active_languages()), set2={'en', 'he'})


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
@exclude_on_speedy_net
class SiteProfileMatchTestCase(TestCase):
    def get_default_user_1(self):
        user_1 = ActiveUserFactory(first_name='Walter', last_name='White', slug='walter', date_of_birth=datetime(1958, 10, 22), gender=User.GENDER_MALE, diet=User.DIET_VEGETARIAN)
        user_1.profile.smoking = SiteProfile.SMOKING_NO
        user_1.profile.marital_status = SiteProfile.MARITAL_STATUS_SINGLE
        user_1.profile.min_age_match = 20
        user_1.profile.max_age_match = 180
        user_1.profile.gender_to_match = [User.GENDER_FEMALE]
        return user_1

    def get_default_user_2(self):
        user_2 = ActiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse', date_of_birth=datetime(1978, 9, 12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGETARIAN)
        user_2.profile.smoking = SiteProfile.SMOKING_YES
        user_2.profile.marital_status = SiteProfile.MARITAL_STATUS_SINGLE
        user_2.diet = User.DIET_VEGAN
        user_2.profile.gender_to_match = [User.GENDER_MALE]
        return user_2

    def test_gender_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.gender_to_match = [User.GENDER_MALE]
        user_2 = self.get_default_user_2()
        user_2.profile.gender_to_match = [User.GENDER_MALE]
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 0)

    def test_gender_match_profile_different_gender(self):
        user_1 = self.get_default_user_1()
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 5)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 5)

    def test_gender_match_profile_same_gender(self):
        user_1 = self.get_default_user_1()
        user_1.profile.gender_to_match = [User.GENDER_MALE]
        user_2 = self.get_default_user_2()
        user_2.gender = User.GENDER_MALE
        user_2.profile.gender_to_match = [User.GENDER_MALE]
        user_2.save()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 5)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 5)

    def test_age_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.min_age_match = 20
        user_1.profile.max_age_match = 30
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 0)

    def test_smoking_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.smoking_match = {SiteProfile.SMOKING_YES: 0, SiteProfile.SMOKING_NO: 5, SiteProfile.SMOKING_SOMETIMES: 0}
        user_1.profile.save()
        user_2 = self.get_default_user_2()
        user_2.profile.smoking = SiteProfile.SMOKING_YES
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 0)

    def test_marital_status_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.save()
        user_2 = self.get_default_user_2()
        user_2.profile.smoking = SiteProfile.SMOKING_YES
        user_2.profile.marital_status_match[SiteProfile.MARITAL_STATUS_MARRIED] = SiteProfile.RANK_0
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 5)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 5)

    def test_marital_status_doesnt_match_profile(self):
        user_1 = self.get_default_user_1()
        user_1.profile.marital_status = SiteProfile.MARITAL_STATUS_MARRIED
        user_1.profile.save()
        user_2 = self.get_default_user_2()
        user_2.profile.smoking = SiteProfile.SMOKING_YES
        user_2.profile.marital_status_match[SiteProfile.MARITAL_STATUS_MARRIED] = SiteProfile.RANK_0
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 0)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 0)

    def test_match_profile_rank_3(self):
        user_1 = self.get_default_user_1()
        user_1.profile.smoking_match = {SiteProfile.SMOKING_YES: 3, SiteProfile.SMOKING_NO: 5, SiteProfile.SMOKING_SOMETIMES: 4}
        user_1.profile.diet_match = {User.DIET_VEGAN: 4, User.DIET_VEGETARIAN: 5, User.DIET_CARNIST: 0}
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 3)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 5)

    def test_match_profile_rank_4(self):
        user_1 = self.get_default_user_1()
        user_1.profile.diet_match = {User.DIET_VEGAN: 4, User.DIET_VEGETARIAN: 5, User.DIET_CARNIST: 0}
        user_2 = self.get_default_user_2()
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 4)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 5)

    def test_match_profile_rank_1(self):
        user_1 = self.get_default_user_2()
        user_1.profile.smoking_match = {SiteProfile.SMOKING_YES: 3, SiteProfile.SMOKING_NO: 5, SiteProfile.SMOKING_SOMETIMES: 4}
        user_1.profile.diet_match = {User.DIET_VEGAN: 4, User.DIET_VEGETARIAN: 5, User.DIET_CARNIST: 0}
        user_1.profile.marital_status_match[SiteProfile.MARITAL_STATUS_MARRIED] = SiteProfile.RANK_1
        user_2 = self.get_default_user_1()
        user_2.profile.marital_status = SiteProfile.MARITAL_STATUS_MARRIED
        rank_1 = user_1.profile.get_matching_rank(user_2.profile)
        self.assertEqual(rank_1, 1)
        rank_2 = user_2.profile.get_matching_rank(user_1.profile)
        self.assertEqual(rank_2, 5)

