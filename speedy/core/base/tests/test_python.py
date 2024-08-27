from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import SpeedyCoreBaseLanguageMixin
    from speedy.core.base.test.models import SiteTestCase


    class PythonOnlyEnglishTestCase(SpeedyCoreBaseLanguageMixin, SiteTestCase):
        def test_501_digits(self):
            for f in ["-5", "5"]:
                int(f + "0" * 500)

        def test_1001_digits(self):
            for f in ["-5", "5"]:
                int(f + "0" * 1000)

        def test_2001_digits(self):
            for f in ["-5", "5"]:
                int(f + "0" * 2000)

        def test_4001_digits(self):
            for f in ["-5", "5"]:
                int(f + "0" * 4000)

        def test_4300_digits(self):
            for f in ["-5", "5"]:
                int(f + "0" * 4299)

        def test_4301_digits(self):
            for f in ["-5", "5"]:
                with self.assertRaises(ValueError) as cm:
                    int(f + "0" * 4300)
                self.assertEqual(first=str(cm.exception), second=self._exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_by_digits(digits=4301))

        def test_5001_digits(self):
            for f in ["-5", "5"]:
                with self.assertRaises(ValueError) as cm:
                    int(f + "0" * 5000)
                self.assertEqual(first=str(cm.exception), second=self._exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_by_digits(digits=5001))

        def test_50001_digits(self):
            for f in ["-5", "5"]:
                with self.assertRaises(ValueError) as cm:
                    int(f + "0" * 50000)
                self.assertEqual(first=str(cm.exception), second=self._exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_by_digits(digits=50001))

        def test_500001_digits(self):
            for f in ["-5", "5"]:
                with self.assertRaises(ValueError) as cm:
                    int(f + "0" * 500000)
                self.assertEqual(first=str(cm.exception), second=self._exceeds_the_limit_4300_digits_for_integer_string_conversion_error_message_by_digits(digits=500001))


