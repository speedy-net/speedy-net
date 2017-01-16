from django.core.urlresolvers import reverse_lazy
from django.views import generic

from rules.contrib.views import LoginRequiredMixin

from speedy.core.views import FormValidMessageMixin
from .forms import ProfilePrivacyForm


class EditProfilePrivacyView(LoginRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    template_name = 'accounts_core/edit_profile/privacy.html'
    success_url = reverse_lazy('accounts:edit_profile_privacy')
    form_class = ProfilePrivacyForm

    def get_object(self, queryset=None):
        return self.request.user.profile
