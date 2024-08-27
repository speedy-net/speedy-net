from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase

        from speedy.core.accounts.utils import normalize_email


        class NormalizeEmailOnlyEnglishTestCase(SiteTestCase):
            def test_normalize_none(self):
                self.assertEqual(first=normalize_email(email=None), second='')

            def test_normalize_empty_string(self):
                self.assertEqual(first=normalize_email(email=''), second='')

            def test_normalize_strings(self):
                self.assertEqual(first=normalize_email(email=' '), second=' ')
                self.assertEqual(first=normalize_email(email='  '), second='  ')
                self.assertEqual(first=normalize_email(email='   '), second='   ')
                self.assertEqual(first=normalize_email(email='l'), second='l')
                self.assertEqual(first=normalize_email(email='lll'), second='lll')
                self.assertEqual(first=normalize_email(email='hello'), second='hello')
                self.assertEqual(first=normalize_email(email='HELLO'), second='hello')
                self.assertEqual(first=normalize_email(email=' l '), second=' l ')
                self.assertEqual(first=normalize_email(email=' lll '), second=' lll ')
                self.assertEqual(first=normalize_email(email=' hello '), second=' hello ')
                self.assertEqual(first=normalize_email(email=' HELLO '), second=' hello ')

            def test_normalize_emails(self):
                self.assertEqual(first=normalize_email(email='mike@example.com'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email='MIKE@example.com'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email='mike@EXAMPLE.COM'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email='MIKE@EXAMPLE.COM'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' mike@example.com '), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' MIKE@example.com '), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' mike@EXAMPLE.COM '), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' MIKE@EXAMPLE.COM '), second='mike@example.com')


