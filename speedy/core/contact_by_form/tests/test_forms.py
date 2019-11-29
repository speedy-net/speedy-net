from django.conf import settings as django_settings
from django.test import override_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.contact_by_form.test.mixins import SpeedyCoreFeedbackLanguageMixin
    from speedy.core.contact_by_form.forms import FeedbackForm
    from speedy.core.contact_by_form.models import Feedback
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    class FeedbackFormTestCaseMixin(SpeedyCoreFeedbackLanguageMixin):
        def assert_form_text_field(self, form):
            self.assertTrue(expr=form.fields['text'].required)

        def test_feedback_form_for_visitor_displays_name_and_email(self):
            defaults = {
                'type': Feedback.TYPE_FEEDBACK,
            }
            form = FeedbackForm(defaults=defaults)
            self.assertListEqual(list1=list(form.fields.keys()), list2=self._feedback_form_all_the_required_fields_keys(user_is_logged_in=False))
            self.assertTrue(expr=form.fields['sender_name'].required)
            self.assertTrue(expr=form.fields['sender_email'].required)
            self.assert_form_text_field(form=form)

        def test_visitor_cannot_submit_form_without_all_the_required_fields(self):
            defaults = {
                'type': Feedback.TYPE_FEEDBACK,
            }
            data = {}
            form = FeedbackForm(defaults=defaults, data=data)
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._feedback_form_all_the_required_fields_are_required_errors_dict(user_is_logged_in=False))

        def test_visitor_cannot_submit_form_with_not_allowed_string_1(self):
            defaults = {
                'type': Feedback.TYPE_FEEDBACK,
            }
            data = {
                'sender_name': "A",
                'sender_email': "test@example.com",
                'text': """
                    Best regards
                    Mike
                    monkeydigital.co@gmail.com
                """,
                'no_bots': '17',
            }
            form = FeedbackForm(defaults=defaults, data=data)
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._please_contact_us_by_email_errors_dict())

        def test_visitor_cannot_submit_form_with_not_allowed_string_2(self):
            defaults = {
                'type': Feedback.TYPE_FEEDBACK,
            }
            data = {
                'sender_name': "A",
                'sender_email': "test@example.com",
                'text': """
                    We will increase your Website TF in 30 days (Majestic SEO – Trust Flow) or we will refund you every cent. 100% Money back guarantee
                    
                    We offer Guaranteed TF 20 and TF 30
                    
                    Majestic Trust Flow is the most important SEO metric since the dissapearance of Google Page Rank.
                    Ensure confidence and trust in your website having a high Trust Flow score
                    
                    More details about our service can be found here:
                    https://monkeydigital.co/product/trust-flow-seo-package/
                    
                    Best regards
                    Mike
                """,
                'no_bots': '17',
            }
            form = FeedbackForm(defaults=defaults, data=data)
            self.assertFalse(expr=form.is_valid())
            self.assertDictEqual(d1=form.errors, d2=self._please_contact_us_by_email_errors_dict())

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
            self.assertFalse(expr=form.is_valid())
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
            self.assertTrue(expr=form.is_valid())
            feedback = form.save()
            self.assertEqual(first=feedback.sender, second=user)
            self.assertEqual(first=feedback.sender_name, second='')
            self.assertEqual(first=feedback.sender_email, second='')
            self.assertEqual(first=feedback.type, second=Feedback.TYPE_REPORT_ENTITY)
            self.assertEqual(first=feedback.report_entity_id, second=other_user.pk)
            self.assertIsNone(obj=feedback.report_file)
            self.assertEqual(first=feedback.text, second=data['text'])


    @only_on_sites_with_login # Contact by form is currently limited only to sites with login.
    class FeedbackFormEnglishTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='en')


    @only_on_sites_with_login # Contact by form is currently limited only to sites with login.
    @override_settings(LANGUAGE_CODE='he')
    class FeedbackFormHebrewTestCase(FeedbackFormTestCaseMixin, SiteTestCase):
        def validate_all_values(self):
            super().validate_all_values()
            self.assertEqual(first=self.language_code, second='he')


