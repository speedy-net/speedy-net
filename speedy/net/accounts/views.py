from functools import partial

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, REDIRECT_FIELD_NAME
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _, get_language
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.detail import SingleObjectMixin
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

from .forms import RegistrationForm, LoginForm, UserEmailAddressForm, ProfileForm, ProfilePrivacyForm, PasswordChangeForm, DeactivationForm, ActivationForm, ProfileNotificationsForm
from .models import User, UserEmailAddress


class IndexView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            return reverse('profiles:me')
        else:
            return reverse('accounts:registration')


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'language': get_language(),
        })
        return kwargs


@sensitive_post_parameters()
@never_cache
def login(request, template_name='accounts/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=LoginForm,
          extra_context=None):
    response = auth_views.login(
        request,
        template_name=template_name,
        redirect_field_name=redirect_field_name,
        authentication_form=authentication_form,
        extra_context=extra_context,
    )
    return response


class EditProfileView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'accounts/edit_profile/account.html'
    success_url = reverse_lazy('accounts:edit_profile')
    form_class = ProfileForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'language': get_language(),
        })
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user


class EditProfilePrivacyView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'accounts/edit_profile/privacy.html'
    success_url = reverse_lazy('accounts:edit_profile_privacy')
    form_class = ProfilePrivacyForm

    def get_object(self, queryset=None):
        return self.request.user.profile


class EditProfileNotificationsView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'accounts/edit_profile/notifications.html'
    success_url = reverse_lazy('accounts:edit_profile_notifications')
    form_class = ProfileNotificationsForm

    def get_object(self, queryset=None):
        return self.request.user.profile


class EditProfileCredentialsView(LoginRequiredMixin, generic.FormView):
    template_name = 'accounts/edit_profile/credentials.html'
    success_url = reverse_lazy('accounts:edit_profile_credentials')
    form_class = PasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        user = self.request.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(self.request, user)
        return super().form_valid(form)


class DeactivateAccountView(LoginRequiredMixin, generic.FormView):
    template_name = 'accounts/edit_profile/deactivate.html'
    form_class = DeactivationForm
    success_url = '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.deactivate()
        auth_logout(self.request)
        messages.error(self.request, _('Your account has been deactivated.'))
        return super().form_valid(form)


@login_required
def activate(request):
    return auth_views.password_reset(
        request,
        post_reset_redirect='accounts:activate_done',
        template_name='accounts/activate/form.html',
        password_reset_form=partial(ActivationForm, request.user),
    )


@never_cache
def activate_confirm(request, uidb64=None, token=None):
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.activate()
        messages.success(request, _('Your account is now activated. Welcome back!'))
        return redirect('/')
    else:
        return render_to_response('accounts/activate/confirm.html')


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
