"""
Test cases for the utility functions of the Speedy Core accounts app.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from speedy.core.base.test.models import SiteTestCase

        from speedy.core.accounts.utils import normalize_email


        class NormalizeEmailOnlyEnglishTestCase(SiteTestCase):
            """
            Tests speedy.core.accounts.utils.normalize_email, run only once (in English) since it is language-independent.

            Methods:
                test_normalize_none(self): Asserts that normalizing None returns an empty string.
                test_normalize_empty_string(self): Asserts that normalizing an empty string returns an empty string.
                test_normalize_strings(self): Asserts that non-email strings are only lowercased, leading/trailing whitespace is preserved.
                test_normalize_emails(self): Asserts that email addresses are lowercased and have their leading/trailing whitespace trimmed.
            """

            def test_normalize_none(self):
                """
                Asserts that normalizing None returns an empty string.
                """
                self.assertEqual(first=normalize_email(email=None), second='')

            def test_normalize_empty_string(self):
                """
                Asserts that normalizing an empty string returns an empty string.
                """
                self.assertEqual(first=normalize_email(email=''), second='')

            def test_normalize_strings(self):
                """
                Asserts that normalizing non-email strings only lowercases them, while leading and trailing whitespace is preserved.
                """
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
                """
                Asserts that normalizing email addresses lowercases them and trims leading and trailing whitespace.
                """
                self.assertEqual(first=normalize_email(email='mike@example.com'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email='MIKE@example.com'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email='mike@EXAMPLE.COM'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email='MIKE@EXAMPLE.COM'), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' mike@example.com '), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' MIKE@example.com '), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' mike@EXAMPLE.COM '), second='mike@example.com')
                self.assertEqual(first=normalize_email(email=' MIKE@EXAMPLE.COM '), second='mike@example.com')


