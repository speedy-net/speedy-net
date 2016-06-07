from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, REDIRECT_FIELD_NAME
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

from .forms import RegistrationForm, LoginForm
from .models import User


class IndexView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return reverse('accounts:me')
        else:
            return reverse('accounts:registration')


class MeView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.request.user.get_absolute_url()


class UserProfileView(generic.DetailView):
    template_name = 'accounts/user_profile.html'
    model = User


class RegistrationView(generic.CreateView):
    template_name = 'accounts/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:registration_success')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Registration complete. Don\'t forget to confirm your email.'))
        user = form.instance
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        auth_login(self.request, user)
        return response


@sensitive_post_parameters()
@never_cache
def login(request, template_name='accounts/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=LoginForm,
          extra_context=None):
    response = auth_views.login(request, template_name=template_name,
                                redirect_field_name=redirect_field_name,
                                authentication_form=authentication_form,
                                extra_context=extra_context)
    if response.status_code == 302:
        messages.success(request, _('Welcome back.'))
    return response
