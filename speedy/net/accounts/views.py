import logging

from django.contrib import messages
from django.contrib.sites.models import Site
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import pgettext_lazy, ugettext as _
from django.utils.timezone import now

from speedy.core.accounts import views as speedy_core_accounts_views
from speedy.net.accounts import utils

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
            logger.info('User {user} activated their account on {site_name} (registered {registered_days_ago} days ago).'.format(
                site_name=_(site.name),
                user=self.request.user,
                registered_days_ago=(now() - self.request.user.date_created).days,
            ))
        return redirect(to=success_url)


