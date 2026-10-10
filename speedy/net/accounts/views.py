import logging

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import logout as django_auth_logout
from django.contrib.sites.models import Site
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.timezone import now
from django.utils.translation import get_language, pgettext_lazy, gettext_lazy as _
from django.views import generic
from rules.contrib.views import LoginRequiredMixin, PermissionRequiredMixin

from speedy.core.accounts import views as speedy_core_accounts_views
from speedy.core.profiles.views import SelfUserMixin
from speedy.core.accounts.models import User
from speedy.net.accounts import utils
from .forms import DeleteAccountForm

logger = logging.getLogger(__name__)


class RegistrationView(speedy_core_accounts_views.RegistrationView):
    """
    Registration view for Speedy Net. Adds the total number of active members text to the template context.

    Methods:
        get_context_data(self, **kwargs): Add the total number of active members text to the context.
    """
    def get_context_data(self, **kwargs):
        """
        Add the total number of active members text to the context.

        :param kwargs: Additional keyword arguments.
        :return: The context data.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'total_number_of_active_members_text': utils.get_total_number_of_active_members_text(),
        })
        return cd


class IndexView(speedy_core_accounts_views.IndexView):
    """
    The home page view of Speedy Net. Redirects authenticated users to their profile page, and uses the Speedy Net registration view for anonymous users.
    """
    redirect_authenticated_users_to = 'profiles:me'
    registration_view = RegistrationView


class ActivateSiteProfileView(speedy_core_accounts_views.ActivateSiteProfileView):
    """
    View used to activate a newly registered user's Speedy Net profile.

    Methods:
        get_account_activation_url(self): Get the URL of the account activation page.
        display_welcome_message(self): Display a welcome message to the user once their account is active.
        form_valid(self, form): Activate the profile, display the welcome message, log the activation, and redirect to the success URL.
    """
    def get_account_activation_url(self):
        """
        Get the URL of the account activation page.

        :return: The URL of the account activation page.
        :rtype: django.utils.functional.Promise
        """
        return reverse_lazy(viewname='accounts:activate')

    def display_welcome_message(self):
        """
        Display a welcome message to the user once their account is active.
        """
        site = Site.objects.get_current()
        messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Welcome to {site_name}! Your account is now active.').format(site_name=_(site.name)))

    def form_valid(self, form):
        """
        Activate the profile, display the welcome message, log the activation, and redirect to the success URL.

        :param form: The validated form.
        :type form: django.forms.Form
        :return: A redirect to the success URL.
        :rtype: django.http.HttpResponseRedirect
        """
        super().form_valid(form=form)
        success_url = self.get_success_url()
        if (self.request.user.speedy_net_profile.is_active):
            self.display_welcome_message()
            site = Site.objects.get_current()
            language_code = get_language()
            logger.info('User {user} activated their account on {site_name} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                site_name=_(site.name),
                user=self.request.user,
                registered_days_ago=(now() - self.request.user.date_created).days,
                language_code=language_code,
            ))
        return redirect(to=success_url)


class DeleteAccountView(LoginRequiredMixin, SelfUserMixin, PermissionRequiredMixin, generic.FormView):
    """
    View used by a user to permanently delete their Speedy Net (and Speedy Match) account.

    Attributes:
        permission_required (str): The permission required to access this view.
        template_name (str): The template used to render this view.
        form_class (type): The form class used to confirm the deletion.
        success_url (str): The URL to redirect to after a successful deletion.

    Methods:
        __init__(self, *args, **kwargs): Assert that this view is only used on the Speedy Net site.
        get_form_kwargs(self): Add the current user to the form kwargs.
        form_valid(self, form): Mark the user as deleted, display a confirmation message, log the deletion, log the user out, and redirect to the index page.
    """
    permission_required = 'accounts.delete_account'
    template_name = 'accounts/edit_profile/delete_account.html'
    form_class = DeleteAccountForm
    success_url = '/'

    def __init__(self, *args, **kwargs):
        """
        Assert that this view is only used on the Speedy Net site.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        assert (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID)
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self):
        """
        Add the current user to the form kwargs.

        :return: The keyword arguments used to instantiate the form.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        """
        Mark the user as deleted, display a confirmation message, log the deletion, log the user out, and redirect to the index page.

        :param form: The validated form.
        :type form: speedy.net.accounts.forms.DeleteAccountForm
        :return: A redirect to the index page.
        :rtype: django.http.HttpResponseRedirect
        """
        super().form_valid(form=form)
        user = self.request.user
        assert (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID)
        assert (form.cleaned_data['delete_my_account_text'] == _("Yes. Delete my account."))
        assert (user.is_active is False)
        assert (user.is_staff is False)
        assert (user.is_superuser is False)
        User.objects.mark_a_user_as_deleted(user=user, delete_password="Mark this user as deleted in Speedy Net.")
        site = Site.objects.get_current()
        message = pgettext_lazy(context=self.request.user.get_gender(), message='Your Speedy Net and Speedy Match accounts have been deleted. Thank you for using {site_name}.').format(site_name=_(site.name))
        messages.success(request=self.request, message=message)
        language_code = get_language()
        logger.info('User {user} deleted their account on {site_name} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
            site_name=_(site.name),
            user=user,
            registered_days_ago=(now() - user.date_created).days,
            language_code=language_code,
        ))
        django_auth_logout(request=self.request)
        return redirect(to='accounts:index')


