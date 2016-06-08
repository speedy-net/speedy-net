from django.contrib import messages
from django.contrib.auth import login as auth_login, REDIRECT_FIELD_NAME
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.detail import SingleObjectMixin
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

from .forms import RegistrationForm, LoginForm, UserEmailAddressForm
from .models import User, UserEmailAddress


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

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, _('Registration complete. Don\'t forget to confirm your email.'))
        user = form.instance
        user.email_addresses.all()[0].send_confirmation_email()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(self.request, user)
        return HttpResponseRedirect('/')


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


class EditProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'accounts/edit_profile.html'


class VerifyUserEmailAddressView(SingleObjectMixin, generic.View):
    model = UserEmailAddress
    slug_field = 'confirmation_token'
    slug_url_kwarg = 'token'
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        email_address = self.get_object()
        if email_address.is_confirmed:
            messages.warning(self.request, _('You\'ve already confirmed this email address.'))
        else:
            email_address.verify()
            messages.success(self.request, _('You\'ve confirmed your email address.'))
        return HttpResponseRedirect(self.success_url)


class AddUserEmailAddressView(LoginRequiredMixin, generic.CreateView):
    form_class = UserEmailAddressForm
    template_name = 'accounts/email_address_form.html'
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'defaults': {
                'user': self.request.user,
            }
        })
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.send_confirmation_email()
        messages.success(self.request, 'A confirmation was sent to {}'.format(self.object.email))
        return response


class ResendConfirmationEmailView(PermissionRequiredMixin, SingleObjectMixin, generic.View):
    model = UserEmailAddress
    permission_required = 'accounts.confirm_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        email_address = self.get_object()
        email_address.send_confirmation_email()
        messages.success(self.request, 'A confirmation was sent to {}'.format(email_address.email))
        return HttpResponseRedirect(self.success_url)


class DeleteUserEmailAddressView(PermissionRequiredMixin, generic.DeleteView):
    model = UserEmailAddress
    permission_required = 'accounts.delete_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'The email address was deleted.')
        return response


class SetPrimaryUserEmailAddressView(PermissionRequiredMixin, SingleObjectMixin, generic.View):
    model = UserEmailAddress
    permission_required = 'accounts.setprimary_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def post(self, request, *args, **kwargs):
        email_address = self.get_object()
        email_address.make_primary()
        messages.success(self.request, 'You have changed your primary email address.')
        return HttpResponseRedirect(self.success_url)
