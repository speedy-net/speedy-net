from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.views import generic

from speedy.core.uploads.models import File
from speedy.core.accounts.models import Entity
from .forms import FeedbackForm
from .models import Feedback


class FeedbackView(generic.CreateView):
    form_class = FeedbackForm
    template_name = 'feedback/feedback_form.html'
    success_url = reverse_lazy('feedback:success')

    def get_type(self):
        return self.kwargs.get('type', Feedback.TYPE_FEEDBACK)

    def get_report_entity(self):
        slug = self.kwargs.get('report_entity_slug')
        if self.get_type() != Feedback.TYPE_REPORT_ENTITY:
            return None
        try:
            return Entity.objects.get(slug=slug)
        except Entity.DoesNotExist:
            raise Http404()

    def get_report_file(self):
        id = self.kwargs.get('report_file_id')
        if self.get_type() != Feedback.TYPE_REPORT_FILE:
            return None
        try:
            return File.objects.get(id=id)
        except (File.DoesNotExist, ValueError):
            raise Http404()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        defaults = {
            'sender': self.request.user if self.request.user.is_authenticated() else None,
            'type': self.get_type(),
            'report_entity': self.get_report_entity(),
            'report_file': self.get_report_file(),
        }
        kwargs.update({'defaults': defaults})
        return kwargs



class FeedbackSuccessView(generic.TemplateView):
    template_name = 'feedback/feedback_success.html'
