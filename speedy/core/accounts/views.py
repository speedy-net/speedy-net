import logging
from importlib import import_module
from urllib.parse import urlparse

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import login as django_auth_login, logout as django_auth_logout, views as django_auth_views, update_session_auth_hash
from django.contrib.sites.models import Site
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _, pgettext_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

from speedy.core.base.views import FormValidMessageMixin
from speedy.core.profiles.views import SelfUserMixin
from speedy.core.base.utils import reflection_import
from .forms import LoginForm, PasswordResetForm, SetPasswordForm, RegistrationForm, UserEmailAddressForm, ProfileForm, PasswordChangeForm, SiteProfileDeactivationForm, ProfileNotificationsForm, UserEmailAddressPrivacyForm, ProfilePrivacyForm
from .models import UserEmailAddress

logger = logging.getLogger(__name__)


@csrf_exempt
def set_session(request):
    """
    Cross-domain authentication.
    """
    response = HttpResponse('')
    origin = request.META.get('HTTP_ORIGIN')
    if isinstance(origin, bytes):
        origin = origin.decode()
    netloc = urlparse(origin).netloc
    if isinstance(netloc, bytes):
        netloc = netloc.decode()
    valid_origin = any(netloc.endswith('.' + site.domain) for site in Site.objects.all().order_by("pk"))
    if (not (valid_origin)):
        return response
    if (request.method == 'POST'):
        session_key = request.POST.get('key')
        SessionStore = import_module(django_settings.SESSION_ENGINE).SessionStore
        if ((session_key) and (SessionStore().exists(session_key))):
            # Set session cookie
            request.session = SessionStore(session_key)
            request.session.modified = True
        else:
            # Delete session cookie
            request.session.flush()
    response['Access-Control-Allow-Origin'] = origin
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


class LoginView(django_auth_views.LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    extra_context = None
    redirect_authenticated_user = True


class LogoutView(django_auth_views.LogoutView):
    template_name = 'accounts/logged_out.html'


class PasswordResetView(django_auth_views.PasswordResetView):
    template_name = 'accounts/password_reset/form.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetDoneView(generic.TemplateView):
    template_name = 'accounts/password_reset/done.html'


class PasswordResetConfirmView(django_auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset/confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')


class PasswordResetCompleteView(django_auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset/complete.html'


class RegistrationView(generic.CreateView):
    template_name = 'main/main_page.html'
    form_class = RegistrationForm

    # form_valid_message = _("Registration complete. Don't forget to confirm your email.")

    # def get_form_valid_message(self, form):
    #     return pgettext_lazy(context=self.object.get_gender(), message="Registration complete. Don't forget to confirm your email.")

    def form_valid(self, form):
        self.object = form.save()
        logger.debug('RegistrationView::form_valid(): django_settings.ACTIVATE_PROFILE_AFTER_REGISTRATION: %s', django_settings.ACTIVATE_PROFILE_AFTER_REGISTRATION)
        if (django_settings.ACTIVATE_PROFILE_AFTER_REGISTRATION):
            logger.debug('RegistrationView::form_valid(): activating profile, profile: %s', self.object.profile)
            self.object.profile.activate()
        user = form.instance
        email_addresses = user.email_addresses.all()
        if (not (len(email_addresses) == 1)):
            site = Site.objects.get_current()
            language_code = get_language()
            logger.error("RegistrationView::form_valid::User has {len_email_addresses} email addresses, site_name={site_name}, user={user} (registered {registered_days_ago} days ago), language_code={language_code}.".format(
                len_email_addresses=len(email_addresses),
                site_name=_(site.name),
                user=user,
                registered_days_ago=(now() - user.date_created).days,
                language_code=language_code,
            ))
        for email_address in email_addresses:
            email_address.send_confirmation_email()
        user.backend = django_settings.DEFAULT_AUTHENTICATION_BACKEND
        django_auth_login(request=self.request, user=user)
        return HttpResponseRedirect(redirect_to='/')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'language_code': get_language(),
        })
        return kwargs


class IndexView(generic.View):
    canonical_full_path = "/"
    redirect_authenticated_users_to = 'profiles:me'  # The default.
    registration_view = RegistrationView

    def dispatch(self, request, *args, **kwargs):
        if (self.request.user.is_authenticated):
            if (self.redirect_authenticated_users_to == 'profiles:me'):
                # If redirect_authenticated_users_to == 'profiles:me', redirect to user's profile directly and not via /me/.
                return redirect(to=self.request.user.get_absolute_url())
            else:
                return redirect(to=self.redirect_authenticated_users_to)
        else:
            if request.method.lower() in ["get"]:
                if (not (request.get_full_path() == self.canonical_full_path)):
                    return redirect(to=self.canonical_full_path, permanent=True)
            return self.registration_view.as_view()(request=request, *args, **kwargs)


class EditProfileView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/profile.html'
    success_url = reverse_lazy('accounts:edit_profile')
    form_class = ProfileForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'language_code': get_language(),
        })
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user


class EditProfileNotificationsView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/notifications.html'
    success_url = reverse_lazy('accounts:edit_profile_notifications')
    form_class = ProfileNotificationsForm

    def get_object(self, queryset=None):
        return self.request.user


