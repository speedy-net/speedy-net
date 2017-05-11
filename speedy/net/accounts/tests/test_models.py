from datetime import datetime

from speedy.core.base.test import TestCase
from speedy.core.accounts.models import User
from speedy.core.accounts.tests.test_factories import DefaultUserFactory, InactiveUserFactory


class SiteProfileTestCase(TestCase):
    def get_default_user_1(self):
        user_1 = InactiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse', date_of_birth=datetime(1978, 9, 12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGAN)
        return user_1

    def get_default_user_2(self):
        user_2 = DefaultUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse', date_of_birth=datetime(1978, 9, 12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGAN)
        return user_2

    def test_call_activate_directly_and_assert_no_exception(self):
        user_1 = self.get_default_user_1()
        self.assertEqual(user_1.profile.is_active, False)
        user_1.profile.activate()
        self.assertEqual(user_1.profile.is_active, True)

    def test_call_deactivate_directly_and_assert_no_exception(self):
        user_1 = self.get_default_user_2()
        self.assertEqual(user_1.profile.is_active, True)
        user_1.profile.deactivate()
        self.assertEqual(user_1.profile.is_active, False)

    def test_call_get_name_directly_and_assert_no_exception(self):
        user_1 = self.get_default_user_1()
        self.assertEqual(user_1.profile.get_name(), 'Jesse Pinkman')


