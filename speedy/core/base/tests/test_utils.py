from django.conf import settings as django_settings

if (django_settings.TESTS):
    from datetime import date

    from speedy.core.base.test.models import SiteTestCase

    from speedy.core.base.utils import normalize_slug, normalize_username, timesince


    class NormalizeSlugOnlyEnglishTestCase(SiteTestCase):
        def test_normalize_none(self):
            with self.assertRaises(AttributeError) as cm:
                normalize_slug(slug=None)
            self.assertEqual(first=str(cm.exception), second="'NoneType' object has no attribute 'lower'")

        def test_normalize_empty_string(self):
            self.assertEqual(first=normalize_slug(slug=''), second='')

        def test_normalize_strings(self):
            self.assertEqual(first=normalize_slug(slug=' '), second='')
            self.assertEqual(first=normalize_slug(slug='  '), second='')
            self.assertEqual(first=normalize_slug(slug='   '), second='')
            self.assertEqual(first=normalize_slug(slug='l'), second='l')
            self.assertEqual(first=normalize_slug(slug='lll'), second='lll')
            self.assertEqual(first=normalize_slug(slug='hello'), second='hello')
            self.assertEqual(first=normalize_slug(slug='HELLO'), second='hello')
            self.assertEqual(first=normalize_slug(slug=' l '), second='l')
            self.assertEqual(first=normalize_slug(slug=' lll '), second='lll')
            self.assertEqual(first=normalize_slug(slug=' hello '), second='hello')
            self.assertEqual(first=normalize_slug(slug=' HELLO '), second='hello')

        def test_convert_to_lowercase(self):
            self.assertEqual(first=normalize_slug(slug='CamelCase'), second='camelcase')
            self.assertEqual(first=normalize_slug(slug='UPPERCASE'), second='uppercase')
            self.assertEqual(first=normalize_slug(slug='lowercase'), second='lowercase')

        def test_convert_dots_to_dashes(self):
            self.assertEqual(first=normalize_slug(slug='one.dot'), second='one-dot')
            self.assertEqual(first=normalize_slug(slug='two..dot.s'), second='two-dot-s')

        def test_convert_underscores_to_dashes(self):
            self.assertEqual(first=normalize_slug(slug='one_underscore'), second='one-underscore')
            self.assertEqual(first=normalize_slug(slug='two__under_scores'), second='two-under-scores')

        def test_convert_multiple_dashes_to_one(self):
            self.assertEqual(first=normalize_slug(slug='three---dash---es'), second='three-dash-es')

        def test_cut_leading_symbols(self):
            self.assertEqual(first=normalize_slug(slug='-dash'), second='dash')
            self.assertEqual(first=normalize_slug(slug='..dots'), second='dots')
            self.assertEqual(first=normalize_slug(slug='_under_score'), second='under-score')

        def test_cut_trailing_symbols(self):
            self.assertEqual(first=normalize_slug(slug='dash-'), second='dash')
            self.assertEqual(first=normalize_slug(slug='dots...'), second='dots')
            self.assertEqual(first=normalize_slug(slug='under_score_'), second='under-score')


    class NormalizeUsernameOnlyEnglishTestCase(SiteTestCase):
        def test_normalize_none(self):
            with self.assertRaises(AttributeError) as cm:
                normalize_username(username=None)
            self.assertEqual(first=str(cm.exception), second="'NoneType' object has no attribute 'lower'")

        def test_normalize_empty_string(self):
            self.assertEqual(first=normalize_username(username=''), second='')

        def test_normalize_strings(self):
            self.assertEqual(first=normalize_username(username=' '), second='')
            self.assertEqual(first=normalize_username(username='  '), second='')
            self.assertEqual(first=normalize_username(username='   '), second='')
            self.assertEqual(first=normalize_username(username='l'), second='l')
            self.assertEqual(first=normalize_username(username='lll'), second='lll')
            self.assertEqual(first=normalize_username(username='hello'), second='hello')
            self.assertEqual(first=normalize_username(username='HELLO'), second='hello')
            self.assertEqual(first=normalize_username(username=' l '), second='l')
            self.assertEqual(first=normalize_username(username=' lll '), second='lll')
            self.assertEqual(first=normalize_username(username=' hello '), second='hello')
            self.assertEqual(first=normalize_username(username=' HELLO '), second='hello')

        def test_remove_dashes_dots_and_underscores(self):
            self.assertEqual(first=normalize_username(username='this-is-a-slug'), second='thisisaslug')
            self.assertEqual(first=normalize_username(username='.this_is...a_slug--'), second='thisisaslug')


    class TimeSinceOnlyEnglishTestCase(SiteTestCase):
        def test_timesince(self):
            today = date.today()
            self.assertEqual(first=timesince(d=today, now=today), second="")


