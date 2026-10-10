"""
Views of the Speedy Core accounts app: login, logout, password reset, registration, editing the profile, site profile activation, and managing user email addresses.
"""
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
    Allows a Speedy site to set or delete the session cookie on another Speedy site's domain,
    if the request's origin belongs to one of the sites. A POST request with a valid session key sets the session, otherwise the session is flushed.

    :param request: The current HTTP request.
    :type request: django.http.HttpRequest
    :return: An empty response, with CORS headers set if the origin is valid and the request was processed.
    :rtype: django.http.HttpResponse
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
    """
    View allowing a user to log in, rendering the site's custom login form and redirecting already-authenticated users away.
    """
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    extra_context = None
    redirect_authenticated_user = True


class LogoutView(django_auth_views.LogoutView):
    """
    View allowing a logged-in user to log out, rendering a confirmation page afterwards.
    """
    template_name = 'accounts/logged_out.html'


class PasswordResetView(django_auth_views.PasswordResetView):
    """
    View allowing a user to request a password reset email, rendering the site's custom password reset form and redirecting to the "done" page on success.
    """
    template_name = 'accounts/password_reset/form.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy(viewname='accounts:password_reset_done')


class PasswordResetDoneView(generic.TemplateView):
    """
    View rendering the confirmation page shown after a password reset email has been requested.
    """
    template_name = 'accounts/password_reset/done.html'


class PasswordResetConfirmView(django_auth_views.PasswordResetConfirmView):
    """
    View allowing a user to set a new password from a password reset link, rendering the site's custom set-password form and redirecting to the "complete" page on success.
    """
    template_name = 'accounts/password_reset/confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy(viewname='accounts:password_reset_complete')


class PasswordResetCompleteView(django_auth_views.PasswordResetCompleteView):
    """
    View rendering the confirmation page shown after a password has been successfully reset.
    """
    template_name = 'accounts/password_reset/complete.html'


