"""
Views for the contact by form app of Speedy Core: the feedback form view and the feedback success page.
"""
from django.conf import settings as django_settings
from django.urls import reverse_lazy
from django.http import Http404
from django.views import generic

if (django_settings.LOGIN_ENABLED):
    from speedy.core.uploads.models import File
    from speedy.core.accounts.models import Entity

from .forms import FeedbackForm
from .models import Feedback


class FeedbackView(generic.CreateView):
    """
    View for submitting feedback, or reporting an entity or a file, via a form.

    Attributes:
        form_class (type): The form class used to submit feedback.
        template_name (str): The template used to render the feedback form.
        success_url (str): The URL to redirect to after a successful submission.

    Methods:
        get_type(self): Returns the feedback type from the URL kwargs (defaults to TYPE_FEEDBACK).
        get_report_entity(self): Returns the reported entity (if this is an entity report), or raises Http404 if not found.
        get_report_file(self): Returns the reported file (if this is a file report), or raises Http404 if not found.
        get_form_kwargs(self): Adds the sender, type, report_entity and report_file defaults to the form's keyword arguments.
    """
    form_class = FeedbackForm
    template_name = 'contact_by_form/feedback_form.html'
    success_url = reverse_lazy(viewname='contact:success')

    def get_type(self):
        """
        Returns the feedback type from the URL kwargs, defaulting to Feedback.TYPE_FEEDBACK.

        :return: The feedback type.
        :rtype: int
        """
        return self.kwargs.get('type', Feedback.TYPE_FEEDBACK)

    def get_report_entity(self):
        """
        Returns the entity being reported, when login is enabled and this is an entity report.

        :return: The reported entity, or None if login is disabled or this is not an entity report.
        :rtype: speedy.core.accounts.models.Entity or None
        :raises Http404: If login is enabled, this is an entity report, and no matching entity is found.
        """
        if (django_settings.LOGIN_ENABLED):
            slug = self.kwargs.get('report_entity_slug')
            if (self.get_type() != Feedback.TYPE_REPORT_ENTITY):
                return None
            self.report_entity = True
            entities = Entity.objects.filter_by_slug(slug=slug)
            if (len(entities) == 1):
                return entities[0]
            else:
                raise Http404()
        else:
            return None

    def get_report_file(self):
        """
        Returns the file being reported, when login is enabled and this is a file report.

        :return: The reported file, or None if login is disabled or this is not a file report.
        :rtype: speedy.core.uploads.models.File or None
        :raises Http404: If login is enabled, this is a file report, and no matching file is found.
        """
        if (django_settings.LOGIN_ENABLED):
            report_file_id = self.kwargs.get('report_file_id')
            if (self.get_type() != Feedback.TYPE_REPORT_FILE):
                return None
            self.report_file = True
            files = File.objects.filter(pk=report_file_id)
            if (len(files) == 1):
                return files[0]
            else:
                raise Http404()
        else:
            return None

    def get_form_kwargs(self):
        """
        Adds the sender (current authenticated user, if any), feedback type, reported entity, and reported file as the form's defaults.

        :return: The form's keyword arguments, including the defaults.
        :rtype: dict
        """
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
    """
    View that renders a thank-you page after a successful feedback submission.

    Attributes:
        template_name (str): The template used to render the success page.
    """
    template_name = 'contact_by_form/feedback_success.html'


