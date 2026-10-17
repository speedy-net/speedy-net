"""
Test cases for the utility functions of Speedy Core, such as slug and username normalization, age calculation, image analysis and time since formatting.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    import io

    from datetime import date
    from types import SimpleNamespace
    from unittest.mock import patch

    from PIL import Image

    from django.utils.timezone import now as timezone_now

    from speedy.core.base.test.models import SiteTestCase

    from speedy.core.base.utils import normalize_slug, normalize_username, timesince, get_age, get_age_or_default, get_age_ranges_match, is_animated, is_transparent, looks_like_one_color

    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.decorators import only_on_sites_with_login


    class NormalizeSlugOnlyEnglishTestCase(SiteTestCase):
        """
        Tests normalize_slug(), in English.
        """

        def test_normalize_none(self):
            """
            Tests that normalize_slug() raises an AttributeError when called with None.
            """
            with self.assertRaises(AttributeError) as cm:
                normalize_slug(slug=None)
            self.assertEqual(first=str(cm.exception), second="'NoneType' object has no attribute 'lower'")

        def test_normalize_empty_string(self):
            """
            Tests that normalize_slug() returns an empty string when called with an empty string.
            """
            self.assertEqual(first=normalize_slug(slug=''), second='')

        def test_normalize_strings(self):
            """
            Tests that normalize_slug() strips leading/trailing whitespace and lowercases the slug.
            """
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
            """
            Tests that normalize_slug() converts the slug to lowercase.
            """
            self.assertEqual(first=normalize_slug(slug='CamelCase'), second='camelcase')
            self.assertEqual(first=normalize_slug(slug='UPPERCASE'), second='uppercase')
            self.assertEqual(first=normalize_slug(slug='lowercase'), second='lowercase')

        def test_convert_dots_to_dashes(self):
            """
            Tests that normalize_slug() converts one or more consecutive dots to a single dash.
            """
            self.assertEqual(first=normalize_slug(slug='one.dot'), second='one-dot')
            self.assertEqual(first=normalize_slug(slug='two..dot.s'), second='two-dot-s')

        def test_convert_underscores_to_dashes(self):
            """
            Tests that normalize_slug() converts one or more consecutive underscores to a single dash.
            """
            self.assertEqual(first=normalize_slug(slug='one_underscore'), second='one-underscore')
            self.assertEqual(first=normalize_slug(slug='two__under_scores'), second='two-under-scores')

        def test_convert_multiple_dashes_to_one(self):
            """
            Tests that normalize_slug() converts multiple consecutive dashes to a single dash.
            """
            self.assertEqual(first=normalize_slug(slug='three---dash---es'), second='three-dash-es')

        def test_cut_leading_symbols(self):
            """
            Tests that normalize_slug() removes leading dashes, dots and underscores.
            """
            self.assertEqual(first=normalize_slug(slug='-dash'), second='dash')
            self.assertEqual(first=normalize_slug(slug='..dots'), second='dots')
            self.assertEqual(first=normalize_slug(slug='_under_score'), second='under-score')

        def test_cut_trailing_symbols(self):
            """
            Tests that normalize_slug() removes trailing dashes, dots and underscores.
            """
            self.assertEqual(first=normalize_slug(slug='dash-'), second='dash')
            self.assertEqual(first=normalize_slug(slug='dots...'), second='dots')
            self.assertEqual(first=normalize_slug(slug='under_score_'), second='under-score')


    class NormalizeUsernameOnlyEnglishTestCase(SiteTestCase):
        """
        Tests normalize_username(), in English.
        """

        def test_normalize_none(self):
            """
            Tests that normalize_username() raises an AttributeError when called with None.
            """
            with self.assertRaises(AttributeError) as cm:
                normalize_username(username=None)
            self.assertEqual(first=str(cm.exception), second="'NoneType' object has no attribute 'lower'")

        def test_normalize_empty_string(self):
            """
            Tests that normalize_username() returns an empty string when called with an empty string.
            """
            self.assertEqual(first=normalize_username(username=''), second='')

        def test_normalize_strings(self):
            """
            Tests that normalize_username() strips leading/trailing whitespace and lowercases the username.
            """
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
            """
            Tests that normalize_username() removes dashes, dots and underscores from the username.
            """
            self.assertEqual(first=normalize_username(username='this-is-a-slug'), second='thisisaslug')
            self.assertEqual(first=normalize_username(username='.this_is...a_slug--'), second='thisisaslug')


    class GetAgeOnlyEnglishTestCase(SiteTestCase):
        """
        Tests get_age(), in English.
        """

        @patch(target='speedy.core.base.utils.date')
        def test_birthday_already_passed_this_year(self, mock_date):
            """
            Tests that get_age() returns the age after the birthday has already passed this year.

            :param mock_date: The mocked date class patched into speedy.core.base.utils.
            :type mock_date: unittest.mock.MagicMock
            """
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age(date_of_birth=date(1990, 1, 1)), second=34)

        @patch(target='speedy.core.base.utils.date')
        def test_birthday_is_today(self, mock_date):
            """
            Tests that get_age() returns the new age on the exact day of the birthday.

            :param mock_date: The mocked date class patched into speedy.core.base.utils.
            :type mock_date: unittest.mock.MagicMock
            """
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age(date_of_birth=date(1990, 6, 15)), second=34)

        @patch(target='speedy.core.base.utils.date')
        def test_birthday_not_yet_reached_this_year(self, mock_date):
            """
            Tests that get_age() returns the age before the birthday is reached this year.

            :param mock_date: The mocked date class patched into speedy.core.base.utils.
            :type mock_date: unittest.mock.MagicMock
            """
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age(date_of_birth=date(1990, 12, 31)), second=33)

        @patch(target='speedy.core.base.utils.date')
        def test_date_of_birth_on_leap_day(self, mock_date):
            """
            Tests that get_age() correctly computes the age of a person born on a leap day.

            :param mock_date: The mocked date class patched into speedy.core.base.utils.
            :type mock_date: unittest.mock.MagicMock
            """
            mock_date.today.return_value = date(2024, 3, 1)
            self.assertEqual(first=get_age(date_of_birth=date(2000, 2, 29)), second=24)


    class GetAgeOrDefaultOnlyEnglishTestCase(SiteTestCase):
        """
        Tests get_age_or_default(), in English.
        """

        @patch(target='speedy.core.base.utils.date')
        def test_valid_date_of_birth_returns_the_age(self, mock_date):
            """
            Tests that get_age_or_default() returns the computed age when a date of birth is given.

            :param mock_date: The mocked date class patched into speedy.core.base.utils.
            :type mock_date: unittest.mock.MagicMock
            """
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age_or_default(date_of_birth=date(1990, 1, 1)), second=34)

        def test_none_date_of_birth_returns_the_default_value(self):
            """
            Tests that get_age_or_default() returns the default value when the date of birth is None.
            """
            self.assertEqual(first=get_age_or_default(date_of_birth=None), second=-9 * (10 ** 15))

        def test_none_date_of_birth_returns_the_custom_default_value(self):
            """
            Tests that get_age_or_default() returns a custom default value when the date of birth is None and a default is given.
            """
            self.assertEqual(first=get_age_or_default(date_of_birth=None, default=-1), second=-1)


    class GetAgeRangesMatchOnlyEnglishTestCase(SiteTestCase):
        """
        Tests get_age_ranges_match(), in English.
        """

        @patch(target='speedy.core.base.utils.date')
        def test_get_age_ranges_match_with_different_min_and_max_age(self, mock_date):
            """
            Tests that get_age_ranges_match() returns the expected min/max date of birth range when min_age and max_age differ.

            :param mock_date: The mocked date class patched into speedy.core.base.utils.
            :type mock_date: unittest.mock.MagicMock
            """
            mock_date.today.return_value = date(2024, 6, 15)
            min_date, max_date = get_age_ranges_match(min_age=20, max_age=30)
            self.assertEqual(first=max_date, second=date(2004, 6, 15))
            self.assertEqual(first=min_date, second=date(1993, 6, 16))

        @patch(target='speedy.core.base.utils.date')
        def test_get_age_ranges_match_with_the_same_min_and_max_age(self, mock_date):
            """
            Tests that get_age_ranges_match() returns the expected min/max date of birth range when min_age equals max_age.

            :param mock_date: The mocked date class patched into speedy.core.base.utils.
            :type mock_date: unittest.mock.MagicMock
            """
            mock_date.today.return_value = date(2024, 6, 15)
            min_date, max_date = get_age_ranges_match(min_age=25, max_age=25)
            self.assertEqual(first=max_date, second=date(1999, 6, 15))
            self.assertEqual(first=min_date, second=date(1998, 6, 16))


    class IsAnimatedOnlyEnglishTestCase(SiteTestCase):
        """
        Tests is_animated(), in English.
        """

        def test_static_image_is_not_animated(self):
            """
            Tests that is_animated() returns False for a single-frame static image.
            """
            image = Image.new(mode='RGB', size=(2, 2), color=(255, 0, 0))
            self.assertEqual(first=is_animated(image=image), second=False)

        def test_animated_gif_is_animated(self):
            """
            Tests that is_animated() returns True for a multi-frame animated GIF image.
            """
            frames = [Image.new(mode='RGB', size=(2, 2), color=(i * 50, 0, 0)) for i in range(3)]
            buffer = io.BytesIO()
            frames[0].save(buffer, format='GIF', save_all=True, append_images=frames[1:])
            buffer.seek(0)
            image = Image.open(fp=buffer)
            self.assertEqual(first=is_animated(image=image), second=True)


    class IsTransparentOnlyEnglishTestCase(SiteTestCase):
        """
        Tests is_transparent(), in English.
        """

        def test_rgb_image_is_not_transparent(self):
            """
            Tests that is_transparent() returns False for an RGB image, which has no alpha channel.
            """
            image = Image.new(mode='RGB', size=(2, 2), color=(255, 0, 0))
            self.assertEqual(first=is_transparent(image=image), second=False)

        def test_fully_opaque_rgba_image_is_not_transparent(self):
            """
            Tests that is_transparent() returns False for a fully opaque RGBA image.
            """
            image = Image.new(mode='RGBA', size=(2, 2), color=(255, 0, 0, 255))
            self.assertEqual(first=is_transparent(image=image), second=False)

        def test_partially_transparent_rgba_image_is_transparent(self):
            """
            Tests that is_transparent() returns True for an RGBA image with at least one partially transparent pixel.
            """
            image = Image.new(mode='RGBA', size=(2, 2), color=(255, 0, 0, 255))
            image.putpixel(xy=(0, 0), value=(255, 0, 0, 0))
            self.assertEqual(first=is_transparent(image=image), second=True)

        def test_fully_opaque_la_image_is_not_transparent(self):
            """
            Tests that is_transparent() returns False for a fully opaque LA (grayscale with alpha) image.
            """
            image = Image.new(mode='LA', size=(2, 2), color=(100, 255))
            self.assertEqual(first=is_transparent(image=image), second=False)

        def test_partially_transparent_la_image_is_transparent(self):
            """
            Tests that is_transparent() returns True for an LA image with at least one partially transparent pixel.
            """
            image = Image.new(mode='LA', size=(2, 2), color=(100, 255))
            image.putpixel(xy=(0, 0), value=(100, 0))
            self.assertEqual(first=is_transparent(image=image), second=True)

        def test_palette_image_with_transparency_info_is_transparent(self):
            """
            Tests that is_transparent() returns True for a palette ('P' mode) image that defines transparency info.
            """
            image = Image.new(mode='P', size=(2, 2))
            image.info['transparency'] = 0
            self.assertEqual(first=is_transparent(image=image), second=True)

        def test_palette_image_without_transparency_info_is_not_transparent(self):
            """
            Tests that is_transparent() returns False for a palette ('P' mode) image that defines no transparency info.
            """
            image = Image.new(mode='P', size=(2, 2))
            self.assertEqual(first=is_transparent(image=image), second=False)


    class LooksLikeOneColorOnlyEnglishTestCase(SiteTestCase):
        """
        Tests looks_like_one_color(), in English.
        """

        def set_up(self):
            """
            Sets up a fake user object with a date_created attribute, used by looks_like_one_color().
            """
            super().set_up()
            self._user = SimpleNamespace(date_created=timezone_now())

        def test_single_color_image_looks_like_one_color(self):
            """
            Tests that looks_like_one_color() returns True for an image made of a single uniform color.
            """
            image = Image.new(mode='RGB', size=(10, 10), color=(100, 150, 200))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=True)

        def test_image_with_two_very_different_colors_does_not_look_like_one_color(self):
            """
            Tests that looks_like_one_color() returns False for an image containing two very different colors.
            """
            image = Image.new(mode='RGB', size=(10, 10), color=(0, 0, 0))
            for x in range(6):
                for y in range(10):
                    image.putpixel(xy=(x, y), value=(255, 255, 255))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=False)

        def test_image_with_slightly_different_shades_looks_like_one_color(self):
            """
            Tests that looks_like_one_color() returns True for an image whose pixels differ only by slightly different shades.
            """
            image = Image.new(mode='RGB', size=(10, 10), color=(100, 100, 100))
            image.putpixel(xy=(0, 0), value=(105, 100, 100))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=True)

        def test_rgba_image_is_converted_to_rgb_before_checking(self):
            """
            Tests that looks_like_one_color() converts an RGBA image to RGB before checking and still returns True for a uniform color.
            """
            image = Image.new(mode='RGBA', size=(10, 10), color=(100, 150, 200, 255))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=True)


    if (django_settings.LOGIN_ENABLED):
        class TimeSinceTestCaseMixin(TestCaseMixin):
            """
            Mixin providing a shared assertion that timesince() returns an empty string when the given date equals now.
            """

            def test_timesince(self):
                """
                Tests that timesince() returns an empty string when the given date equals now.
                """
                today = date.today()
                self.assertEqual(first=timesince(d=today, now=today), second="")


        @only_on_sites_with_login
        class TimeSinceAllMainLanguagesEnglishTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class TimeSinceAllMainLanguagesFrenchTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class TimeSinceAllMainLanguagesGermanTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class TimeSinceAllMainLanguagesSpanishTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class TimeSinceAllMainLanguagesPortugueseTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class TimeSinceAllMainLanguagesItalianTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class TimeSinceAllMainLanguagesDutchTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class TimeSinceAllMainLanguagesJapaneseTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class TimeSinceAllMainLanguagesRussianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class TimeSinceAllMainLanguagesChineseTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class TimeSinceAllMainLanguagesPolishTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class TimeSinceAllMainLanguagesPersianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class TimeSinceAllMainLanguagesHebrewTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class TimeSinceAllMainLanguagesKoreanTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class TimeSinceAllMainLanguagesArabicTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class TimeSinceAllMainLanguagesIndonesianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class TimeSinceAllMainLanguagesUkrainianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class TimeSinceAllMainLanguagesTurkishTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class TimeSinceAllMainLanguagesVietnameseTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class TimeSinceAllMainLanguagesCzechTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class TimeSinceAllMainLanguagesSwedishTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class TimeSinceAllMainLanguagesFinnishTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class TimeSinceAllMainLanguagesHungarianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class TimeSinceAllMainLanguagesThaiTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class TimeSinceAllMainLanguagesGreekTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class TimeSinceAllMainLanguagesMalayTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class TimeSinceAllMainLanguagesSerbianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class TimeSinceAllMainLanguagesRomanianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class TimeSinceAllMainLanguagesBengaliTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class TimeSinceAllMainLanguagesCatalanTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class TimeSinceAllMainLanguagesNorwegianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class TimeSinceAllMainLanguagesBulgarianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class TimeSinceAllMainLanguagesDanishTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class TimeSinceAllMainLanguagesSlovakTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class TimeSinceAllMainLanguagesHindiTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class TimeSinceAllMainLanguagesEstonianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class TimeSinceAllMainLanguagesCroatianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class TimeSinceAllMainLanguagesAzerbaijaniTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class TimeSinceAllMainLanguagesCantoneseTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class TimeSinceAllMainLanguagesLithuanianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class TimeSinceAllMainLanguagesSlovenianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class TimeSinceAllMainLanguagesBasqueTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class TimeSinceAllMainLanguagesArmenianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class TimeSinceAllMainLanguagesUzbekTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class TimeSinceAllMainLanguagesTamilTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class TimeSinceAllMainLanguagesLatvianTestCase(TimeSinceTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests that timesince() returns an empty string when the given date equals now, for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