class RegistrationView(generic.CreateView):
    """
    View allowing a new user to register an account.

    Saves the new user, optionally activates their site profile (depending on settings), logs the user in, sends a
    confirmation email to each of their email addresses, and redirects to the home page.

    Methods:
        form_valid(self, form): Save the new user, activate the profile if configured to, send confirmation emails and log the user in.
        get_form_kwargs(self): Add the current language code to the form's keyword arguments.
    """
    template_name = 'main/main_page.html'
    form_class = RegistrationForm

    # form_valid_message = _("Registration complete. Don't forget to confirm your email.")

    # def get_form_valid_message(self, form):
    #     return pgettext_lazy(context=self.object.get_gender(), message="Registration complete. Don't forget to confirm your email.")

    def form_valid(self, form):
        """
        Save the new user, optionally activate their profile, send confirmation emails to all of their email
        addresses, log the user in, and redirect to the home page.

        :param form: The validated registration form.
        :type form: speedy.core.accounts.forms.RegistrationForm
        :return: A redirect response to the home page.
        :rtype: django.http.HttpResponseRedirect
        """
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
        """
        Add the current language code to the form's keyword arguments.

        :return: The keyword arguments to instantiate the form with.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'language_code': get_language(),
        })
        return kwargs


class IndexView(generic.View):
    """
    View rendering the home page.

    Redirects already-authenticated users to their profile (or to another configured URL), redirects requests whose
    path isn't the canonical path, and otherwise delegates to the registration view to render the registration form.

    Attributes:
        canonical_full_path (str): The canonical path of the home page ("/").
        redirect_authenticated_users_to (str): The URL name or path to redirect authenticated users to.
        registration_view (type): The view class used to render the registration form for anonymous users.

    Methods:
        dispatch(self, request, *args, **kwargs): Redirect authenticated users, enforce the canonical path, and otherwise delegate to the registration view.
    """
    canonical_full_path = "/"
    redirect_authenticated_users_to = 'profiles:me'  # The default.
    registration_view = RegistrationView

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect authenticated users to their profile (or configured URL), enforce the canonical path for GET
        requests, and otherwise delegate to the registration view.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response, or the response from the registration view.
        :rtype: django.http.HttpResponse
        """
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
    """
    View allowing a logged-in user to edit their own profile details.

    Attributes:
        permission_required (str): The permission required to edit the profile ('accounts.edit_profile').

    Methods:
        get_form_kwargs(self): Add the current language code to the form's keyword arguments.
        get_object(self, queryset=None): Return the current user as the object being edited.
    """
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/profile.html'
    success_url = reverse_lazy(viewname='accounts:edit_profile')
    form_class = ProfileForm

    def get_form_kwargs(self):
        """
        Add the current language code to the form's keyword arguments.

        :return: The keyword arguments to instantiate the form with.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'language_code': get_language(),
        })
        return kwargs

    def get_object(self, queryset=None):
        """
        Return the current user as the object being edited.

        :param queryset: An optional queryset to use for looking up the object (unused).
        :type queryset: django.db.models.QuerySet or None
        :return: The user making the request.
        :rtype: speedy.core.accounts.models.User
        """
        return self.request.user


class EditProfileNotificationsView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    """
    View allowing a logged-in user to edit their notification settings.

    Attributes:
        permission_required (str): The permission required to edit the profile ('accounts.edit_profile').

    Methods:
        get_object(self, queryset=None): Return the current user as the object being edited.
    """
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/notifications.html'
    success_url = reverse_lazy(viewname='accounts:edit_profile_notifications')
    form_class = ProfileNotificationsForm

    def get_object(self, queryset=None):
        """
        Return the current user as the object being edited.

        :param queryset: An optional queryset to use for looking up the object (unused).
        :type queryset: django.db.models.QuerySet or None
        :return: The user making the request.
        :rtype: speedy.core.accounts.models.User
        """
        return self.request.user


class EditProfileCredentialsView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.FormView):
    """
    View allowing a logged-in user to change their password and manage their email addresses.

    Attributes:
        permission_required (str): The permission required to edit the profile ('accounts.edit_profile').

    Methods:
        get_form_kwargs(self): Add the current user to the form's keyword arguments.
        get_context_data(self, **kwargs): Add the user's email addresses (each with a privacy form) to the template context.
        form_valid(self, form): Save the new password, update the session's auth hash, and show a success message.
    """
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/credentials.html'
    success_url = reverse_lazy(viewname='accounts:edit_profile_credentials')
    form_class = PasswordChangeForm

    def get_form_kwargs(self):
        """
        Add the current user to the form's keyword arguments.

        :return: The keyword arguments to instantiate the form with.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add the user's email addresses, each annotated with its own privacy form, to the template context.

        :param kwargs: Additional keyword arguments passed by the calling view machinery.
        :type kwargs: dict
        :return: The context dictionary to render the template with.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        email_addresses = list(self.request.user.email_addresses.all())
        for address in email_addresses:
            address.privacy_form = UserEmailAddressPrivacyForm(instance=address)
        cd.update({
            'email_addresses': email_addresses,
        })
        return cd

    def form_valid(self, form):
        """
        Save the new password, update the session's authentication hash so the user stays logged in, and show a
        success message.

        :param form: The validated password change form.
        :type form: speedy.core.accounts.forms.PasswordChangeForm
        :return: The response produced by the superclass after a valid submission.
        :rtype: django.http.HttpResponse
        """
        form.save()
        user = self.request.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        update_session_auth_hash(request=self.request, user=user)
        messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Your new password has been saved.'))
        return super().form_valid(form)


