from django.core.urlresolvers import reverse_lazy
from django.views import generic

from rules.contrib.views import LoginRequiredMixin

from speedy.core.base.views import FormValidMessageMixin
from . import forms


class EditProfilePrivacyView(LoginRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    template_name = 'accounts/edit_profile/privacy.html'
    success_url = reverse_lazy('accounts:edit_profile_privacy')
    form_class = forms.AccountPrivacyForm

    def get_object(self, queryset=None):
        return self.request.user.profile

