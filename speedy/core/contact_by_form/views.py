from urllib import parse

from django.conf import settings as django_settings
from django.urls import reverse_lazy
from django.urls import resolve, Resolver404
from django.http import Http404
from django.views import generic

if (django_settings.LOGIN_ENABLED):
    from speedy.core.uploads.models import File
    from speedy.core.accounts.models import Entity

from .forms import FeedbackForm
from .models import Feedback


class FeedbackView(generic.CreateView):
    form_class = FeedbackForm
    template_name = 'contact_by_form/feedback_form.html'
    success_url = reverse_lazy('contact:success')

    def get_type(self):
        return self.kwargs.get('type', Feedback.TYPE_FEEDBACK)

    def get_report_entity(self):
        if (django_settings.LOGIN_ENABLED):
            slug = self.kwargs.get('report_entity_slug')
            if (self.get_type() != Feedback.TYPE_REPORT_ENTITY):
                return None
            try:
                self.report_entity = True
                return Entity.objects.get_by_slug(slug=slug)
            except Entity.DoesNotExist:
                raise Http404()
        else:
            return None

    def get_report_file(self):
        if (django_settings.LOGIN_ENABLED):
            report_file_id = self.kwargs.get('report_file_id')
            if (self.get_type() != Feedback.TYPE_REPORT_FILE):
                return None
            try:
                self.report_file = True
                return File.objects.get(pk=report_file_id)
            except (File.DoesNotExist, ValueError):
                raise Http404()
        else:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        defaults = {
            'sender': self.request.user if (self.request.user.is_authenticated) else None,
            'type': self.get_type(),
            'report_entity': self.get_report_entity(),
            'report_file': self.get_report_file(),
        }
        kwargs.update({'defaults': defaults})
        return kwargs


class FeedbackSuccessView(generic.TemplateView):
    template_name = 'contact_by_form/feedback_success.html'


