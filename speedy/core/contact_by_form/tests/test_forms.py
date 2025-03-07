from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from django.test import override_settings

        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.contact_by_form.test.mixins import SpeedyCoreFeedbackLanguageMixin

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.contact_by_form.forms import FeedbackForm
        from speedy.core.contact_by_form.models import Feedback


        class FeedbackFormTestCaseMixin(SpeedyCoreFeedbackLanguageMixin, TestCaseMixin):
            def assert_form_text_field(self, form):
                self.assertIs(expr1=form.fields['text'].required, expr2=True)

            def test_feedback_form_for_visitor_displays_name_and_email(self):
                defaults = {
                    'type': Feedback.TYPE_FEEDBACK,
                }
                form = FeedbackForm(defaults=defaults)
                self.assertListEqual(list1=list(form.fields.keys()), list2=self._feedback_form_all_the_required_fields_keys(user_is_logged_in=False))
                self.assertIs(expr1=form.fields['sender_name'].required, expr2=True)
                self.assertIs(expr1=form.fields['sender_email'].required, expr2=True)
                self.assert_form_text_field(form=form)

            def test_visitor_cannot_submit_form_without_all_the_required_fields(self):
                defaults = {
                    'type': Feedback.TYPE_FEEDBACK,
                }
                data = {}
                form = FeedbackForm(defaults=defaults, data=data)
                self.assertIs(expr1=form.is_valid(), expr2=False)
                self.assertDictEqual(d1=form.errors, d2=self._feedback_form_all_the_required_fields_are_required_errors_dict(user_is_logged_in=False))

            @only_on_sites_with_login
            def test_feedback_form_for_user_doesnt_require_name_and_email(self):
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
        class FeedbackFormEnglishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fr')
        class FeedbackFormFrenchTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='de')
        class FeedbackFormGermanTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='es')
        class FeedbackFormSpanishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='pt')
        class FeedbackFormPortugueseTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='it')
        class FeedbackFormItalianTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='nl')
        class FeedbackFormDutchTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackFormSwedishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackFormKoreanTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackFormFinnishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackFormHebrewTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


