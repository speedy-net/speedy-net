from datetime import date

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_speedy_net
from speedy.core.accounts.models import User
from speedy.core.accounts.tests.test_factories import DefaultUserFactory, InactiveUserFactory


@only_on_speedy_net
class SpeedyNetSiteProfileTestCase(SiteTestCase):
    def get_default_user_doron(self):
        user = DefaultUserFactory(first_name="Doron", last_name="Matalon", slug="doron-matalon", date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
        user.save_user_and_profile()
        return user

    def get_inactive_user_jennifer(self):
        user = InactiveUserFactory(first_name="Jennifer", last_name="Connelly", slug="jennifer-connelly", date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
        user.save_user_and_profile()
        return user

    def test_call_activate_directly_and_assert_no_exception(self):
        user = self.get_inactive_user_jennifer()
        self.assertEqual(first=user.is_active, second=False)
        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
        user.speedy_net_profile.activate()
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)

    def test_call_deactivate_directly_and_assert_no_exception(self):
        user = self.get_default_user_doron()
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.speedy_net_profile.is_active, second=True)
        user.speedy_net_profile.deactivate()
        self.assertEqual(first=user.is_active, second=False)
        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)

    def test_call_get_name_directly_and_assert_no_exception(self):
        user = self.get_default_user_doron()
        self.assertEqual(first=user.speedy_net_profile.get_name(), second="Jennifer Connelly")

    def test_call_call_after_verify_email_address_directly_and_assert_no_exception(self):
        user = self.get_inactive_user_jennifer()
        self.assertEqual(first=user.is_active, second=False)
        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
        user.speedy_match_profile.call_after_verify_email_address()
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)

    def test_call_validate_profile_and_activate_directly_and_assert_exception(self):
        user = self.get_inactive_user_jennifer()
        self.assertEqual(first=user.is_active, second=False)
        self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
        with self.assertRaises(NotImplementedError) as cm:
            user.speedy_match_profile.validate_profile_and_activate()
        self.assertEqual(first=str(cm.exception), second="___validate_profile_and_activate is not implemented.")
        self.assertEqual(first=user.is_active, second=True)
        self.assertEqual(first=user.speedy_match_profile.is_active, second=False)

    def test_call_str_of_user_directly_and_assert_no_exception(self):
        user = self.get_default_user_doron()
        self.assertEqual(first=str(user), second="Jennifer Connelly")


