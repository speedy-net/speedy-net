from django.core import mail

from speedy.core.base.test import TestCase, only_on_sites_with_login
from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from speedy.core.uploads.tests.test_factories import FileFactory
from ..models import Feedback


class FeedbackViewBaseMixin(object):
    def setup_other_user_and_file(self):
        raise NotImplementedError()

    def get_page_url(self):
        raise NotImplementedError()

    def check_feedback(self, feedback):
        raise NotImplementedError()

    def setup(self):
        self.user = ActiveUserFactory()
        self.setup_other_user_and_file()
        self.page_url = self.get_page_url()

    def test_visitor_can_see_feedback_form(self):
        r = self.client.get(path=self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='feedback/feedback_form.html')
        self.assertContains(response=r, text='id_sender_name')
        self.assertContains(response=r, text='id_sender_email')

    def test_visitor_can_submit_form(self):
        self.assertEqual(first=Feedback.objects.count(), second=0)
        data = {
            'sender_name': 'Mike',
            'sender_email': 'mike@example.com',
            'text': 'Hello',
        }
        r = self.client.post(path=self.page_url, data=data)
        self.assertRedirects(response=r, expected_url='/contact/thank-you/')
        self.assertEqual(first=Feedback.objects.count(), second=1)
        feedback = Feedback.objects.first()
        self.check_feedback(feedback=feedback)

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
        self.check_feedback(feedback=feedback)
        self.assertEqual(first=len(mail.outbox), second=1)
        self.assertEqual(first=mail.outbox[0].subject, second='{}: {}'.format(self.site.name, str(feedback)))


class FeedbackViewTypeFeedbackTestCase(FeedbackViewBaseMixin, TestCase):
    def setup_other_user_and_file(self):
        pass

    def get_page_url(self):
        return '/contact/'

    def check_feedback(self, feedback):
        self.assertEqual(first=feedback.type, second=Feedback.TYPE_FEEDBACK)


@only_on_sites_with_login
class FeedbackViewTypeReportEntityTestCase(FeedbackViewBaseMixin, TestCase):
    def setup_other_user_and_file(self):
        self.other_user = ActiveUserFactory()

    def get_page_url(self):
        return '/contact/report/entity/{}/'.format(self.other_user.slug)

    def check_feedback(self, feedback):
        self.assertEqual(first=feedback.type, second=Feedback.TYPE_REPORT_ENTITY)
        self.assertEqual(first=feedback.report_entity_id, second=self.other_user.id)

    def test_404(self):
        r = self.client.get(path='/contact/report/entity/abrakadabra/')
        self.assertEqual(first=r.status_code, second=404)


@only_on_sites_with_login
class FeedbackViewTypeReportFileTestCase(FeedbackViewBaseMixin, TestCase):
    def setup_other_user_and_file(self):
        self.file = FileFactory()

    def get_page_url(self):
        return '/contact/report/file/{}/'.format(self.file.id)

    def check_feedback(self, feedback):
        self.assertEqual(first=feedback.type, second=Feedback.TYPE_REPORT_FILE)
        self.assertEqual(first=feedback.report_file_id, second=self.file.id)

    def test_404(self):
        r = self.client.get(path='/contact/report/file/abrakadabra/')
        self.assertEqual(first=r.status_code, second=404)


