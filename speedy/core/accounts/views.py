from importlib import import_module
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, REDIRECT_FIELD_NAME, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _, get_language, pgettext_lazy
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.detail import SingleObjectMixin
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

from speedy.core.base.views import FormValidMessageMixin
from speedy.core.base.utils import reflection_import
from .forms import RegistrationForm, LoginForm, UserEmailAddressForm, ProfileForm, PasswordChangeForm, SiteProfileDeactivationForm, SiteProfileActivationForm, ProfileNotificationsForm, UserEmailAddressPrivacyForm
from .models import UserEmailAddress


@csrf_exempt
def set_session(request):
    """
    Cross-domain authentication.
    """
    response = HttpResponse('')
    origin = request.META.get('HTTP_ORIGIN')
    netloc = urlparse(origin).netloc
    valid_origin = any(netloc.endswith('.' + site.domain) for site in Site.objects.all().order_by("pk"))
    if not valid_origin:
        return response
    if request.method == 'POST':
        session_key = request.POST.get('key')
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        if session_key and SessionStore().exists(session_key):
            # Set session cookie
            request.session = SessionStore(session_key)
            request.session.modified = True
        else:
            # Delete session cookie
            request.session.flush()
    response['Access-Control-Allow-Origin'] = origin
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


class IndexView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return redirect(to='profiles:me')
        else:
            return RegistrationView.as_view()(request=request, *args, **kwargs)


class RegistrationView(FormValidMessageMixin, generic.CreateView):
    template_name = 'accounts/registration.html'
    form_class = RegistrationForm
    form_valid_message = _('Registration complete. Don\'t forget to confirm your email.')

    def form_valid(self, form):
        self.object = form.save()
        if settings.ACTIVATE_PROFILE_AFTER_REGISTRATION:
            self.object.profile.activate()
        user = form.instance
        user.email_addresses.all()[0].send_confirmation_email()
        user.backend = settings.DEFAULT_AUTHENTICATION_BACKEND
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
def login(request, template_name='accounts/login.html', redirect_field_name=REDIRECT_FIELD_NAME, authentication_form=LoginForm, extra_context=None):
    response = auth_views.login(
        request,
        template_name=template_name,
        redirect_field_name=redirect_field_name,
        authentication_form=authentication_form,
        extra_context=extra_context,
    )
    return response


class EditProfileView(LoginRequiredMixin, FormValidMessageMixin, generic.UpdateView):
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


class EditProfileNotificationsView(LoginRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    template_name = 'accounts/edit_profile/notifications.html'
    success_url = reverse_lazy('accounts:edit_profile_notifications')
    form_class = ProfileNotificationsForm

    def get_object(self, queryset=None):
        return self.request.user.profile


class EditProfileCredentialsView(LoginRequiredMixin, FormValidMessageMixin, generic.FormView):
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
        update_session_auth_hash(self.request, user)
        messages.success(self.request, pgettext_lazy(self.request.user.get_gender(), 'Your new password has been saved.'))
        return super().form_valid(form)


class ActivateSiteProfileView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'accounts/edit_profile/activate.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_class(self):
        return reflection_import(settings.SITE_PROFILE_ACTIVATION_FORM)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.is_active:
            return redirect(to=self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        SPEEDY_NET_SITE_ID = settings.SITE_PROFILES['net']['site_id']
        cd.update({'speedy_net_url': Site.objects.get(id=SPEEDY_NET_SITE_ID).domain})
        return cd

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'gender_to_match' in self.request.POST:
            kwargs['data']['gender_to_match'] = ','.join(self.request.POST.getlist('gender_to_match'))
        return kwargs

    def get(self, request, *args, **kwargs):
        site = Site.objects.get_current()
        SPEEDY_MATCH_SITE_ID = settings.SITE_PROFILES['match']['site_id']
        SPEEDY_NET_SITE_ID = settings.SITE_PROFILES['net']['site_id']
        if ((not (site.pk == SPEEDY_NET_SITE_ID)) and (not (request.user.get_profile(model=None, profile_model=settings.SITE_PROFILES['net']['site_profile_model']).is_active))):
            return render(self.request, self.template_name, {'speedy_net_url': Site.objects.get(id=SPEEDY_NET_SITE_ID).domain})
        if ((site.pk == SPEEDY_MATCH_SITE_ID) and ('back' in request.GET)):
            if request.user.profile.activation_step >= 1:
                request.user.profile.activation_step -= 1
                request.user.profile.save()
        if ((site.pk == SPEEDY_MATCH_SITE_ID) and ('step' in request.GET)):
            if (request.GET.get('step') == '-1'):
                return redirect('accounts:edit_profile')
            step, errors = self.request.user.profile.validate_profile_and_activate()
            self.request.user.profile.activation_step = min(int(request.GET.get('step')), step)
            self.request.user.profile.save(update_fields={'activation_step'})
        if ((site.pk == SPEEDY_MATCH_SITE_ID) and (not (self.request.user.profile.is_active)) and (self.request.user.profile.activation_step == len(settings.SITE_PROFILE_FORM_FIELDS))):
            return redirect(reverse_lazy('accounts:edit_profile_credentials'))
        return super().get(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.has_verified_email:
            return super().post(request, *args, **kwargs)
        else:
            return redirect(to=reverse_lazy('accounts:activate'))

    def form_valid(self, form):
        response = super().form_valid(form=form)
        if self.object.is_active:
            messages.success(self.request, _('Welcome to {}!').format(Site.objects.get_current().name))
        else:
            return redirect(reverse_lazy('accounts:activate'))
        return response


class DeactivateSiteProfileView(LoginRequiredMixin, generic.FormView):
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
        current_site = Site.objects.get_current()
        if settings.SITE_ID == 1:
            message = _('Your Speedy Net and Speedy Match account has been deactivated. You can reactivate it any time.')
        else:
            message = _('Your {} account has been deactivated. You can reactivate it any time. Your Speedy Net account remains intact.')
        messages.success(request=self.request, message=message)
        return super().form_valid(form=form)


class VerifyUserEmailAddressView(LoginRequiredMixin, SingleObjectMixin, generic.View):
    model = UserEmailAddress
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        email_address = self.get_object()
        token = self.kwargs.get('token')
        if email_address.is_confirmed:
            messages.warning(self.request, pgettext_lazy(self.request.user.get_gender(), 'You\'ve already confirmed this email address.'))
        else:
            if email_address.confirmation_token == token:
                email_address.verify()
                messages.success(self.request, pgettext_lazy(self.request.user.get_gender(), 'You\'ve confirmed your email address.'))
            else:
                messages.error(self.request, _('Invalid confirmation link.'))
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
        email_address = self.object
        email_address.send_confirmation_email()
        if email_address.user.email_addresses.filter(is_primary=True).count() == 0:
            email_address.make_primary()
        messages.success(self.request, 'A confirmation was sent to {}'.format(email_address.email))
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


class ChangeUserEmailAddressPrivacyView(PermissionRequiredMixin, generic.UpdateView):
    model = UserEmailAddress
    form_class = UserEmailAddressPrivacyForm
    permission_required = 'accounts.change_useremailaddress'
    success_url = reverse_lazy('accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)
