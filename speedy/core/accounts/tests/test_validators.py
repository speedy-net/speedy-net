from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from types import SimpleNamespace

        from django.core.exceptions import ValidationError

        from speedy.core.base.test.models import SiteTestCase

        from speedy.core.accounts.validators import validate_profile_picture


        class ValidateProfilePictureOnlyEnglishTestCase(SiteTestCase):
            """
            Tests speedy.core.accounts.validators.validate_profile_picture.

            This validator has no dedicated or indirect test coverage anywhere in the repository (the
            "A profile picture is required" branch is exercised only in speedy.match registration tests,
            and the file size branch is not exercised anywhere).
            """
            def test_none_profile_picture_raises_required_error(self):
                with self.assertRaises(ValidationError) as cm:
                    validate_profile_picture(profile_picture=None)
                self.assertEqual(first=cm.exception.messages, second=["A profile picture is required."])

            def test_profile_picture_within_size_limit_is_valid(self):
                profile_picture = SimpleNamespace(size=django_settings.MAX_PHOTO_SIZE)
                self.assertIsNone(obj=validate_profile_picture(profile_picture=profile_picture))

            def test_profile_picture_exceeding_size_limit_raises_error(self):
                profile_picture = SimpleNamespace(size=django_settings.MAX_PHOTO_SIZE + 1)
                with self.assertRaises(ValidationError) as cm:
                    validate_profile_picture(profile_picture=profile_picture)
                self.assertEqual(first=cm.exception.messages, second=["This picture's file size is too big. The maximal file size allowed is 30 MB."])


