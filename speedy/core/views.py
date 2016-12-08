from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic


class StaticMainPageBaseView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        if (request.get_full_path() == "/"):
            return super().get(request=request, *args, **kwargs)
        else:
            return redirect(to="/", permanent=True)

    class Meta:
        abstract = True


class FormValidMessageMixin(object):
    form_valid_message = _('Changes saved.')

    def get_form_valid_message(self, form):
        return self.form_valid_message

    def form_valid(self, form):
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=self.get_form_valid_message(form=form))
        return response
