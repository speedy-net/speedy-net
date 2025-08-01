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
        from speedy.core.contact_by_form.test.mixins import SpeedyCoreFeedbackLanguageMixin

        from speedy.core.accounts.test.user_factories import InactiveUserFactory, SpeedyNetInactiveUserFactory, ActiveUserFactory
        from speedy.core.uploads.test.factories import FileFactory

        from speedy.core.contact_by_form.models import Feedback


        class FeedbackViewBaseMixin(TestCaseMixin):
            def set_up_class(self):
                raise NotImplementedError()

            def get_page_url(self):
                raise NotImplementedError()

            def set_up(self):
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
                        raise NotImplementedError()
                self.set_up_class()
                self.page_url = self.get_page_url()

            def check_feedback(self, feedback, expected_sender_id, expected_sender_name, expected_sender_email, expected_text):
                self.assertEqual(first=feedback.type, second=self.expected_feedback_type)
                self.assertEqual(first=feedback.report_entity_id, second=self.expected_report_entity_id)
                self.assertEqual(first=feedback.report_file_id, second=self.expected_report_file_id)
                self.assertEqual(first=feedback.sender_id, second=expected_sender_id)
                self.assertEqual(first=feedback.sender_name, second=expected_sender_name)
                self.assertEqual(first=feedback.sender_email, second=expected_sender_email)
                self.assertEqual(first=feedback.text, second=expected_text)

            def test_visitor_can_see_feedback_form(self):
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
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertRedirects(response=r, expected_url='/contact/thank-you/', status_code=302, target_status_code=200)
                self.assertEqual(first=Feedback.objects.count(), second=1)
                feedback = Feedback.objects.first()
                self.check_feedback(feedback=feedback, expected_sender_id=None, expected_sender_name=data['sender_name'], expected_sender_email=data['sender_email'], expected_text=data['text'])

            def test_visitor_can_submit_form_1(self):
                data = {
                    'sender_name': 'Yarden Harel',
                    'sender_email': 'yarden@example.com',
                    'text': 'Hello',
                    'no_bots': '17',
                }
                self.run_test_visitor_can_submit_form(data=data)

            def test_visitor_can_submit_form_2(self):
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "I personally don't like this user.",
                    'no_bots': ' 17 ',
                }
                self.run_test_visitor_can_submit_form(data=data)

            def test_visitor_can_submit_form_3(self):
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "a" * 50000,
                    'no_bots': '17',
                }
                self.run_test_visitor_can_submit_form(data=data)

            def test_visitor_cannot_submit_form_without_all_the_required_fields(self):
                data = {}
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._feedback_form_all_the_required_fields_are_required_errors_dict(user_is_logged_in=False))
                self.assertEqual(first=Feedback.objects.count(), second=0)

            def test_visitor_cannot_submit_form_without_no_bots_17_1(self):
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
                data = {
                    'sender_name': 'Mike',
                    'sender_email': 'mike@example.com',
                    'text': "I personally don't like this user. {} 1".format(random.choice(["https://t.me/pump_upp", "https://datebest.net"])),
                    'no_bots': ' 17 ',
                }
                self.assertEqual(first=Feedback.objects.count(), second=0)
                r = self.client.post(path=self.page_url, data=data)
                self.assertEqual(first=r.status_code, second=200)
                self.assertDictEqual(d1=r.context['form'].errors, d2=self._please_contact_us_by_email_errors_dict())
                self.assertEqual(first=Feedback.objects.count(), second=0)

            def test_visitor_cannot_submit_form_with_text_too_long_1(self):
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


        class FeedbackViewTypeFeedbackTestCaseMixin(FeedbackViewBaseMixin, SpeedyCoreFeedbackLanguageMixin, TestCaseMixin):
            def set_up_class(self):
                self.expected_feedback_type = Feedback.TYPE_FEEDBACK
                self.expected_report_entity_id = None
                self.expected_report_file_id = None

            def get_page_url(self):
                return '/contact/'


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        class FeedbackViewTypeFeedbackAllLanguagesEnglishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fr')
        class FeedbackViewTypeFeedbackAllLanguagesFrenchTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='de')
        class FeedbackViewTypeFeedbackAllLanguagesGermanTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='es')
        class FeedbackViewTypeFeedbackAllLanguagesSpanishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='pt')
        class FeedbackViewTypeFeedbackAllLanguagesPortugueseTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='it')
        class FeedbackViewTypeFeedbackAllLanguagesItalianTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='nl')
        class FeedbackViewTypeFeedbackAllLanguagesDutchTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackViewTypeFeedbackAllLanguagesSwedishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackViewTypeFeedbackAllLanguagesKoreanTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackViewTypeFeedbackAllLanguagesFinnishTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login  # Contact by form is currently limited only to sites with login.
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeFeedbackAllLanguagesHebrewTestCase(FeedbackViewTypeFeedbackTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class FeedbackViewTypeReportEntityTestCaseMixin(FeedbackViewBaseMixin, SpeedyCoreFeedbackLanguageMixin, TestCaseMixin):
            def set_up_class(self):
                self.other_user = ActiveUserFactory()
                self.expected_feedback_type = Feedback.TYPE_REPORT_ENTITY
                self.expected_report_entity_id = self.other_user.pk
                self.expected_report_file_id = None

            def get_page_url(self):
                return '/contact/report/entity/{}/'.format(self.other_user.slug)

            def test_404(self):
                r = self.client.get(path='/contact/report/entity/abrakadabra/')
                self.assertEqual(first=r.status_code, second=404)


        @only_on_sites_with_login
        class FeedbackViewTypeReportEntityAllLanguagesEnglishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class FeedbackViewTypeReportEntityAllLanguagesFrenchTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class FeedbackViewTypeReportEntityAllLanguagesGermanTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class FeedbackViewTypeReportEntityAllLanguagesSpanishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class FeedbackViewTypeReportEntityAllLanguagesPortugueseTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class FeedbackViewTypeReportEntityAllLanguagesItalianTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class FeedbackViewTypeReportEntityAllLanguagesDutchTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackViewTypeReportEntityAllLanguagesSwedishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackViewTypeReportEntityAllLanguagesKoreanTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackViewTypeReportEntityAllLanguagesFinnishTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeReportEntityAllLanguagesHebrewTestCase(FeedbackViewTypeReportEntityTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


        class FeedbackViewTypeReportFileTestCaseMixin(FeedbackViewBaseMixin, SpeedyCoreFeedbackLanguageMixin, TestCaseMixin):
            def set_up_class(self):
                self.file = FileFactory()
                self.expected_feedback_type = Feedback.TYPE_REPORT_FILE
                self.expected_report_entity_id = None
                self.expected_report_file_id = self.file.pk

            def get_page_url(self):
                return '/contact/report/file/{}/'.format(self.file.pk)

            def test_404(self):
                r = self.client.get(path='/contact/report/file/abrakadabra/')
                self.assertEqual(first=r.status_code, second=404)


        @only_on_sites_with_login
        class FeedbackViewTypeReportFileAllLanguagesEnglishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='en')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fr')
        class FeedbackViewTypeReportFileAllLanguagesFrenchTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fr')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='de')
        class FeedbackViewTypeReportFileAllLanguagesGermanTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='de')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='es')
        class FeedbackViewTypeReportFileAllLanguagesSpanishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='es')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='pt')
        class FeedbackViewTypeReportFileAllLanguagesPortugueseTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='pt')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='it')
        class FeedbackViewTypeReportFileAllLanguagesItalianTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='it')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='nl')
        class FeedbackViewTypeReportFileAllLanguagesDutchTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='nl')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='sv')
        class FeedbackViewTypeReportFileAllLanguagesSwedishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='sv')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='ko')
        class FeedbackViewTypeReportFileAllLanguagesKoreanTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='ko')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='fi')
        class FeedbackViewTypeReportFileAllLanguagesFinnishTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='fi')


        @only_on_sites_with_login
        @override_settings(LANGUAGE_CODE='he')
        class FeedbackViewTypeReportFileAllLanguagesHebrewTestCase(FeedbackViewTypeReportFileTestCaseMixin, SiteTestCase):
            def validate_all_values(self):
                super().validate_all_values()
                self.assertEqual(first=self.language_code, second='he')


