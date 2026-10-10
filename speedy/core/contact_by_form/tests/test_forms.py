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

            Methods:
                assert_form_text_field(self, form): Asserts the form's text field is required.
                test_feedback_form_for_visitor_displays_name_and_email(self): Asserts a visitor's form includes and requires the sender name/email fields, plus the required text field.
                test_visitor_cannot_submit_form_without_all_the_required_fields(self): Asserts an empty visitor submission is invalid, with "required" errors for all required fields.
                test_feedback_form_for_user_doesnt_require_name_and_email(self): Asserts a logged-in user's form omits the sender name/email fields and only requires the text field.
                test_user_cannot_submit_form_without_all_the_required_fields(self): Asserts an empty logged-in user submission is invalid, with a "required" error only for the text field.
                test_form_save_for_abuse_report_as_user(self): Asserts a valid abuse report (reporting another user) saves a Feedback instance with the expected sender, type, reported entity, and text.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
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

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackFormAllMainLanguagesHebrewTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            """
            Tests the feedback form for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """
            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


