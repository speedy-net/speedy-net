from datetime import date

from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_speedy_net
    from speedy.core.accounts.models import User
    from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
    from speedy.core.accounts.test.user_factories import DefaultUserFactory, InactiveUserFactory, ActiveUserFactory


    @only_on_speedy_net
    class SpeedyNetSiteProfileTestCase(SiteTestCase):
        def get_default_user_doron(self):
            user = DefaultUserFactory(first_name_en="Doron", last_name_en="Matalon", slug="doron-matalon", date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
            user.save_user_and_profile()
            return user

        def get_inactive_user_jennifer(self):
            user = InactiveUserFactory(first_name_en="Jennifer", last_name_en="Connelly", slug="jennifer-connelly", date_of_birth=date(year=1978, month=9, day=12), gender=User.GENDER_FEMALE)
            user.save_user_and_profile()
            return user

        def test_profile_property_and_class(self):
            from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

            user = self.get_default_user_doron()
            self.assertEqual(first=user.profile, second=user.speedy_net_profile)
            self.assertEqual(first=user.profile.pk, second=user.speedy_net_profile.pk)
            self.assertEqual(first=user.profile.__class__, second=user.speedy_net_profile.__class__)
            self.assertEqual(first=user.profile.__class__, second=SpeedyNetSiteProfile)
            self.assertEqual(first=user.profile.__class__.__name__, second="SiteProfile")
            self.assertEqual(first=user.speedy_net_profile.__class__, second=SpeedyNetSiteProfile)
            self.assertEqual(first=user.speedy_net_profile.__class__.__name__, second="SiteProfile")
            self.assertEqual(first=user.speedy_match_profile.__class__, second=SpeedyMatchSiteProfile)
            self.assertNotEqual(first=user.speedy_match_profile, second=user.profile)
            self.assertNotEqual(first=user.speedy_match_profile.__class__, second=user.profile.__class__)
            self.assertNotEqual(first=user.speedy_match_profile.__class__, second=SpeedyNetSiteProfile)

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

        def test_call_call_after_verify_email_address_directly_and_assert_no_exception(self):
            user = self.get_inactive_user_jennifer()
            self.assertEqual(first=user.is_active, second=False)
            self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
            user.speedy_net_profile.call_after_verify_email_address()
            self.assertEqual(first=user.is_active, second=False)
            self.assertEqual(first=user.speedy_net_profile.is_active, second=False)

        def test_call_validate_profile_and_activate_directly_and_assert_exception(self):
            user = self.get_inactive_user_jennifer()
            self.assertEqual(first=user.is_active, second=False)
            self.assertEqual(first=user.speedy_net_profile.is_active, second=False)
            with self.assertRaises(NotImplementedError) as cm:
                user.speedy_net_profile.validate_profile_and_activate()
            self.assertEqual(first=str(cm.exception), second="validate_profile_and_activate is not implemented.")
            self.assertEqual(first=user.is_active, second=False)
            self.assertEqual(first=user.speedy_net_profile.is_active, second=False)

        def test_call_get_name_directly_and_assert_no_exception(self):
            user = self.get_default_user_doron()
            self.assertEqual(first=user.speedy_net_profile.get_name(), second="Doron Matalon")

        def test_call_user_name_directly_and_assert_no_exception(self):
            user = self.get_default_user_doron()
            self.assertEqual(first=user.name, second="Doron Matalon")

        def test_user_name_is_the_same_as_get_name_and_get_full_name(self):
            for user in [self.get_default_user_doron(), self.get_inactive_user_jennifer(), DefaultUserFactory(), InactiveUserFactory(), ActiveUserFactory()]:
                self.assertEqual(first=user.name, second=user.speedy_net_profile.get_name())
                self.assertEqual(first=user.name, second=user.get_full_name())
                self.assertEqual(first=user.name, second='{} {}'.format(user.first_name, user.last_name))
                self.assertNotEqual(first=user.name, second=user.get_first_name())
                self.assertNotEqual(first=user.name, second='{}'.format(user.first_name))
                self.assertNotEqual(first=str(user), second=user.name)

        def test_cannot_delete_site_profiles_with_queryset_delete(self):
            with self.assertRaises(NotImplementedError) as cm:
                SpeedyNetSiteProfile.objects.delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                SpeedyNetSiteProfile.objects.all().delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                SpeedyNetSiteProfile.objects.filter(pk=1).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
            with self.assertRaises(NotImplementedError) as cm:
                SpeedyNetSiteProfile.objects.all().exclude(pk=2).delete()
            self.assertEqual(first=str(cm.exception), second="delete is not implemented.")


