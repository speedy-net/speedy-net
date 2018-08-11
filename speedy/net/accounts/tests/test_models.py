from datetime import datetime

from speedy.core.base.test import TestCase, only_on_speedy_net
from speedy.core.accounts.models import User
from speedy.core.accounts.tests.test_factories import DefaultUserFactory, InactiveUserFactory


@only_on_speedy_net
class SiteProfileTestCase(TestCase):
    def get_default_user_1(self):
        user_1 = InactiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=datetime(year=1978, month=9, day=12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGAN)
        user_1.save()
        return user_1

    def get_default_user_2(self):
        user_2 = DefaultUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=datetime(year=1978, month=9, day=12), gender=User.GENDER_FEMALE, diet=User.DIET_VEGAN)
        return user_2

    def test_call_activate_directly_and_assert_no_exception(self):
        user_1 = self.get_default_user_1()
        self.assertEqual(first=user_1.profile.is_active, second=False)
        user_1.profile.activate()
        self.assertEqual(first=user_1.profile.is_active, second=True)

    def test_call_deactivate_directly_and_assert_no_exception(self):
        user_1 = self.get_default_user_2()
        self.assertEqual(first=user_1.profile.is_active, second=True)
        user_1.profile.deactivate()
        self.assertEqual(first=user_1.profile.is_active, second=False)

    def test_call_get_name_directly_and_assert_no_exception(self):
        user_1 = self.get_default_user_1()
        self.assertEqual(first=user_1.profile.get_name(), second='Jesse Pinkman')

    def test_call_str_of_user_directly_and_assert_no_exception(self):
        user_1 = self.get_default_user_1()
        self.assertEqual(first=str(user_1), second='Jesse Pinkman')


