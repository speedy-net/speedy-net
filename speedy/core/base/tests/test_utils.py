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


    class GetAgeOnlyEnglishTestCase(SiteTestCase):
        @patch(target='speedy.core.base.utils.date')
        def test_birthday_already_passed_this_year(self, mock_date):
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age(date_of_birth=date(1990, 1, 1)), second=34)

        @patch(target='speedy.core.base.utils.date')
        def test_birthday_is_today(self, mock_date):
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age(date_of_birth=date(1990, 6, 15)), second=34)

        @patch(target='speedy.core.base.utils.date')
        def test_birthday_not_yet_reached_this_year(self, mock_date):
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age(date_of_birth=date(1990, 12, 31)), second=33)

        @patch(target='speedy.core.base.utils.date')
        def test_date_of_birth_on_leap_day(self, mock_date):
            mock_date.today.return_value = date(2024, 3, 1)
            self.assertEqual(first=get_age(date_of_birth=date(2000, 2, 29)), second=24)


    class GetAgeOrDefaultOnlyEnglishTestCase(SiteTestCase):
        @patch(target='speedy.core.base.utils.date')
        def test_valid_date_of_birth_returns_the_age(self, mock_date):
            mock_date.today.return_value = date(2024, 6, 15)
            self.assertEqual(first=get_age_or_default(date_of_birth=date(1990, 1, 1)), second=34)

        def test_none_date_of_birth_returns_the_default_value(self):
            self.assertEqual(first=get_age_or_default(date_of_birth=None), second=-9 * (10 ** 15))

        def test_none_date_of_birth_returns_the_custom_default_value(self):
            self.assertEqual(first=get_age_or_default(date_of_birth=None, default=-1), second=-1)


    class GetAgeRangesMatchOnlyEnglishTestCase(SiteTestCase):
        @patch(target='speedy.core.base.utils.date')
        def test_get_age_ranges_match_with_different_min_and_max_age(self, mock_date):
            mock_date.today.return_value = date(2024, 6, 15)
            min_date, max_date = get_age_ranges_match(min_age=20, max_age=30)
            self.assertEqual(first=max_date, second=date(2004, 6, 15))
            self.assertEqual(first=min_date, second=date(1993, 6, 16))

        @patch(target='speedy.core.base.utils.date')
        def test_get_age_ranges_match_with_the_same_min_and_max_age(self, mock_date):
            mock_date.today.return_value = date(2024, 6, 15)
            min_date, max_date = get_age_ranges_match(min_age=25, max_age=25)
            self.assertEqual(first=max_date, second=date(1999, 6, 15))
            self.assertEqual(first=min_date, second=date(1998, 6, 16))


    class IsAnimatedOnlyEnglishTestCase(SiteTestCase):
        def test_static_image_is_not_animated(self):
            image = Image.new(mode='RGB', size=(2, 2), color=(255, 0, 0))
            self.assertEqual(first=is_animated(image=image), second=False)

        def test_animated_gif_is_animated(self):
            frames = [Image.new(mode='RGB', size=(2, 2), color=(i * 50, 0, 0)) for i in range(3)]
            buffer = io.BytesIO()
            frames[0].save(buffer, format='GIF', save_all=True, append_images=frames[1:])
            buffer.seek(0)
            image = Image.open(fp=buffer)
            self.assertEqual(first=is_animated(image=image), second=True)


    class IsTransparentOnlyEnglishTestCase(SiteTestCase):
        def test_rgb_image_is_not_transparent(self):
            image = Image.new(mode='RGB', size=(2, 2), color=(255, 0, 0))
            self.assertEqual(first=is_transparent(image=image), second=False)

        def test_fully_opaque_rgba_image_is_not_transparent(self):
            image = Image.new(mode='RGBA', size=(2, 2), color=(255, 0, 0, 255))
            self.assertEqual(first=is_transparent(image=image), second=False)

        def test_partially_transparent_rgba_image_is_transparent(self):
            image = Image.new(mode='RGBA', size=(2, 2), color=(255, 0, 0, 255))
            image.putpixel(xy=(0, 0), value=(255, 0, 0, 0))
            self.assertEqual(first=is_transparent(image=image), second=True)

        def test_fully_opaque_la_image_is_not_transparent(self):
            image = Image.new(mode='LA', size=(2, 2), color=(100, 255))
            self.assertEqual(first=is_transparent(image=image), second=False)

        def test_partially_transparent_la_image_is_transparent(self):
            image = Image.new(mode='LA', size=(2, 2), color=(100, 255))
            image.putpixel(xy=(0, 0), value=(100, 0))
            self.assertEqual(first=is_transparent(image=image), second=True)

        def test_palette_image_with_transparency_info_is_transparent(self):
            image = Image.new(mode='P', size=(2, 2))
            image.info['transparency'] = 0
            self.assertEqual(first=is_transparent(image=image), second=True)

        def test_palette_image_without_transparency_info_is_not_transparent(self):
            image = Image.new(mode='P', size=(2, 2))
            self.assertEqual(first=is_transparent(image=image), second=False)


    class LooksLikeOneColorOnlyEnglishTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self._user = SimpleNamespace(date_created=timezone_now())

        def test_single_color_image_looks_like_one_color(self):
            image = Image.new(mode='RGB', size=(10, 10), color=(100, 150, 200))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=True)

        def test_image_with_two_very_different_colors_does_not_look_like_one_color(self):
            image = Image.new(mode='RGB', size=(10, 10), color=(0, 0, 0))
            for x in range(6):
                for y in range(10):
                    image.putpixel(xy=(x, y), value=(255, 255, 255))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=False)

        def test_image_with_slightly_different_shades_looks_like_one_color(self):
            image = Image.new(mode='RGB', size=(10, 10), color=(100, 100, 100))
            image.putpixel(xy=(0, 0), value=(105, 100, 100))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=True)

        def test_rgba_image_is_converted_to_rgb_before_checking(self):
            image = Image.new(mode='RGBA', size=(10, 10), color=(100, 150, 200, 255))
            self.assertEqual(first=looks_like_one_color(image=image, _user=self._user), second=True)


    if (django_settings.LOGIN_ENABLED):
        class TimeSinceTestCaseMixin(TestCaseMixin):
            def test_timesince(self):
                today = date.today()
                self.assertEqual(first=timesince(d=today, now=today), second="")


        @only_on_sites_with_login
        class TimeSinceAllMainLanguagesEnglishTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class TimeSinceAllMainLanguagesFrenchTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class TimeSinceAllMainLanguagesGermanTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class TimeSinceAllMainLanguagesSpanishTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class TimeSinceAllMainLanguagesPortugueseTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class TimeSinceAllMainLanguagesItalianTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class TimeSinceAllMainLanguagesDutchTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class TimeSinceAllMainLanguagesHebrewTestCase(TimeSinceTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


