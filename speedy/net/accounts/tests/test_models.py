from datetime import date

from speedy.core.base.test import TestCase, only_on_speedy_net
from speedy.core.accounts.models import User
from speedy.core.accounts.tests.test_factories import DefaultUserFactory, InactiveUserFactory


@only_on_speedy_net
class SpeedyNetSiteProfileTestCase(TestCase):
    def get_default_user_1(self):
        user = DefaultUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
        user.save_user_and_profile()
        return user

    def get_default_user_2(self):
        user = InactiveUserFactory(first_name='Jesse', last_name='Pinkman', slug='jesse-pinkman', date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
        user.save_user_and_profile()
        return user

    def test_call_activate_directly_and_assert_no_exception(self):
        user = self.get_default_user_2()
        self.assertEqual(first=user.is_active, second=False)
        self.assertEqual(first=user.profile.is_active, second=False)
        user.profile.activate()
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.profile.is_active, second=True)

    def test_call_deactivate_directly_and_assert_no_exception(self):
        user = self.get_default_user_1()
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.profile.is_active, second=True)
        user.profile.deactivate()
        self.assertEqual(first=user.is_active, second=False)
        self.assertEqual(first=user.profile.is_active, second=False)

    def test_call_get_name_directly_and_assert_no_exception(self):
        user = self.get_default_user_1()
        self.assertEqual(first=user.profile.get_name(), second='Jesse Pinkman')

    def test_call_str_of_user_directly_and_assert_no_exception(self):
        user = self.get_default_user_1()
        self.assertEqual(first=str(user), second='Jesse Pinkman')