class EditProfileCredentialsView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.FormView):
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/credentials.html'
    success_url = reverse_lazy('accounts:edit_profile_credentials')
    form_class = PasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        email_addresses = list(self.request.user.email_addresses.all())
        for address in email_addresses:
            address.privacy_form = UserEmailAddressPrivacyForm(instance=address)
        cd.update({
            'email_addresses': email_addresses,
        })
        return cd

    def form_valid(self, form):
        form.save()
        user = self.request.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        update_session_auth_hash(request=self.request, user=user)
        messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Your new password has been saved.'))
        return super().form_valid(form)


class ActivateSiteProfileView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/activate.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_class(self):
        return reflection_import(name=django_settings.SITE_PROFILE_ACTIVATION_FORM)

    def dispatch(self, request, *args, **kwargs):
        if ((request.user.is_authenticated) and (request.user.profile.is_active)):
            return redirect(to=self.success_url)
        return super().dispatch(request=request, *args, **kwargs)

    def get_account_activation_url(self):
        # This function is not defined in this base (abstract) view.
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        if (request.user.has_confirmed_email_or_registered_now):
            return super().post(request=request, *args, **kwargs)
        else:
            return redirect(to=self.get_account_activation_url())


class DeactivateSiteProfileView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.FormView):
    # A user can deactivate their account also if they are already inactive.
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/deactivate.html'
    form_class = SiteProfileDeactivationForm
    success_url = '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.profile.deactivate()
        site = Site.objects.get_current()
        if (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID):
            message = pgettext_lazy(context=self.request.user.get_gender(), message='Your Speedy Net and Speedy Match accounts have been deactivated. You can reactivate them any time.')
        else:
            message = pgettext_lazy(context=self.request.user.get_gender(), message='Your {site_name} account has been deactivated. You can reactivate it any time. Your Speedy Net account remains active.').format(site_name=_(site.name))
        messages.success(request=self.request, message=message)
        language_code = get_language()
        logger.info('User {user} deactivated their account on {site_name} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
            site_name=_(site.name),
            user=user,
            registered_days_ago=(now() - user.date_created).days,
            language_code=language_code,
        ))
        return super().form_valid(form=form)


class EditProfileEmailsView(generic.RedirectView):
    pattern_name = 'accounts:edit_profile_credentials'


class VerifyUserEmailAddressView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, SingleObjectMixin, generic.View):
    model = UserEmailAddress
    permission_required = 'accounts.edit_profile'
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get_success_url(self):
        # If user came from Speedy Match and their email address is confirmed, redirect to matches page.
        if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            if (self.request.user.email_addresses.filter(is_confirmed=True).count() == 1):
                return reverse_lazy('matches:list')
        return reverse_lazy('accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        email_address = self.get_object()
        if (not (email_address.user == self.request.user)):
            django_auth_logout(request=self.request)
            return redirect(to=self.request.get_full_path())
        assert (email_address.user == self.request.user)
        token = self.kwargs.get('token')
        if (email_address.is_confirmed):
            messages.warning(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message="You've already confirmed this email address."))
        else:
            if (email_address.confirmation_token == token):
                email_address.verify()
                messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message="You've confirmed your email address."))
            else:
                messages.error(request=self.request, message=_('Invalid confirmation link.'))
        return HttpResponseRedirect(redirect_to=self.get_success_url())


class AddUserEmailAddressView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.CreateView):
    permission_required = 'accounts.edit_profile'
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
        email_address = self.object
        email_address.send_confirmation_email()
        if (email_address.user.email_addresses.filter(is_primary=True).count() == 0):
            email_address.make_primary()
        messages.success(request=self.request, message=_('A confirmation message was sent to {email_address}').format(email_address=email_address.email))
        return response


class ResendConfirmationEmailView(PermissionRequiredMixin, SingleObjectMixin, generic.View):
    model = UserEmailAddress
    permission_required = 'accounts.confirm_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=self.success_url)

    def post(self, request, *args, **kwargs):
        email_address = self.get_object()
        email_address.send_confirmation_email()
        messages.success(request=self.request, message=_('A confirmation message was sent to {email_address}').format(email_address=email_address.email))
        return HttpResponseRedirect(redirect_to=self.success_url)


class DeleteUserEmailAddressView(PermissionRequiredMixin, generic.DeleteView):
    model = UserEmailAddress
    permission_required = 'accounts.delete_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=self.success_url)

    def form_valid(self, *args, **kwargs):
        response = super().form_valid(*args, **kwargs)
        messages.success(request=self.request, message=_('The email address was deleted.'))
        return response


class SetPrimaryUserEmailAddressView(PermissionRequiredMixin, SingleObjectMixin, generic.View):
    model = UserEmailAddress
    permission_required = 'accounts.setprimary_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=self.success_url)

    def post(self, request, *args, **kwargs):
        email_address = self.get_object()
        email_address.make_primary()
        messages.success(request=self.request, message=_('You have made this email address primary.'))
        return HttpResponseRedirect(redirect_to=self.success_url)


class ChangeUserEmailAddressPrivacyView(PermissionRequiredMixin, generic.UpdateView):
    model = UserEmailAddress
    form_class = UserEmailAddressPrivacyForm
    permission_required = 'accounts.change_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=self.success_url)


class EditProfilePrivacyView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/privacy.html'
    success_url = reverse_lazy('accounts:edit_profile_privacy')
    form_class = ProfilePrivacyForm

    def get_object(self, queryset=None):
        return self.request.user


