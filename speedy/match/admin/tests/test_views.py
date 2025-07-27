from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings
        from django.utils.html import escape

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_speedy_match

        from speedy.core.admin.tests.test_views import AdminViewBaseMixin


        class AdminMatchesListViewTestCaseMixin(AdminViewBaseMixin, TestCaseMixin):
            def get_page_url(self):
                return '/admin/matches/'

            def test_admin_has_access(self):
                r = super().test_admin_has_access()
                for user in [self.user_1, self.user_2, self.user_3]:
                    self.assertIn(member=escape(user.first_name), container=r.content.decode())
                    self.assertIn(member=escape(user.name), container=r.content.decode())
                    self.assertNotIn(member=escape(user.full_name), container=r.content.decode())
                    self.assertNotIn(member=escape(user.id), container=r.content.decode())
                self.assertEqual(first=r.content.decode().count(escape("['{}']".format(self.language_code))), second=0)


        @only_on_speedy_match
        class AdminMatchesListViewAllLanguagesEnglishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fr')
        class AdminMatchesListViewAllLanguagesFrenchTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='de')
        class AdminMatchesListViewAllLanguagesGermanTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='es')
        class AdminMatchesListViewAllLanguagesSpanishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='pt')
        class AdminMatchesListViewAllLanguagesPortugueseTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='it')
        class AdminMatchesListViewAllLanguagesItalianTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='nl')
        class AdminMatchesListViewAllLanguagesDutchTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='sv')
        class AdminMatchesListViewAllLanguagesSwedishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='ko')
        class AdminMatchesListViewAllLanguagesKoreanTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='fi')
        class AdminMatchesListViewAllLanguagesFinnishTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_speedy_match
        @override_settings(LANGUAGE_CODE='he')
        class AdminMatchesListViewAllLanguagesHebrewTestCase(AdminMatchesListViewTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


