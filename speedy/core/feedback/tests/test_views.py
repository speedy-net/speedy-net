from django.contrib.sites.models import Site
from django.core import mail

from speedy.core.accounts.tests.test_factories import USER_PASSWORD, ActiveUserFactory
from speedy.core.base.test import TestCase, exclude_on_speedy_composer, exclude_on_speedy_mail_software
from speedy.core.uploads.tests.test_factories import FileFactory
from ..models import Feedback


class FeedbackViewBaseMixin(object):
    def get_page_url(self):
        raise NotImplementedError()

    def check_feedback(self, feedback):
        raise NotImplementedError()

    def set_up(self):
        self.user = ActiveUserFactory()
        self.other_user = ActiveUserFactory()
        self.file = FileFactory()
        self.page_url = self.get_page_url()

    def test_visitor_can_see_feedback_form(self):
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='feedback/feedback_form.html')
        self.assertContains(response=r, text='id_sender_name')
        self.assertContains(response=r, text='id_sender_email')

    def test_visitor_can_submit_form(self):
        self.assertEqual(first=Feedback.objects.count(), second=0)
        r = self.client.post(self.page_url, data={
            'sender_name': 'Mike',
            'sender_email': 'mike@example.com',
            'text': 'Hello',
        })
        self.assertRedirects(response=r, expected_url='/contact/thank-you/')
        self.assertEqual(first=Feedback.objects.count(), second=1)
        feedback = Feedback.objects.first()
        self.check_feedback(feedback)

    @exclude_on_speedy_composer
    @exclude_on_speedy_mail_software
    def test_user_can_see_feedback_form(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        r = self.client.get(self.page_url)
        self.assertEqual(first=r.status_code, second=200)
        self.assertTemplateUsed(response=r, template_name='feedback/feedback_form.html')
        self.assertNotContains(response=r, text='id_sender_name')
        self.assertNotContains(response=r, text='id_sender_email')

    @exclude_on_speedy_composer
    @exclude_on_speedy_mail_software
    def test_user_can_submit_form(self):
        self.client.login(username=self.user.slug, password=USER_PASSWORD)
        self.assertEqual(first=Feedback.objects.count(), second=0)
        r = self.client.post(self.page_url, data={
            'text': 'Hello',
        })
        self.assertRedirects(response=r, expected_url='/contact/thank-you/')
        self.assertEqual(first=Feedback.objects.count(), second=1)
        feedback = Feedback.objects.first()
        self.check_feedback(feedback)
        self.assertEqual(first=len(mail.outbox), second=1)
        site = Site.objects.get_current()
        self.assertEqual(first=mail.outbox[0].subject, second='{}: {}'.format(site.name, str(feedback)))


class FeedbackViewTypeFeedbackTestCase(FeedbackViewBaseMixin, TestCase):
    def get_page_url(self):
        return '/contact/'

    def check_feedback(self, feedback):
        self.assertEqual(first=feedback.type, second=Feedback.TYPE_FEEDBACK)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class FeedbackViewTypeReportEntityTestCase(FeedbackViewBaseMixin, TestCase):
    def get_page_url(self):
        return '/contact/report/entity/{}/'.format(self.other_user.slug)

    def check_feedback(self, feedback):
        self.assertEqual(first=feedback.type, second=Feedback.TYPE_REPORT_ENTITY)
        self.assertEqual(first=feedback.report_entity_id, second=self.other_user.id)

    def test_404(self):
        r = self.client.get('/contact/report/entity/abrakadabra/')
        self.assertEqual(first=r.status_code, second=404)


@exclude_on_speedy_composer
@exclude_on_speedy_mail_software
class FeedbackViewTypeReportFileTestCase(FeedbackViewBaseMixin, TestCase):
    def get_page_url(self):
        return '/contact/report/file/{}/'.format(self.file.id)

    def check_feedback(self, feedback):
        self.assertEqual(first=feedback.type, second=Feedback.TYPE_REPORT_FILE)
        self.assertEqual(first=feedback.report_file_id, second=self.file.id)

    def test_404(self):
        r = self.client.get('/contact/report/file/abrakadabra/')
        self.assertEqual(first=r.status_code, second=404)


