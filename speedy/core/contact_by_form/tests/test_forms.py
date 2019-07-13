from django.conf import settings as django_settings

if (django_settings.LOGIN_ENABLED):
    from speedy.core.base.test.models import SiteTestCase
    from speedy.core.base.test.decorators import only_on_sites_with_login
    from speedy.core.contact_by_form.test.mixins import SpeedyCoreFeedbackLanguageMixin
    from speedy.core.contact_by_form.forms import FeedbackForm
    from speedy.core.contact_by_form.models import Feedback
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


    class FeedbackFormTestCase(SpeedyCoreFeedbackLanguageMixin, SiteTestCase):
        def assert_form_text_field(self, form):
            self.assertTrue(expr=form.fields['text'].required)
            # print(form.fields['text']) # ~~~~ TODO: remove this line!
            # print(form.fields['text'].widget) # ~~~~ TODO: remove this line!
            # print(form.fields['text'].required) # ~~~~ TODO: remove this line!
            # print(form.fields['text'].disabled) # ~~~~ TODO: remove this line!
            # print(form.fields['text'].widget.is_required) # ~~~~ TODO: remove this line!
            # print(form.fields['text'].widget.is_hidden) # ~~~~ TODO: remove this line!

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


