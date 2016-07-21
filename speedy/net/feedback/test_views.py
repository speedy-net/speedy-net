from django.test import TestCase

from speedy.net.accounts.test_factories import UserFactory
from speedy.net.uploads.test_factories import FileFactory
from .models import Feedback


class FeedbackViewBaseMixin(object):
    def get_page_url(self):
        raise NotImplementedError()

    def check_feedback(self, feedback):
        raise NotImplementedError()

    def setUp(self):
        self.user = UserFactory()
        self.other_user = UserFactory()
        self.file = FileFactory()
        self.page_url = self.get_page_url()

    def test_visitor_can_see_feedback_form(self):
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'feedback/feedback_form.html')
        self.assertContains(r, 'id_sender_name')
        self.assertContains(r, 'id_sender_email')

    def test_visitor_can_submit_form(self):
        self.assertEqual(Feedback.objects.count(), 0)
        r = self.client.post(self.page_url, data={
            'sender_name': 'Mike',
            'sender_email': 'mike@example.com',
            'text': 'Hello',
        })
        self.assertRedirects(r, '/feedback/thank-you/')
        feedback = Feedback.objects.first()
        self.check_feedback(feedback)

    def test_user_can_see_feedback_form(self):
        self.client.login(username=self.user.slug, password='111')
        r = self.client.get(self.page_url)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'feedback/feedback_form.html')
        self.assertNotContains(r, 'id_sender_name')
        self.assertNotContains(r, 'id_sender_email')

    def test_user_can_submit_form(self):
        self.client.login(username=self.user.slug, password='111')
        self.assertEqual(Feedback.objects.count(), 0)
        r = self.client.post(self.page_url, data={
            'text': 'Hello',
        })
        self.assertRedirects(r, '/feedback/thank-you/')
        feedback = Feedback.objects.first()
        self.check_feedback(feedback)


class FeedbackViewTypeFeedbackTestCase(FeedbackViewBaseMixin, TestCase):
    def get_page_url(self):
        return '/feedback/'

    def check_feedback(self, feedback):
        self.assertEqual(feedback.type, Feedback.TYPE_FEEDBACK)


class FeedbackViewTypeReportEntityTestCase(FeedbackViewBaseMixin, TestCase):
    def get_page_url(self):
        return '/feedback/entity/{}/'.format(self.other_user.slug)

    def check_feedback(self, feedback):
        self.assertEqual(feedback.type, Feedback.TYPE_REPORT_ENTITY)
        self.assertEqual(feedback.report_entity_id, self.other_user.id)

    def test_404(self):
        r = self.client.get('/feedback/entity/abrakadabra/')
        self.assertEqual(r.status_code, 404)


class FeedbackViewTypeReportFileTestCase(FeedbackViewBaseMixin, TestCase):
    def get_page_url(self):
        return '/feedback/file/{}/'.format(self.file.id)

    def check_feedback(self, feedback):
        self.assertEqual(feedback.type, Feedback.TYPE_REPORT_FILE)
        self.assertEqual(feedback.report_file_id, self.file.id)

    def test_404(self):
        r = self.client.get('/feedback/file/abrakadabra/')
        self.assertEqual(r.status_code, 404)
