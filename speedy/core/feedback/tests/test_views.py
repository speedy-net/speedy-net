from django.core import mail

from speedy.core.base.test.models import SiteTestCase
from speedy.core.base.test.decorators import only_on_sites_with_login
from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from speedy.core.uploads.tests.test_factories import FileFactory
from ..models import Feedback


class FeedbackViewBaseMixin(object):
    def setup_class(self):
        raise NotImplementedError()

    def get_page_url(self):
        raise NotImplementedError()

    def setup(self):
        super().setup()
        self.user = ActiveUserFactory()
        self.setup_class()
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
        self.assertTemplateUsed(response=r, template_name='feedback/feedback_form.html')
        self.assertContains(response=r, text='id_sender_name')
        self.assertContains(response=r, text='id_sender_email')

    def run_test_visitor_can_submit_form(self, data):
        self.assertEqual(first=Feedback.objects.count(), second=0)
        r = self.client.post(path=self.page_url, data=data)
        self.assertRedirects(response=r, expected_url='/contact/thank-you/')
        self.assertEqual(first=Feedback.objects.count(), second=1)
        feedback = Feedback.objects.first()
        self.check_feedback(feedback=feedback, expected_sender_id=None, expected_sender_name=data['sender_name'], expected_sender_email=data['sender_email'], expected_text=data['text'])

    def test_visitor_can_submit_form_1(self):
        data = {
            'sender_name': 'Yarden Harel',
            'sender_email': 'yarden@example.com',
            'text': 'Hello',
        }
        self.run_test_visitor_can_submit_form(data=data)

    def test_visitor_can_submit_form_2(self):
        data = {
            'sender_name': 'Mike',
            'sender_email': 'mike@example.com',
            'text': "I personally don't like this user.",
        }
        self.run_test_visitor_can_submit_form(data=data)

    @only_on_sites_with_login
    def test_user_can_see_feedback_form(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='feedback/feedback_form.html')
        self.assertNotContains(response=r, text='id_sender_name')
        self.assertNotContains(response=r, text='id_sender_email')

    @only_on_sites_with_login
    def test_user_can_submit_form(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Feedback.objects.count(), second=0)
        data = {
            'text': 'Hello',
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertRedirects(response=r, expected_url='/contact/thank-you/')
        self.assertEqual(first=Feedback.objects.count(), second=1)
        feedback = Feedback.objects.first()
        self.check_feedback(feedback=feedback, expected_sender_id=self.user.pk, expected_sender_name='', expected_sender_email='', expected_text=data['text'])
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='{}: {}'.format(self.site.name, str(feedback)))


class FeedbackViewTypeFeedbackTestCase(FeedbackViewBaseMixin, SiteTestCase):
    def setup_class(self):
        self.expected_feedback_type = Feedback.TYPE_FEEDBACK
        self.expected_report_entity_id = None
        self.expected_report_file_id = None

    def get_page_url(self):
        return '/contact/'


@only_on_sites_with_login
class FeedbackViewTypeReportEntityTestCase(FeedbackViewBaseMixin, SiteTestCase):
    def setup_class(self):
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
class FeedbackViewTypeReportFileTestCase(FeedbackViewBaseMixin, SiteTestCase):
    def setup_class(self):
        self.file = FileFactory()
        self.expected_feedback_type = Feedback.TYPE_REPORT_FILE
        self.expected_report_entity_id = None
        self.expected_report_file_id = self.file.pk

    def get_page_url(self):
        return '/contact/report/file/{}/'.format(self.file.pk)

    def test_404(self):
        r = self.client.get(path='/contact/report/file/abrakadabra/')
        self.assertEqual(first=r.status_code, second=404)


