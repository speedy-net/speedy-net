"""
Test cases for the user manager of Speedy Net.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_net

        from speedy.core.accounts.test.user_factories import InactiveUserFactory, ActiveUserFactory

        from speedy.core.accounts.models import User


        @only_on_speedy_net
        class UserManagerOnlyEnglishTestCase(SiteTestCase):
            """
            Test the User manager's mark_a_user_as_deleted method on Speedy Net (English only, the manager logic doesn't depend on the language).

            Methods:
                test_cannot_mark_a_user_as_deleted_with_wrong_delete_password(self): Verify an inactive user cannot be marked as deleted with an incorrect delete password.
                test_cannot_mark_an_active_user_as_deleted(self): Verify an active user cannot be marked as deleted.
                test_cannot_mark_a_staff_user_as_deleted(self): Verify a staff user cannot be marked as deleted.
                test_cannot_mark_a_superuser_as_deleted(self): Verify a superuser cannot be marked as deleted.
            """

            def test_cannot_mark_a_user_as_deleted_with_wrong_delete_password(self):
                """
                Verify an inactive user cannot be marked as deleted with an incorrect delete password.
                """
                user = InactiveUserFactory()
                self.assertEqual(first=user.is_active, second=False)
                self.assertEqual(first=user.is_staff, second=False)
                self.assertEqual(first=user.is_superuser, second=False)
                with self.assertRaises(ValueError) as cm:
                    User.objects.mark_a_user_as_deleted(user=user, delete_password="Wrong delete password.")
                self.assertEqual(first=str(cm.exception), second="The delete password is incorrect.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_deleted, second=False)
                self.assertEqual(first=len(user.email_addresses.all()), second=0)

            def test_cannot_mark_an_active_user_as_deleted(self):
                """
                Verify an active user cannot be marked as deleted.
                """
                user = ActiveUserFactory()
                self.assertEqual(first=user.is_active, second=True)
                self.assertEqual(first=user.is_staff, second=False)
                self.assertEqual(first=user.is_superuser, second=False)
                with self.assertRaises(ValueError) as cm:
                    User.objects.mark_a_user_as_deleted(user=user, delete_password="Mark this user as deleted in Speedy Net.")
                self.assertEqual(first=str(cm.exception), second="User must be inactive to be marked as deleted.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_deleted, second=False)
                self.assertEqual(first=len(user.email_addresses.all()), second=1)

            def test_cannot_mark_a_staff_user_as_deleted(self):
                """
                Verify a staff user cannot be marked as deleted.
                """
                # Note: User.save() requires is_superuser == is_staff, so a staff user must also be a superuser.
                user = InactiveUserFactory(is_staff=True, is_superuser=True)
                # Superusers are not deactivated by SiteProfile.deactivate(), so deactivate is_active explicitly to isolate the staff/superuser guard from the is_active guard.
                user.is_active = False
                user.save_user_and_profile()
                self.assertEqual(first=user.is_active, second=False)
                self.assertEqual(first=user.is_staff, second=True)
                self.assertEqual(first=user.is_superuser, second=True)
                with self.assertRaises(ValueError) as cm:
                    User.objects.mark_a_user_as_deleted(user=user, delete_password="Mark this user as deleted in Speedy Net.")
                self.assertEqual(first=str(cm.exception), second="Staff and superusers cannot be marked as deleted.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_deleted, second=False)
                self.assertEqual(first=len(user.email_addresses.all()), second=0)

            def test_cannot_mark_a_superuser_as_deleted(self):
                """
                Verify a superuser cannot be marked as deleted.
                """
                # Note: User.save() requires is_superuser == is_staff, so a superuser must also be staff.
                user = InactiveUserFactory(is_superuser=True, is_staff=True)
                # Superusers are not deactivated by SiteProfile.deactivate(), so deactivate is_active explicitly to isolate the staff/superuser guard from the is_active guard.
                user.is_active = False
                user.save_user_and_profile()
                self.assertEqual(first=user.is_active, second=False)
                self.assertEqual(first=user.is_staff, second=True)
                self.assertEqual(first=user.is_superuser, second=True)
                with self.assertRaises(ValueError) as cm:
                    User.objects.mark_a_user_as_deleted(user=user, delete_password="Mark this user as deleted in Speedy Net.")
                self.assertEqual(first=str(cm.exception), second="Staff and superusers cannot be marked as deleted.")
                user = User.objects.get(pk=user.pk)
                self.assertEqual(first=user.is_deleted, second=False)
                self.assertEqual(first=len(user.email_addresses.all()), second=0)


