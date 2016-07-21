from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from .models import Feedback
from .forms import FeedbackForm


class FeedbackFormTestCase(TestCase):
    def test_feedback_form_for_visitor_displays_name_and_email(self):
        form = FeedbackForm(
            defaults={
                'type': Feedback.TYPE_FEEDBACK,
            }
        )
        self.assertListEqual(list(form.fields.keys()), ['sender_name', 'sender_email', 'text'])
        self.assertTrue(form.fields['sender_name'].required)
        self.assertTrue(form.fields['sender_email'].required)

    def test_feedback_form_for_user_doesnt_require_name_and_email(self):
        user = UserFactory()
        form = FeedbackForm(
            defaults={
                'type': Feedback.TYPE_FEEDBACK,
                'sender': user,
            }
        )
        self.assertListEqual(list(form.fields.keys()), ['text'])

    def test_form_save_for_abuse_report_as_user(self):
        user = UserFactory()
        other_user = UserFactory()
        form = FeedbackForm(
            data={
                'text': "I personally don't like this user.",
            },
            defaults={
                'type': Feedback.TYPE_REPORT_ENTITY,
                'sender': user,
                'report_entity': other_user,
            }
        )
        self.assertTrue(form.is_valid())
        feedback = form.save()
        self.assertEqual(feedback.sender, user)
        self.assertEqual(feedback.sender_name, '')
        self.assertEqual(feedback.sender_email, '')
        self.assertEqual(feedback.type, Feedback.TYPE_REPORT_ENTITY)
        self.assertEqual(feedback.report_entity_id, other_user.id)
        self.assertEqual(feedback.report_file, None)
