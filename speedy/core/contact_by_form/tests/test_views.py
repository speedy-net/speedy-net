"""
Test cases for the feedback views of the contact by form app of Speedy Core, in all main languages.
"""
from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import random

        from django.test import override_settings
        from django.core import mail

        from speedy.core.base.test import tests_settings
        from speedy.core.base.test.mixins import TestCaseMixin
        from speedy.core.base.test.models import SiteTestCase
        from speedy.core.base.test.decorators import only_on_sites_with_login
        from speedy.core.contact_by_form.test.mixins import SpeedyCoreFeedbackModelsMixin, SpeedyCoreFeedbackLanguageMixin

        from speedy.core.accounts.test.user_factories import InactiveUserFactory, SpeedyNetInactiveUserFactory, ActiveUserFactory
        from speedy.core.uploads.test.factories import FileFactory

        from speedy.core.contact_by_form.models import Feedback
        from speedy.core.contact_by_form.forms import FeedbackForm


        class FeedbackViewBaseMixin(SpeedyCoreFeedbackModelsMixin, SpeedyCoreFeedbackLanguageMixin, TestCaseMixin):
            """
            Base mixin for testing the feedback view, covering form display, submission by visitors and logged-in users, validation errors, and that Feedback deletion via querysets is disabled.

            Methods:
                set_up_class(self): Not implemented in this mixin - must be overridden by subclasses to set expected feedback type/report ids.
                get_page_url(self): Not implemented in this mixin - must be overridden by subclasses to return the page URL under test.
                set_up(self): Creates a random active/inactive user (when login is enabled), calls set_up_class(), and sets the page URL.
                check_feedback(self, feedback, expected_sender_id, expected_sender_name, expected_sender_email, expected_text): Asserts the given Feedback instance matches the expected type, report ids, sender, and text.
                test_visitor_can_see_feedback_form(self): Asserts a visitor sees the feedback form with the expected fields, ids, labels, and textarea.
                run_test_visitor_can_submit_form(self, data): Submits the form as a visitor with the given data and asserts a Feedback instance is created and redirects to the thank-you page.
                test_visitor_can_submit_form_1(self): Asserts a visitor can submit a short feedback message.
                test_visitor_can_submit_form_2(self): Asserts a visitor can submit feedback with a leading/trailing-space no_bots value.
                test_visitor_can_submit_form_3(self): Asserts a visitor can submit feedback with the maximum allowed text length (50000 characters).
                test_visitor_cannot_submit_form_without_all_the_required_fields(self): Asserts an empty visitor submission is invalid, with "required" errors for all required fields.
                test_visitor_cannot_submit_form_without_no_bots_17_1(self): Asserts an incorrect no_bots value ("16") produces a "not 17" error and doesn't create a Feedback instance.
                test_visitor_cannot_submit_form_without_no_bots_17_2(self): Asserts a blank no_bots value produces a "required" error and doesn't create a Feedback instance.
                test_visitor_cannot_submit_form_with_not_allowed_strings(self): Asserts text containing a not-allowed string produces a "please contact us by email" error and doesn't create a Feedback instance.
                test_visitor_cannot_submit_form_with_text_too_long_1(self): Asserts text one character over the maximum length produces a max-length error and doesn't create a Feedback instance.
                test_visitor_cannot_submit_form_with_text_too_long_2(self): Asserts a much longer text produces a max-length error and doesn't create a Feedback instance.
                test_user_can_see_feedback_form(self): Asserts a logged-in user sees the feedback form with only the text field (no sender name/email).
                test_user_can_submit_form(self): Asserts a logged-in user can submit feedback, which creates a Feedback instance linked to the user and sends a notification email.
                test_user_cannot_submit_form_without_all_the_required_fields(self): Asserts an empty logged-in user submission is invalid, with a "required" error only for the text field, and no email is sent.
                test_cannot_delete_feedbacks_with_queryset_delete(self): Asserts that deleting Feedback objects via queryset delete() (in various forms) always raises NotImplementedError.
            """

            def set_up_class(self):
                """
                Not implemented in this mixin - must be overridden by subclasses to set the expected feedback type and report entity/file ids.

                :raises NotImplementedError: Always, since this method must be overridden by subclasses.
                """
                raise NotImplementedError("This method is not implemented in this mixin.")

            def get_page_url(self):
                """
                Not implemented in this mixin - must be overridden by subclasses to return the page URL under test.

                :raises NotImplementedError: Always, since this method must be overridden by subclasses.
                """
                raise NotImplementedError("This method is not implemented in this mixin.")

            def set_up(self):
                """
                Creates a random active, inactive, or Speedy-Net-only-inactive user (when login is enabled), calls set_up_class() to set expected feedback values, and sets the page URL.
                """
                super().set_up()
                if (django_settings.LOGIN_ENABLED):
                    # Test that both active and inactive users can submit feedback.
                    self.random_choice = random.choice([1, 2, 3])
                    if (self.random_choice == 1):
                        self.user = ActiveUserFactory()
                    elif (self.random_choice == 2):
                        self.user = InactiveUserFactory()
                    elif (self.random_choice == 3):
                        self.user = SpeedyNetInactiveUserFactory()
                    else:
                        raise NotImplementedError("Invalid random choice.")
                self.set_up_class()
                self.page_url = self.get_page_url()

            def check_feedback(self, feedback, expected_sender_id, expected_sender_name, expected_sender_email, expected_text):
                """
                Asserts the given Feedback instance matches the expected feedback type, report entity/file ids, sender, and text.

                :param feedback: The Feedback instance to check.
                :type feedback: speedy.core.contact_by_form.models.Feedback
                :param expected_sender_id: The expected sender's primary key, or None.
                :type expected_sender_id: int or None
                :param expected_sender_name: The expected sender name.
                :type expected_sender_name: str
                :param expected_sender_email: The expected sender email.
                :type expected_sender_email: str
                :param expected_text: The expected feedback text.
                :type expected_text: str
                """
                self.assertEqual(first=feedback.type, second=self.expected_feedback_type)
                self.assertEqual(first=feedback.report_entity_id, second=self.expected_report_entity_id)
                self.assertEqual(first=feedback.report_file_id, second=self.expected_report_file_id)
                self.assertEqual(first=feedback.sender_id, second=expected_sender_id)
                self.assertEqual(first=feedback.sender_name, second=expected_sender_name)
                self.assertEqual(first=feedback.sender_email, second=expected_sender_email)
                self.assertEqual(first=feedback.text, second=expected_text)

            def test_visitor_can_see_feedback_form(self):
                """
                Asserts a visitor sees the feedback form with the sender_name, sender_email and text fields, their ids, labels, and a textarea.
                """
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='contact_by_form/feedback_form.html')
                self.assertContains(response=r, text=' name="sender_name"', count=1)
                self.assertContains(response=r, text=' name="sender_email"', count=1)
                self.assertContains(response=r, text=' name="text"', count=1)
                self.assertContains(response=r, text=' id="id_sender_name"', count=1)
                self.assertContains(response=r, text=' id="id_sender_email"', count=1)
                self.assertContains(response=r, text=' id="id_text"', count=1)
                self.assertContains(response=r, text='<label for="id_sender_name"', count=1)
                self.assertContains(response=r, text='<label for="id_sender_email"', count=1)
                self.assertContains(response=r, text='<label for="id_text"', count=1)
                self.assertContains(response=r, text='<textarea ', count=1)

            def run_test_visitor_can_submit_form(self, data):
                """
                Submits the feedback form as a visitor with the given data and asserts a Feedback instance is created, matching the submitted data, and the response redirects to the thank-you page.

                :param data: The form data to submit.
                :type data: dict
                """
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url='/contact/thank-you/', status_code=302, target_status_code=200)
                self.assertEqual(first=Feedback.objects.count(), second=1)
                feedback = Feedback.objects.first()
                self.check_feedback(feedback=feedback, expected_sender_id=None, expected_sender_name=data['sender_name'], expected_sender_email=data['sender_email'], expected_text=data['text'])

            def test_visitor_can_submit_form_1(self):
                """
                Asserts a visitor can submit a short feedback message with a valid no_bots value.
                """
                data = {
                    'sender_name': 'Yarden Harel',
                    'sender_email': 'yarden@example.com',
                    'text': 'Hello',
                    'no_bots': '17',
                }
                self.run_test_visitor_can_submit_form(data=data)

            def test_visitor_can_submit_form_2(self):
                """
                Asserts a visitor can submit feedback when the no_bots value has leading/trailing spaces around "17".
                """
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "I personally don't like this user.",
                    'no_bots': ' 17 ',
                }
                self.run_test_visitor_can_submit_form(data=data)

            def test_visitor_can_submit_form_3(self):
                """
                Asserts a visitor can submit feedback with text at the maximum allowed length (50000 characters).
                """
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "a" * 50000,
                    'no_bots': '17',
                }
                self.run_test_visitor_can_submit_form(data=data)

            def test_visitor_cannot_submit_form_without_all_the_required_fields(self):
                """
                Asserts that submitting the form as a visitor with no data is invalid, produces "required" errors for all required visitor fields, and doesn't create a Feedback instance.
                """
                data = {}
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._feedback_form_all_the_required_fields_are_required_errors_dict(user_is_logged_in=False))
                self.assertEqual(first=Feedback.objects.count(), second=0)

            def test_visitor_cannot_submit_form_without_no_bots_17_1(self):
                """
                Asserts that submitting an incorrect no_bots value ("16") produces a "not 17" error and doesn't create a Feedback instance.
                """
                data = {
                    'sender_name': 'Yarden Harel',
                    'sender_email': 'yarden@example.com',
                    'text': 'Hello',
                    'no_bots': '16',
                }
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._feedback_form_no_bots_is_not_17_errors_dict())
                self.assertEqual(first=Feedback.objects.count(), second=0)

            def test_visitor_cannot_submit_form_without_no_bots_17_2(self):
                """
                Asserts that submitting a blank (whitespace-only) no_bots value produces a "required" error and doesn't create a Feedback instance.
                """
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "I personally don't like this user.",
                    'no_bots': ' ',
                }
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._feedback_form_no_bots_is_required_errors_dict())
                self.assertEqual(first=Feedback.objects.count(), second=0)

            def test_visitor_cannot_submit_form_with_not_allowed_strings(self):
                """
                Asserts that text containing a not-allowed (spam-related) string produces a "please contact us by email" error and doesn't create a Feedback instance.
                """
                self.assertListEqual(list1=self._not_allowed_strings, list2=FeedbackForm._not_allowed_strings)
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "I personally don't like this user. {} 1".format(random.choice(self._not_allowed_strings)),
                    'no_bots': ' 17 ',
                }
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_contact_us_by_email_errors_dict())
                self.assertEqual(first=Feedback.objects.count(), second=0)

            def test_visitor_cannot_submit_form_with_text_too_long_1(self):
                """
                Asserts that text one character over the maximum length (50001 characters) produces a max-length error and doesn't create a Feedback instance.
                """
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "a" * 50001,
                    'no_bots': '17',
                }
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(value_length=50001))
                self.assertEqual(first=Feedback.objects.count(), second=0)

            def test_visitor_cannot_submit_form_with_text_too_long_2(self):
                """
                Asserts that a much longer text (1,000,000 characters) produces a max-length error and doesn't create a Feedback instance.
                """
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "b" * 1000000,
                    'no_bots': '17',
                }
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._ensure_this_value_has_at_most_max_length_characters_errors_dict_by_value_length(value_length=1000000))
                self.assertEqual(first=Feedback.objects.count(), second=0)

            @only_on_sites_with_login
            def test_user_can_see_feedback_form(self):
                """
                Asserts a logged-in user sees the feedback form with only the text field (no sender_name/sender_email fields).
                """
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                r = self.client.get(path=self.page_url)
                self.assertEqual(first=r.status_code, second=200)
                self.assertTemplateUsed(response=r, template_name='contact_by_form/feedback_form.html')
                self.assertNotContains(response=r, text=' name="sender_name"')
                self.assertNotContains(response=r, text=' name="sender_email"')
                self.assertContains(response=r, text=' name="text"', count=1)
                self.assertNotContains(response=r, text=' id="id_sender_name"')
                self.assertNotContains(response=r, text=' id="id_sender_email"')
                self.assertContains(response=r, text=' id="id_text"', count=1)
                self.assertNotContains(response=r, text='<label for="id_sender_name"')
                self.assertNotContains(response=r, text='<label for="id_sender_email"')
                self.assertContains(response=r, text='<label for="id_text"', count=1)
                self.assertContains(response=r, text='<textarea ', count=1)

            @only_on_sites_with_login
            def test_user_can_submit_form(self):
                """
                Asserts a logged-in user can submit feedback (text only), which creates a Feedback instance linked to the user and sends a single notification email with the expected subject.
                """
                self.assertEqual(first=len(mail.outbox), second=0)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Feedback.objects.count(), second=0)
                data = {
                    'text': 'Hello',
                }
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url='/contact/thank-you/', status_code=302, target_status_code=200)
                self.assertEqual(first=Feedback.objects.count(), second=1)
                feedback = Feedback.objects.first()
                self.check_feedback(feedback=feedback, expected_sender_id=self.user.pk, expected_sender_name='', expected_sender_email='', expected_text=data['text'])
                self.assertEqual(first=len(mail.outbox), second=1)
                self.assertEqual(first=mail.outbox[0].subject, second='{}: {}'.format(self.site_name, str(feedback)))

            @only_on_sites_with_login
            def test_user_cannot_submit_form_without_all_the_required_fields(self):
                """
                Asserts that submitting an empty form as a logged-in user is invalid, produces a "required" error only for the text field, doesn't create a Feedback instance, and doesn't send any email.
                """
                self.assertEqual(first=len(mail.outbox), second=0)
                self.client.login(username=self.user.slug, password=tests_settings.USER_PASSWORD)
                self.assertEqual(first=Feedback.objects.count(), second=0)
                data = {}
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._feedback_form_all_the_required_fields_are_required_errors_dict(user_is_logged_in=True))
                self.assertEqual(first=Feedback.objects.count(), second=0)
                self.assertEqual(first=len(mail.outbox), second=0)

            def test_cannot_delete_feedbacks_with_queryset_delete(self):
                """
                Asserts that deleting Feedback objects via queryset delete() - on the manager, all(), a filter(), or a filter combined with exclude() - always raises NotImplementedError.
                """
                with self.assertRaises(NotImplementedError) as cm:
                    Feedback.objects.delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    Feedback.objects.all().delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    Feedback.objects.filter(pk=1).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")
                with self.assertRaises(NotImplementedError) as cm:
                    Feedback.objects.all().exclude(pk=2).delete()
                self.assertEqual(first=str(cm.exception), second="delete is not implemented.")


        class FeedbackViewTypeFeedbackTestCaseMixin(FeedbackViewBaseMixin, TestCaseMixin):
            """
            Tests the feedback view for a plain feedback submission (not an abuse report).

            Methods:
                set_up_class(self): Sets the expected feedback type (TYPE_FEEDBACK) and no report entity/file.
                get_page_url(self): Returns the feedback page URL.
            """

            def set_up_class(self):
                """
                Sets the expected feedback type to TYPE_FEEDBACK, with no reported entity or file.
                """
                self.expected_feedback_type = Feedback.TYPE_FEEDBACK
                self.expected_report_entity_id = None
                self.expected_report_file_id = None

            def get_page_url(self):
                """
                Returns the feedback page URL.

                :return: The page URL.
                :rtype: str
                """
                return '/contact/'


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        class FeedbackViewTypeFeedbackAllMainLanguagesEnglishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (English).

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
        class FeedbackViewTypeFeedbackAllMainLanguagesFrenchTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (French).

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
        class FeedbackViewTypeFeedbackAllMainLanguagesGermanTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (German).

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
        class FeedbackViewTypeFeedbackAllMainLanguagesSpanishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (Spanish).

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
        class FeedbackViewTypeFeedbackAllMainLanguagesPortugueseTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (Portuguese).

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
        class FeedbackViewTypeFeedbackAllMainLanguagesItalianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (Italian).

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
        class FeedbackViewTypeFeedbackAllMainLanguagesDutchTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (Dutch).

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
        class FeedbackViewTypeFeedbackAllMainLanguagesHebrewTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class FeedbackViewTypeReportEntityTestCaseMixin(FeedbackViewBaseMixin, TestCaseMixin):
            """
            Tests the feedback view for reporting another user (entity abuse report).

            Methods:
                set_up_class(self): Creates another user to report and sets the expected feedback type (TYPE_REPORT_ENTITY) and reported entity id.
                get_page_url(self): Returns the report-entity page URL for the other user.
                test_404(self): Asserts requesting the report-entity page for a nonexistent slug returns a 404.
            """

            def set_up_class(self):
                """
                Creates another active user to be reported, and sets the expected feedback type to TYPE_REPORT_ENTITY with that user as the reported entity (and no reported file).
                """
                self.other_user = ActiveUserFactory()
                self.expected_feedback_type = Feedback.TYPE_REPORT_ENTITY
                self.expected_report_entity_id = self.other_user.pk
                self.expected_report_file_id = None

            def get_page_url(self):
                """
                Returns the report-entity page URL for the other user.

                :return: The page URL.
                :rtype: str
                """
                return '/contact/report/entity/{}/'.format(self.other_user.slug)

            def test_404(self):
                """
                Asserts requesting the report-entity page with a nonexistent slug returns a 404 response.
                """
                r = self.client.get(path='/contact/report/entity/abrakadabra/')
                self.assertEqual(first=r.status_code, second=404)


        @only_on_sites_with_login
        class FeedbackViewTypeReportEntityAllMainLanguagesEnglishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class FeedbackViewTypeReportEntityAllMainLanguagesFrenchTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class FeedbackViewTypeReportEntityAllMainLanguagesGermanTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class FeedbackViewTypeReportEntityAllMainLanguagesSpanishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class FeedbackViewTypeReportEntityAllMainLanguagesPortugueseTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class FeedbackViewTypeReportEntityAllMainLanguagesItalianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class FeedbackViewTypeReportEntityAllMainLanguagesDutchTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeReportEntityAllMainLanguagesHebrewTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class FeedbackViewTypeReportFileTestCaseMixin(FeedbackViewBaseMixin, TestCaseMixin):
            """
            Tests the feedback view for reporting an uploaded file (file abuse report).

            Methods:
                set_up_class(self): Creates a file to report and sets the expected feedback type (TYPE_REPORT_FILE) and reported file id.
                get_page_url(self): Returns the report-file page URL for the file.
                test_404(self): Asserts requesting the report-file page for a nonexistent file id returns a 404.
            """

            def set_up_class(self):
                """
                Creates a file to be reported, and sets the expected feedback type to TYPE_REPORT_FILE with that file as the reported file (and no reported entity).
                """
                self.file = FileFactory()
                self.expected_feedback_type = Feedback.TYPE_REPORT_FILE
                self.expected_report_entity_id = None
                self.expected_report_file_id = self.file.pk

            def get_page_url(self):
                """
                Returns the report-file page URL for the file.

                :return: The page URL.
                :rtype: str
                """
                return '/contact/report/file/{}/'.format(self.file.pk)

            def test_404(self):
                """
                Asserts requesting the report-file page with a nonexistent file id returns a 404 response.
                """
                r = self.client.get(path='/contact/report/file/abrakadabra/')
                self.assertEqual(first=r.status_code, second=404)


        @only_on_sites_with_login
        class FeedbackViewTypeReportFileAllMainLanguagesEnglishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (English).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'en'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class FeedbackViewTypeReportFileAllMainLanguagesFrenchTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (French).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class FeedbackViewTypeReportFileAllMainLanguagesGermanTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (German).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'de'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class FeedbackViewTypeReportFileAllMainLanguagesSpanishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (Spanish).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'es'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class FeedbackViewTypeReportFileAllMainLanguagesPortugueseTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (Portuguese).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class FeedbackViewTypeReportFileAllMainLanguagesItalianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (Italian).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'it'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class FeedbackViewTypeReportFileAllMainLanguagesDutchTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (Dutch).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeReportFileAllMainLanguagesHebrewTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (Hebrew).

            Methods:
                validate_all_values(self): Runs the mixin's shared assertions and verifies the active language code matches this test case's language.
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


