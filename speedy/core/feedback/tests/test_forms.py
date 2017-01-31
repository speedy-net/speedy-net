from speedy.core.accounts.tests.test_factories import UserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from ..forms import FeedbackForm
from ..models import Feedback


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class FeedbackFormTestCase(TestCase):
    def test_feedback_form_for_visitor_displays_name_and_email(self):
        form = FeedbackForm(
            defaults={
                'type': Feedback.TYPE_FEEDBACK,
            }
        )
        self.assertListEqual(list1=list(form.fields.keys()), list2=['sender_name', 'sender_email', 'text'])
        self.assertTrue(expr=form.fields['sender_name'].required)
        self.assertTrue(expr=form.fields['sender_email'].required)

    def test_feedback_form_for_user_doesnt_require_name_and_email(self):
        user = UserFactory()
        form = FeedbackForm(
            defaults={
                'type': Feedback.TYPE_FEEDBACK,
                'sender': user,
            }
        )
        self.assertListEqual(list1=list(form.fields.keys()), list2=['text'])

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
        self.assertTrue(expr=form.is_valid())
        feedback = form.save()
        self.assertEqual(first=feedback.sender, second=user)
        self.assertEqual(first=feedback.sender_name, second='')
        self.assertEqual(first=feedback.sender_email, second='')
        self.assertEqual(first=feedback.type, second=Feedback.TYPE_REPORT_ENTITY)
        self.assertEqual(first=feedback.report_entity_id, second=other_user.id)
        self.assertEqual(first=feedback.report_file, second=None)