class ActivateSiteProfileView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.UpdateView):
    """
    Base (abstract) view allowing a logged-in user to activate their site profile.

    Subclasses must override :meth:`get_account_activation_url` and are expected to provide the actual activation
    form via settings. Already-active users are redirected straight to ``success_url``, and users who haven't
    confirmed an email address (and didn't just register) are redirected to the account activation URL instead of
    being allowed to submit the form.

    Attributes:
        permission_required (str): The permission required to edit the profile ('accounts.edit_profile').

    Methods:
        get_object(self, queryset=None): Return the current user's site profile as the object being edited.
        get_form_class(self): Return the activation form class configured for the current site.
        dispatch(self, request, *args, **kwargs): Redirect already-active users to the success URL, otherwise delegate to the superclass.
        get_account_activation_url(self): Abstract method - must be implemented by subclasses.
        post(self, request, *args, **kwargs): Allow the form to be submitted only if the user has confirmed an email address or just registered.
    """
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/activate.html'
    success_url = '/'

    def get_object(self, queryset=None):
        """
        Return the current user's site profile as the object being edited.

        :param queryset: An optional queryset to use for looking up the object (unused).
        :type queryset: django.db.models.QuerySet or None
        :return: The site profile of the user making the request.
        :rtype: speedy.core.profiles.models.SiteProfileBase
        """
        return self.request.user.profile

    def get_form_class(self):
        """
        Return the site profile activation form class configured for the current site.

        :return: The form class to use for activating the site profile.
        :rtype: type
        """
        return reflection_import(name=django_settings.SITE_PROFILE_ACTIVATION_FORM)

    def dispatch(self, request, *args, **kwargs):
        """
        Redirect already-authenticated users whose site profile is already active to the success URL, otherwise
        delegate to the superclass.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response, or the response from the superclass.
        :rtype: django.http.HttpResponse
        """
        if ((request.user.is_authenticated) and (request.user.profile.is_active)):
            return redirect(to=self.success_url)
        return super().dispatch(request=request, *args, **kwargs)

    def get_account_activation_url(self):
        """
        Return the URL to redirect a user to when they need to confirm an email address before activating their
        profile.

        This method is not defined in this base (abstract) view; subclasses must override it.

        :raises NotImplementedError: Always, since this method must be implemented by subclasses.
        """
        # This method is not defined in this base (abstract) view.
        raise NotImplementedError("This method is not defined in this base (abstract) view.")

    def post(self, request, *args, **kwargs):
        """
        Allow the activation form to be submitted only if the user has confirmed an email address or just
        registered; otherwise redirect to the account activation URL.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The response from the superclass, or a redirect to the account activation URL.
        :rtype: django.http.HttpResponse
        """
        if (request.user.has_confirmed_email_or_registered_now):
            return super().post(request=request, *args, **kwargs)
        else:
            return redirect(to=self.get_account_activation_url())


class DeactivateSiteProfileView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.FormView):
    """
    View allowing a logged-in user to deactivate their site profile (a user can deactivate their account even if
    it is already inactive).

    Attributes:
        permission_required (str): The permission required to edit the profile ('accounts.edit_profile').

    Methods:
        get_form_kwargs(self): Add the current user to the form's keyword arguments.
        form_valid(self, form): Deactivate the profile, show a success message, and log the deactivation.
    """
    # A user can deactivate their account also if they are already inactive.
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/deactivate.html'
    form_class = SiteProfileDeactivationForm
    success_url = '/'

    def get_form_kwargs(self):
        """
        Add the current user to the form's keyword arguments.

        :return: The keyword arguments to instantiate the form with.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        """
        Deactivate the user's site profile, show a site-specific success message, and log the deactivation.

        :param form: The validated site profile deactivation form.
        :type form: speedy.core.accounts.forms.SiteProfileDeactivationForm
        :return: The response produced by the superclass after a valid submission.
        :rtype: django.http.HttpResponse
        """
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
    """
    View redirecting to the edit profile credentials page, which also manages the user's email addresses.
    """
    pattern_name = 'accounts:edit_profile_credentials'


class VerifyUserEmailAddressView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, SingleObjectMixin, generic.View):
    """
    View allowing a user to confirm one of their email addresses via a confirmation link's token.

    Attributes:
        model (type): The model this view looks up its object from (``UserEmailAddress``).
        permission_required (str): The permission required to confirm the email address ('accounts.edit_profile').
        success_url (str): The default URL to redirect to after handling the confirmation link.

    Methods:
        get_success_url(self): Return the URL to redirect to, preferring the Speedy Match matches page when applicable.
        get(self, request, *args, **kwargs): Verify the email address's confirmation token and redirect accordingly.
    """
    model = UserEmailAddress
    permission_required = 'accounts.edit_profile'
    success_url = reverse_lazy(viewname='accounts:edit_profile_emails')

    def get_success_url(self):
        """
        Return the URL to redirect to after handling the confirmation link, preferring the Speedy Match matches
        page when the user just confirmed their only email address on the Speedy Match site.

        :return: The URL to redirect to.
        :rtype: str
        """
        # If user came from Speedy Match and their email address is confirmed, redirect to matches page.
        if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
            if (self.request.user.email_addresses.filter(is_confirmed=True).count() == 1):
                return reverse_lazy(viewname='matches:list')
        return reverse_lazy(viewname='accounts:edit_profile_emails')

    def get(self, request, *args, **kwargs):
        """
        Verify that the requested email address belongs to the current user, then confirm it if the supplied
        token matches, showing an appropriate message, and redirect to the success URL. If the email address
        doesn't belong to the current user, log the user out and redirect to the same URL.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the success URL, or to the current URL after logging out.
        :rtype: django.http.HttpResponseRedirect
        :raises AssertionError: If the email address doesn't belong to the current user after the logout redirect check.
        """
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
    """
    View allowing a logged-in user to add a new email address to their account.

    Attributes:
        permission_required (str): The permission required to add the email address ('accounts.edit_profile').

    Methods:
        get_form_kwargs(self): Add the current user as the default owner of the new email address.
        form_valid(self, form): Send a confirmation email, make the address primary if it's the user's first, and show a success message.
    """
    permission_required = 'accounts.edit_profile'
    form_class = UserEmailAddressForm
    template_name = 'accounts/email_address_form.html'
    success_url = reverse_lazy(viewname='accounts:edit_profile_emails')

    def get_form_kwargs(self):
        """
        Add the current user as the default owner of the new email address.

        :return: The keyword arguments to instantiate the form with.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'defaults': {
                'user': self.request.user,
            }
        })
        return kwargs

    def form_valid(self, form):
        """
        Save the new email address, send it a confirmation email, make it the primary address if the user has no
        primary address yet, and show a success message.

        :param form: The validated email address form.
        :type form: speedy.core.accounts.forms.UserEmailAddressForm
        :return: The response produced by the superclass after a valid submission.
        :rtype: django.http.HttpResponse
        """
        response = super().form_valid(form)
        email_address = self.object
        email_address.send_confirmation_email()
        if (email_address.user.email_addresses.filter(is_primary=True).count() == 0):
            email_address.make_primary()
        messages.success(request=self.request, message=_('A confirmation message was sent to {email_address}').format(email_address=email_address.email))
        return response


