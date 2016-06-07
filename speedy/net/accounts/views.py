from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views import generic

from .forms import RegistrationForm


class RegistrationView(generic.CreateView):
    template_name = 'accounts/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:registration_success')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'OK')
        return response
