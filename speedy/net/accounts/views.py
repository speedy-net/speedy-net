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
    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'total_number_of_active_members_text': utils.get_total_number_of_active_members_text(),
        })
        return cd


class IndexView(speedy_core_accounts_views.IndexView):
    redirect_authenticated_users_to = 'profiles:me'
    registration_view = RegistrationView


class ActivateSiteProfileView(speedy_core_accounts_views.ActivateSiteProfileView):
    def get_account_activation_url(self):
        return reverse_lazy('accounts:activate')

    def display_welcome_message(self):
        site = Site.objects.get_current()
        messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Welcome to {site_name}! Your account is now active.').format(site_name=_(site.name)))

    def form_valid(self, form):
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
    permission_required = 'accounts.delete_account'
    template_name = 'accounts/edit_profile/delete_account.html'
    form_class = DeleteAccountForm
    success_url = '/'

    def __init__(self, *args, **kwargs):
        assert (django_settings.SITE_ID == django_settings.SPEEDY_NET_SITE_ID)
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
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


