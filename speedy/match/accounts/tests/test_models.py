from datetime import datetime

from speedy.core.base.test import TestCase
from ..models import SiteProfile
from speedy.core.accounts.tests.test_factories import UserFactory, User


class SiteProfileTestCase(TestCase):
    def test_get_active_languages(self):
        p = SiteProfile(active_languages='en, he, de')
        self.assertListEqual(list1=p.get_active_languages(), list2=['en', 'he', 'de'])
        p = SiteProfile(active_languages='')
        self.assertListEqual(list1=p.get_active_languages(), list2=[])

    def test_set_active_languages(self):
        p = SiteProfile()
        p.set_active_languages(['en', 'he'])
        self.assertSetEqual(set1=set(p.get_active_languages()), set2={'en', 'he'})


class SiteProfileMatchTestCase(TestCase):

    def test_gender_doesnt_match_profile(self):
        user1 = UserFactory(first_name='Walter', last_name='White', slug='walter', date_of_birth=datetime(1958, 10, 22), gender=User.GENDER_MALE)
        user1.profile.gender_to_match = [User.GENDER_FEMALE]
        user2 = UserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse', date_of_birth=datetime(1978, 9, 12), gender=User.GENDER_MALE)
        rank = user1.profile.matching_function(user2.profile)
        self.assertFalse(rank)

    def test_age_doesnt_match_profile(self):
        user1 = UserFactory(first_name='Walter', last_name='White', slug='walter', date_of_birth=datetime(1958, 10, 22),
                            gender=User.GENDER_MALE)
        user1.profile.min_age_match = 20
        user1.profile.max_age_match = 30
        user2 = UserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse', date_of_birth=datetime(1978, 9, 12),
                            gender=User.GENDER_MALE)
        rank = user1.profile.matching_function(user2.profile)
        self.assertFalse(rank)

    def test_smoking_doesnt_match_prodile(self):
        user1 = UserFactory(first_name='Walter', last_name='White', slug='walter', date_of_birth=datetime(1958, 10, 22),
                            gender=User.GENDER_MALE)
        user1.profile.min_age_match = 20
        user1.profile.max_age_match = 180
        user1.profile.smoking_match = {SiteProfile.SMOKING_YES: 0, SiteProfile.SMOKING_NO: 5, SiteProfile.SMOKING_SOMETIMES: 0}
        user1.profile.save()
        user2 = UserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse', date_of_birth=datetime(1978, 9, 12),
                            gender=User.GENDER_MALE)
        user2.profile.smoking = SiteProfile.SMOKING_YES
        rank = user1.profile.matching_function(user2.profile)
        self.assertFalse(rank)

    def test_match_profile(self):
        user1 = UserFactory(first_name='Walter', last_name='White', slug='walter', date_of_birth=datetime(1958, 10, 22),
                            gender=User.GENDER_MALE, diet=User.DIET_VEGETARIAN)
        user1.profile.smoking = SiteProfile.SMOKING_NO

        user1.profile.min_age_match = 20
        user1.profile.max_age_match = 180
        user1.profile.smoking_match = {SiteProfile.SMOKING_YES: 3, SiteProfile.SMOKING_NO: 5, SiteProfile.SMOKING_SOMETIMES: 4}
        user1.profile.diet_match = {User.DIET_VEGAN: 4, User.DIET_VEGETARIAN: 5, User.DIET_CARNIST: 0}

        user2 = UserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse', date_of_birth=datetime(1978, 9, 12),
                            gender=User.GENDER_MALE, diet=User.DIET_VEGETARIAN)
        user2.profile.smoking = 1
        user2.diet = User.DIET_VEGAN
        rank = user1.profile.matching_function(user2.profile)
        self.assertEqual(rank, 3)
