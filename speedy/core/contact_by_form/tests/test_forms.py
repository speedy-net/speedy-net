"""
Test cases for the feedback form of the contact by form app of Speedy Core, in all main languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.contact_by_form.test.mixins import SpeedyCoreFeedbackModelsMixin, SpeedyCoreFeedbackLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.contact_by_form.forms import FeedbackForm
        from speedy.core.contact_by_form.models import Feedback


        class FeedbackFormTestCaseMixin(SpeedyCoreFeedbackModelsMixin, SpeedyCoreFeedbackLanguageMixin, TestCaseMixin):
            """
            Tests the FeedbackForm, covering field visibility/requirements for visitors vs. logged-in users, validation errors, and saving an abuse report.
            """

            def assert_form_text_field(self, form):
                """
                Asserts the form's text field is marked as required.

                :param form: The form to check.
                :type form: speedy.core.contact_by_form.forms.FeedbackForm
                """
                self.assertIs(expr1=form.fields['text'].required, expr2=True)

            def test_feedback_form_for_visitor_displays_name_and_email(self):
                """
                Asserts that for a visitor (no sender), the form includes the sender_name, sender_email, text and no_bots fields, with sender_name/sender_email/text all required.
                """
                defaults = {
                    'type': Feedback.TYPE_FEEDBACK,
                }
                form = FeedbackForm(defaults=defaults)
                self.assertListEqual(list1=list(form.fields.keys()), list2=self._feedback_form_all_the_required_fields_keys(user_is_logged_in=False))
                self.assertIs(expr1=form.fields['sender_name'].required, expr2=True)
                self.assertIs(expr1=form.fields['sender_email'].required, expr2=True)
                self.assert_form_text_field(form=form)

            def test_visitor_cannot_submit_form_without_all_the_required_fields(self):
                """
                Asserts that submitting the form as a visitor with no data is invalid and produces "required" errors for all required visitor fields.
                """
                defaults = {
                    'type': Feedback.TYPE_FEEDBACK,
                }
                data = {}
                form = FeedbackForm(defaults=defaults, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._feedback_form_all_the_required_fields_are_required_errors_dict(user_is_logged_in=False))

            @only_on_sites_with_login
            def test_feedback_form_for_user_doesnt_require_name_and_email(self):
                """
                Asserts that for a logged-in user sender, the form only includes the text field (no sender_name/sender_email/no_bots), and the text field is required.
                """
                user = ActiveUserFactory()
                defaults = {
                    'type': Feedback.TYPE_FEEDBACK,
                    'sender': user,
                }
                form = FeedbackForm(defaults=defaults)
                self.assertListEqual(list1=list(form.fields.keys()), list2=self._feedback_form_all_the_required_fields_keys(user_is_logged_in=True))
                self.assert_form_text_field(form=form)

            @only_on_sites_with_login
            def test_user_cannot_submit_form_without_all_the_required_fields(self):
                """
                Asserts that submitting the form as a logged-in user with no data is invalid and produces a "required" error only for the text field.
                """
                user = ActiveUserFactory()
                defaults = {
                    'type': Feedback.TYPE_FEEDBACK,
                    'sender': user,
                }
                data = {}
                form = FeedbackForm(defaults=defaults, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._feedback_form_all_the_required_fields_are_required_errors_dict(user_is_logged_in=True))

            @only_on_sites_with_login
            def test_form_save_for_abuse_report_as_user(self):
                """
                Asserts that a valid abuse report (reporting another user, submitted by a logged-in user) is valid and saves a Feedback instance with the expected sender, empty sender name/email, report type, reported entity, no reported file, and text.
                """
                user = ActiveUserFactory()
                other_user = ActiveUserFactory()
                defaults = {
                    'type': Feedback.TYPE_REPORT_ENTITY,
                    'sender': user,
                    'report_entity': other_user,
                }
                data = {
                    'text': "I personally don't like this user.",
                }
                form = FeedbackForm(defaults=defaults, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=True)
                feedback = form.save()
                self.assertEqual(first=feedback.sender, second=user)
                self.assertEqual(first=feedback.sender_name, second='')
                self.assertEqual(first=feedback.sender_email, second='')
                self.assertEqual(first=feedback.type, second=Feedback.TYPE_REPORT_ENTITY)
                self.assertEqual(first=feedback.report_entity_id, second=other_user.pk)
                self.assertIsNone(obj=feedback.report_file)
                self.assertEqual(first=feedback.text, second=data['text'])


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        class FeedbackFormAllMainLanguagesEnglishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (English).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fr')
        class FeedbackFormAllMainLanguagesFrenchTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (French).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='de')
        class FeedbackFormAllMainLanguagesGermanTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (German).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='es')
        class FeedbackFormAllMainLanguagesSpanishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (Spanish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='pt')
        class FeedbackFormAllMainLanguagesPortugueseTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (Portuguese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='it')
        class FeedbackFormAllMainLanguagesItalianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (Italian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='nl')
        class FeedbackFormAllMainLanguagesDutchTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (Dutch).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ja')
        class FeedbackFormAllMainLanguagesJapaneseTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ru')
        class FeedbackFormAllMainLanguagesRussianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='zh')
        class FeedbackFormAllMainLanguagesChineseTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='pl')
        class FeedbackFormAllMainLanguagesPolishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fa')
        class FeedbackFormAllMainLanguagesPersianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackFormAllMainLanguagesHebrewTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackFormAllMainLanguagesKoreanTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ar')
        class FeedbackFormAllMainLanguagesArabicTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='id')
        class FeedbackFormAllMainLanguagesIndonesianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='uk')
        class FeedbackFormAllMainLanguagesUkrainianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='tr')
        class FeedbackFormAllMainLanguagesTurkishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='vi')
        class FeedbackFormAllMainLanguagesVietnameseTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='cs')
        class FeedbackFormAllMainLanguagesCzechTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackFormAllMainLanguagesSwedishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackFormAllMainLanguagesFinnishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hu')
        class FeedbackFormAllMainLanguagesHungarianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='th')
        class FeedbackFormAllMainLanguagesThaiTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='el')
        class FeedbackFormAllMainLanguagesGreekTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ms')
        class FeedbackFormAllMainLanguagesMalayTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sr')
        class FeedbackFormAllMainLanguagesSerbianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ro')
        class FeedbackFormAllMainLanguagesRomanianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='bn')
        class FeedbackFormAllMainLanguagesBengaliTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ca')
        class FeedbackFormAllMainLanguagesCatalanTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='no')
        class FeedbackFormAllMainLanguagesNorwegianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='bg')
        class FeedbackFormAllMainLanguagesBulgarianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='da')
        class FeedbackFormAllMainLanguagesDanishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sk')
        class FeedbackFormAllMainLanguagesSlovakTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hi')
        class FeedbackFormAllMainLanguagesHindiTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='et')
        class FeedbackFormAllMainLanguagesEstonianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hr')
        class FeedbackFormAllMainLanguagesCroatianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='az')
        class FeedbackFormAllMainLanguagesAzerbaijaniTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='zh-yue')
        class FeedbackFormAllMainLanguagesCantoneseTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='lt')
        class FeedbackFormAllMainLanguagesLithuanianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sl')
        class FeedbackFormAllMainLanguagesSlovenianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='eu')
        class FeedbackFormAllMainLanguagesBasqueTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hy')
        class FeedbackFormAllMainLanguagesArmenianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='uz')
        class FeedbackFormAllMainLanguagesUzbekTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ta')
        class FeedbackFormAllMainLanguagesTamilTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='lv')
        class FeedbackFormAllMainLanguagesLatvianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback form for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


