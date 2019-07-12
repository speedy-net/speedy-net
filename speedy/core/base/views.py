from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic


class StaticBaseView(generic.TemplateView):
    # canonical_full_path must be defined in classes inherited from this class.

    def get(self, request, *args, **kwargs):
        if (request.get_full_path() == self.canonical_full_path):
            return super().get(request=request, *args, **kwargs)
        else:
            return redirect(to=self.canonical_full_path, permanent=True)

    class Meta:
        abstract = True


class StaticMainPageBaseView(StaticBaseView):
    canonical_full_path = "/"

    class Meta:
        abstract = True


class StaticAboutBaseView(StaticBaseView):
    canonical_full_path = "/about/"

    class Meta:
        abstract = True


class StaticPrivacyPolicyBaseView(StaticBaseView):
    canonical_full_path = "/privacy/"

    class Meta:
        abstract = True


class StaticTermsOfServiceBaseView(StaticBaseView):
    canonical_full_path = "/terms/"

    class Meta:
        abstract = True


class StaticContactBaseView(StaticBaseView):
    canonical_full_path = "/contact/"

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