class ResendConfirmationEmailView(PermissionRequiredMixin, SingleObjectMixin, generic.View):
    """
    View allowing a confirmation email to be resent for an email address.

    Attributes:
        model (type): The model this view looks up its object from (``UserEmailAddress``).
        permission_required (str): The permission required to resend the confirmation email ('accounts.confirm_useremailaddress').
        success_url (str): The URL to redirect to after handling the request.
        raise_exception (bool): Whether to raise ``PermissionDenied`` instead of redirecting to the login page when permission is missing.

    Methods:
        get(self, request, *args, **kwargs): Redirect to the success URL without resending the email.
        post(self, request, *args, **kwargs): Resend the confirmation email and show a success message.
    """
    model = UserEmailAddress
    permission_required = 'accounts.confirm_useremailaddress'
    success_url = reverse_lazy(viewname='accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """
        Redirect to the success URL without resending the confirmation email.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the success URL.
        :rtype: django.http.HttpResponseRedirect
        """
        return HttpResponseRedirect(redirect_to=self.success_url)

    def post(self, request, *args, **kwargs):
        """
        Resend the confirmation email for the requested email address and show a success message.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the success URL.
        :rtype: django.http.HttpResponseRedirect
        """
        email_address = self.get_object()
        email_address.send_confirmation_email()
        messages.success(request=self.request, message=_('A confirmation message was sent to {email_address}').format(email_address=email_address.email))
        return HttpResponseRedirect(redirect_to=self.success_url)


class DeleteUserEmailAddressView(PermissionRequiredMixin, generic.DeleteView):
    """
    View allowing an email address to be deleted.

    Attributes:
        model (type): The model this view deletes instances of (``UserEmailAddress``).
        permission_required (str): The permission required to delete the email address ('accounts.delete_useremailaddress').
        success_url (str): The URL to redirect to after handling the request.
        raise_exception (bool): Whether to raise ``PermissionDenied`` instead of redirecting to the login page when permission is missing.

    Methods:
        get(self, request, *args, **kwargs): Redirect to the success URL without deleting the email address.
        form_valid(self, *args, **kwargs): Delete the email address and show a success message.
    """
    model = UserEmailAddress
    permission_required = 'accounts.delete_useremailaddress'
    success_url = reverse_lazy(viewname='accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """
        Redirect to the success URL without deleting the email address.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the success URL.
        :rtype: django.http.HttpResponseRedirect
        """
        return HttpResponseRedirect(redirect_to=self.success_url)

    def form_valid(self, *args, **kwargs):
        """
        Delete the email address and show a success message.

        :param args: Positional arguments passed by the calling view machinery.
        :type args: tuple
        :param kwargs: Keyword arguments passed by the calling view machinery.
        :type kwargs: dict
        :return: The response produced by the superclass after deleting the object.
        :rtype: django.http.HttpResponse
        """
        response = super().form_valid(*args, **kwargs)
        messages.success(request=self.request, message=_('The email address was deleted.'))
        return response


class SetPrimaryUserEmailAddressView(PermissionRequiredMixin, SingleObjectMixin, generic.View):
    """
    View allowing a user to make one of their email addresses the primary one.

    Attributes:
        model (type): The model this view looks up its object from (``UserEmailAddress``).
        permission_required (str): The permission required to set the primary email address ('accounts.setprimary_useremailaddress').
        success_url (str): The URL to redirect to after handling the request.
        raise_exception (bool): Whether to raise ``PermissionDenied`` instead of redirecting to the login page when permission is missing.

    Methods:
        get(self, request, *args, **kwargs): Redirect to the success URL without changing the primary email address.
        post(self, request, *args, **kwargs): Make the email address primary and show a success message.
    """
    model = UserEmailAddress
    permission_required = 'accounts.setprimary_useremailaddress'
    success_url = reverse_lazy(viewname='accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """
        Redirect to the success URL without changing the primary email address.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the success URL.
        :rtype: django.http.HttpResponseRedirect
        """
        return HttpResponseRedirect(redirect_to=self.success_url)

    def post(self, request, *args, **kwargs):
        """
        Make the requested email address the user's primary one and show a success message.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the success URL.
        :rtype: django.http.HttpResponseRedirect
        """
        email_address = self.get_object()
        email_address.make_primary()
        messages.success(request=self.request, message=_('You have made this email address primary.'))
        return HttpResponseRedirect(redirect_to=self.success_url)


class ChangeUserEmailAddressPrivacyView(PermissionRequiredMixin, generic.UpdateView):
    """
    View allowing a user to change the privacy setting of one of their email addresses.

    Attributes:
        model (type): The model this view looks up its object from (``UserEmailAddress``).
        form_class (type): The form used to update the email address's privacy setting.
        permission_required (str): The permission required to change the privacy setting ('accounts.change_useremailaddress').
        success_url (str): The URL to redirect to after handling the request.
        raise_exception (bool): Whether to raise ``PermissionDenied`` instead of redirecting to the login page when permission is missing.

    Methods:
        get(self, request, *args, **kwargs): Redirect to the success URL without changing the privacy setting.
    """
    model = UserEmailAddress
    form_class = UserEmailAddressPrivacyForm
    permission_required = 'accounts.change_useremailaddress'
    success_url = reverse_lazy(viewname='accounts:edit_profile_emails')
    raise_exception = True

    def get(self, request, *args, **kwargs):
        """
        Redirect to the success URL without changing the privacy setting. The privacy setting is expected to be
        submitted via POST instead.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the success URL.
        :rtype: django.http.HttpResponseRedirect
        """
        return HttpResponseRedirect(redirect_to=self.success_url)


class EditProfilePrivacyView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, FormValidMessageMixin, generic.UpdateView):
    """
    View allowing a logged-in user to edit the privacy settings of their profile.

    Attributes:
        permission_required (str): The permission required to edit the profile ('accounts.edit_profile').

    Methods:
        get_object(self, queryset=None): Return the current user as the object being edited.
    """
    permission_required = 'accounts.edit_profile'
    template_name = 'accounts/edit_profile/privacy.html'
    success_url = reverse_lazy(viewname='accounts:edit_profile_privacy')
    form_class = ProfilePrivacyForm

    def get_object(self, queryset=None):
        """
        Return the current user as the object being edited.

        :param queryset: An optional queryset to use for looking up the object (unused).
        :type queryset: django.db.models.QuerySet or None
        :return: The user making the request.
        :rtype: speedy.core.accounts.models.User
        """
        return self.request.user


