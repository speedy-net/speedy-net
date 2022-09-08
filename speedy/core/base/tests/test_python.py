from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.models import SiteTestCase


    class PythonTestCase(SiteTestCase):
        def test_501_digits(self):
            int("-5" + "0" * 500)
            int("5" + "0" * 500)

        def test_1001_digits(self):
            int("-5" + "0" * 1000)
            int("5" + "0" * 1000)

        def test_2001_digits(self):
            int("-5" + "0" * 2000)
            int("5" + "0" * 2000)

        def test_4001_digits(self):
            int("-5" + "0" * 4000)
            int("5" + "0" * 4000)

        def test_4300_digits(self):
            int("-5" + "0" * 4299)
            int("5" + "0" * 4299)

        def test_4301_digits(self):
            with self.assertRaises(ValueError) as cm:
                int("-5" + "0" * 4300)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=4301))
            with self.assertRaises(ValueError) as cm:
                int("5" + "0" * 4300)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=4301))

        def test_5001_digits(self):
            with self.assertRaises(ValueError) as cm:
                int("-5" + "0" * 5000)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=5001))
            with self.assertRaises(ValueError) as cm:
                int("5" + "0" * 5000)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=5001))

        def test_50001_digits(self):
            with self.assertRaises(ValueError) as cm:
                int("-5" + "0" * 50000)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=50001))
            with self.assertRaises(ValueError) as cm:
                int("5" + "0" * 50000)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=50001))

        def test_500001_digits(self):
            with self.assertRaises(ValueError) as cm:
                int("-5" + "0" * 500000)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=500001))
            with self.assertRaises(ValueError) as cm:
                int("5" + "0" * 500000)
            self.assertEqual(first=str(cm.exception), second="Exceeds the limit (4300) for integer string conversion: value has {digits} digits".format(digits=500001))

