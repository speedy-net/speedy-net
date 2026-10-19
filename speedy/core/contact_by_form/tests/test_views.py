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
            """

            def set_up_class(self):
                """
                Not implemented in this mixin - must be overridden by subclasses to set the expected feedback type and report entity/file ids.

                :raises NotImplementedError: Always, since this method must be overridden by subclasses.
                """
                raise NotImplementedError("set_up_class must be defined in classes inherited from FeedbackViewBaseMixin.")

            def get_page_url(self):
                """
                Not implemented in this mixin - must be overridden by subclasses to return the page URL under test.

                :raises NotImplementedError: Always, since this method must be overridden by subclasses.
                """
                raise NotImplementedError("get_page_url must be defined in classes inherited from FeedbackViewBaseMixin.")

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
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ja')
        class FeedbackViewTypeFeedbackAllMainLanguagesJapaneseTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ru')
        class FeedbackViewTypeFeedbackAllMainLanguagesRussianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='zh')
        class FeedbackViewTypeFeedbackAllMainLanguagesChineseTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='pl')
        class FeedbackViewTypeFeedbackAllMainLanguagesPolishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fa')
        class FeedbackViewTypeFeedbackAllMainLanguagesPersianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeFeedbackAllMainLanguagesHebrewTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (plain feedback) for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackViewTypeFeedbackAllMainLanguagesKoreanTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ar')
        class FeedbackViewTypeFeedbackAllMainLanguagesArabicTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='id')
        class FeedbackViewTypeFeedbackAllMainLanguagesIndonesianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='uk')
        class FeedbackViewTypeFeedbackAllMainLanguagesUkrainianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='tr')
        class FeedbackViewTypeFeedbackAllMainLanguagesTurkishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='vi')
        class FeedbackViewTypeFeedbackAllMainLanguagesVietnameseTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='cs')
        class FeedbackViewTypeFeedbackAllMainLanguagesCzechTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackViewTypeFeedbackAllMainLanguagesSwedishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackViewTypeFeedbackAllMainLanguagesFinnishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hu')
        class FeedbackViewTypeFeedbackAllMainLanguagesHungarianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='th')
        class FeedbackViewTypeFeedbackAllMainLanguagesThaiTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='el')
        class FeedbackViewTypeFeedbackAllMainLanguagesGreekTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ms')
        class FeedbackViewTypeFeedbackAllMainLanguagesMalayTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sr')
        class FeedbackViewTypeFeedbackAllMainLanguagesSerbianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ro')
        class FeedbackViewTypeFeedbackAllMainLanguagesRomanianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='bn')
        class FeedbackViewTypeFeedbackAllMainLanguagesBengaliTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ca')
        class FeedbackViewTypeFeedbackAllMainLanguagesCatalanTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='no')
        class FeedbackViewTypeFeedbackAllMainLanguagesNorwegianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='bg')
        class FeedbackViewTypeFeedbackAllMainLanguagesBulgarianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='da')
        class FeedbackViewTypeFeedbackAllMainLanguagesDanishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sk')
        class FeedbackViewTypeFeedbackAllMainLanguagesSlovakTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hi')
        class FeedbackViewTypeFeedbackAllMainLanguagesHindiTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='et')
        class FeedbackViewTypeFeedbackAllMainLanguagesEstonianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hr')
        class FeedbackViewTypeFeedbackAllMainLanguagesCroatianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='az')
        class FeedbackViewTypeFeedbackAllMainLanguagesAzerbaijaniTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='zh-yue')
        class FeedbackViewTypeFeedbackAllMainLanguagesCantoneseTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='lt')
        class FeedbackViewTypeFeedbackAllMainLanguagesLithuanianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sl')
        class FeedbackViewTypeFeedbackAllMainLanguagesSlovenianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='eu')
        class FeedbackViewTypeFeedbackAllMainLanguagesBasqueTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='hy')
        class FeedbackViewTypeFeedbackAllMainLanguagesArmenianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='uz')
        class FeedbackViewTypeFeedbackAllMainLanguagesUzbekTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ta')
        class FeedbackViewTypeFeedbackAllMainLanguagesTamilTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='lv')
        class FeedbackViewTypeFeedbackAllMainLanguagesLatvianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (plain feedback) for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class FeedbackViewTypeReportEntityTestCaseMixin(FeedbackViewBaseMixin, TestCaseMixin):
            """
            Tests the feedback view for reporting another user (entity abuse report).
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
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class FeedbackViewTypeReportEntityAllMainLanguagesJapaneseTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class FeedbackViewTypeReportEntityAllMainLanguagesRussianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class FeedbackViewTypeReportEntityAllMainLanguagesChineseTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class FeedbackViewTypeReportEntityAllMainLanguagesPolishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class FeedbackViewTypeReportEntityAllMainLanguagesPersianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeReportEntityAllMainLanguagesHebrewTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting another user) for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackViewTypeReportEntityAllMainLanguagesKoreanTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class FeedbackViewTypeReportEntityAllMainLanguagesArabicTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class FeedbackViewTypeReportEntityAllMainLanguagesIndonesianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class FeedbackViewTypeReportEntityAllMainLanguagesUkrainianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class FeedbackViewTypeReportEntityAllMainLanguagesTurkishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class FeedbackViewTypeReportEntityAllMainLanguagesVietnameseTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class FeedbackViewTypeReportEntityAllMainLanguagesCzechTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackViewTypeReportEntityAllMainLanguagesSwedishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackViewTypeReportEntityAllMainLanguagesFinnishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class FeedbackViewTypeReportEntityAllMainLanguagesHungarianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class FeedbackViewTypeReportEntityAllMainLanguagesThaiTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class FeedbackViewTypeReportEntityAllMainLanguagesGreekTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class FeedbackViewTypeReportEntityAllMainLanguagesMalayTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class FeedbackViewTypeReportEntityAllMainLanguagesSerbianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class FeedbackViewTypeReportEntityAllMainLanguagesRomanianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class FeedbackViewTypeReportEntityAllMainLanguagesBengaliTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class FeedbackViewTypeReportEntityAllMainLanguagesCatalanTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class FeedbackViewTypeReportEntityAllMainLanguagesNorwegianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class FeedbackViewTypeReportEntityAllMainLanguagesBulgarianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class FeedbackViewTypeReportEntityAllMainLanguagesDanishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class FeedbackViewTypeReportEntityAllMainLanguagesSlovakTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class FeedbackViewTypeReportEntityAllMainLanguagesHindiTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class FeedbackViewTypeReportEntityAllMainLanguagesEstonianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class FeedbackViewTypeReportEntityAllMainLanguagesCroatianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class FeedbackViewTypeReportEntityAllMainLanguagesAzerbaijaniTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class FeedbackViewTypeReportEntityAllMainLanguagesCantoneseTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class FeedbackViewTypeReportEntityAllMainLanguagesLithuanianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class FeedbackViewTypeReportEntityAllMainLanguagesSlovenianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class FeedbackViewTypeReportEntityAllMainLanguagesBasqueTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class FeedbackViewTypeReportEntityAllMainLanguagesArmenianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class FeedbackViewTypeReportEntityAllMainLanguagesUzbekTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class FeedbackViewTypeReportEntityAllMainLanguagesTamilTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class FeedbackViewTypeReportEntityAllMainLanguagesLatvianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting another user) for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


        class FeedbackViewTypeReportFileTestCaseMixin(FeedbackViewBaseMixin, TestCaseMixin):
            """
            Tests the feedback view for reporting an uploaded file (file abuse report).
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
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'nl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ja')
        class FeedbackViewTypeReportFileAllMainLanguagesJapaneseTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Japanese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ja'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ja')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ru')
        class FeedbackViewTypeReportFileAllMainLanguagesRussianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Russian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ru'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ru')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh')
        class FeedbackViewTypeReportFileAllMainLanguagesChineseTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Chinese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pl')
        class FeedbackViewTypeReportFileAllMainLanguagesPolishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Polish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'pl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fa')
        class FeedbackViewTypeReportFileAllMainLanguagesPersianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Persian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fa'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fa')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeReportFileAllMainLanguagesHebrewTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            """
            Tests the feedback view (reporting a file) for all main languages (Hebrew).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'he'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackViewTypeReportFileAllMainLanguagesKoreanTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Korean).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ko'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ar')
        class FeedbackViewTypeReportFileAllMainLanguagesArabicTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Arabic).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ar'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ar')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='id')
        class FeedbackViewTypeReportFileAllMainLanguagesIndonesianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Indonesian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'id'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='id')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uk')
        class FeedbackViewTypeReportFileAllMainLanguagesUkrainianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Ukrainian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='tr')
        class FeedbackViewTypeReportFileAllMainLanguagesTurkishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Turkish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'tr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='tr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='vi')
        class FeedbackViewTypeReportFileAllMainLanguagesVietnameseTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Vietnamese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'vi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='vi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='cs')
        class FeedbackViewTypeReportFileAllMainLanguagesCzechTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Czech).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'cs'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='cs')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackViewTypeReportFileAllMainLanguagesSwedishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Swedish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackViewTypeReportFileAllMainLanguagesFinnishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Finnish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'fi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hu')
        class FeedbackViewTypeReportFileAllMainLanguagesHungarianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Hungarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='th')
        class FeedbackViewTypeReportFileAllMainLanguagesThaiTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Thai).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'th'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='th')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='el')
        class FeedbackViewTypeReportFileAllMainLanguagesGreekTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Greek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'el'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='el')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ms')
        class FeedbackViewTypeReportFileAllMainLanguagesMalayTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Malay).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ms'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ms')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sr')
        class FeedbackViewTypeReportFileAllMainLanguagesSerbianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Serbian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ro')
        class FeedbackViewTypeReportFileAllMainLanguagesRomanianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Romanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ro'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ro')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bn')
        class FeedbackViewTypeReportFileAllMainLanguagesBengaliTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Bengali).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bn'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bn')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ca')
        class FeedbackViewTypeReportFileAllMainLanguagesCatalanTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Catalan).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ca'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ca')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='no')
        class FeedbackViewTypeReportFileAllMainLanguagesNorwegianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Norwegian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'no'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='no')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='bg')
        class FeedbackViewTypeReportFileAllMainLanguagesBulgarianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Bulgarian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'bg'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='bg')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='da')
        class FeedbackViewTypeReportFileAllMainLanguagesDanishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Danish).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'da'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='da')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sk')
        class FeedbackViewTypeReportFileAllMainLanguagesSlovakTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Slovak).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sk'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sk')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hi')
        class FeedbackViewTypeReportFileAllMainLanguagesHindiTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Hindi).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hi'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='et')
        class FeedbackViewTypeReportFileAllMainLanguagesEstonianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Estonian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'et'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='et')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hr')
        class FeedbackViewTypeReportFileAllMainLanguagesCroatianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Croatian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hr'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='az')
        class FeedbackViewTypeReportFileAllMainLanguagesAzerbaijaniTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Azerbaijani).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'az'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='az')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='zh-yue')
        class FeedbackViewTypeReportFileAllMainLanguagesCantoneseTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Cantonese).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'zh-yue'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='zh-yue')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lt')
        class FeedbackViewTypeReportFileAllMainLanguagesLithuanianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Lithuanian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lt'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sl')
        class FeedbackViewTypeReportFileAllMainLanguagesSlovenianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Slovenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'sl'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='eu')
        class FeedbackViewTypeReportFileAllMainLanguagesBasqueTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Basque).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'eu'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='eu')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='hy')
        class FeedbackViewTypeReportFileAllMainLanguagesArmenianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Armenian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'hy'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='hy')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='uz')
        class FeedbackViewTypeReportFileAllMainLanguagesUzbekTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Uzbek).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'uz'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='uz')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ta')
        class FeedbackViewTypeReportFileAllMainLanguagesTamilTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Tamil).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'ta'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ta')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='lv')
        class FeedbackViewTypeReportFileAllMainLanguagesLatvianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):  # ~~~~ TODO: remove this test!!!
            """
            Tests the feedback view (reporting a file) for all main languages (Latvian).
            """

            def validate_all_values(self):
                """
                Runs the mixin's shared assertions and verifies the active language code is 'lv'.
                """
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='lv')


