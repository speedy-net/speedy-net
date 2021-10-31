import logging

from django.contrib import messages
from django.contrib.sites.models import Site
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy, gettext_lazy as _

from speedy.core.accounts import views as speedy_core_accounts_views
from speedy.match.accounts import utils
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

from .forms import ProfileNotificationsForm

logger = logging.getLogger(__name__)


class RegistrationView(speedy_core_accounts_views.RegistrationView):
    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'total_number_of_active_members_text': utils.get_total_number_of_active_members_text(),
        })
        return cd


class IndexView(speedy_core_accounts_views.IndexView):
    redirect_authenticated_users_to = 'matches:list'
    registration_view = RegistrationView


class ActivateSiteProfileView(speedy_core_accounts_views.ActivateSiteProfileView):
    def get_context_data(self, **kwargs):
        if (self.request.user.is_authenticated):
            if ((now() - self.request.user.date_created).days < 7):
                include_in_conversions = True
            else:
                include_in_conversions = False
        else:
            include_in_conversions = False
        cd = super().get_context_data(**kwargs)
        cd.update({
            'steps_range': list(utils.get_steps_range()),
            'current_step': self.step,
            'previous_step': self.step - 1,
            'include_in_conversions': include_in_conversions,
        })
        return cd

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['step'] = self.step
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if (not (self.request.user.is_authenticated)):
            return super().dispatch(request=request, *args, **kwargs)
        if (request.user.is_active):
            try:
                if (not ('step' in kwargs)):
                    return redirect(to='accounts:activate', step=self.request.user.speedy_match_profile.activation_step)
                self.step = int(kwargs['step'])
            except (ValueError):
                return redirect(to='accounts:activate', step=self.request.user.speedy_match_profile.activation_step)
        else:
            if (('step' in kwargs) or (not (request.path == reverse('accounts:activate')))):
                return redirect(to='accounts:activate')
        return super().dispatch(request=request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if (not (request.user.is_active)):
            return render(request=self.request, template_name=self.template_name, context={})
        if (self.step <= 1):
            return redirect(to='accounts:edit_profile')
        if ((self.step >= len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS)) and (request.user.speedy_match_profile.is_active_and_valid)):
            return redirect(to='matches:list')
        if ((self.step > request.user.speedy_match_profile.activation_step) or (self.step >= len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))):
            step = min(request.user.speedy_match_profile.activation_step, len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS) - 1)
            return redirect(to='accounts:activate', step=step)
        if (request.user.speedy_match_profile.is_active):
            logger.error('get inside "if (request.user.speedy_match_profile.is_active):"')
        # Step must be an integer from 2 to 9.
        assert (self.step in range(2, 10))
        assert (self.step <= request.user.speedy_match_profile.activation_step)
        return super().get(request=self.request, *args, **kwargs)

    def get_account_activation_url(self):
        return reverse_lazy('accounts:activate', kwargs={'step': self.step})

    def display_welcome_message(self):
        site = Site.objects.get_current()
        messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Welcome to {site_name}!').format(site_name=_(site.name)))

    def display_not_allowed_to_use_speedy_match_message(self):
        site = Site.objects.get_current()
        messages.error(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message="We're sorry, but you are not authorized to use the {site_name} website. We have found that some of the information you provided when registering on the site is incorrect or that you have violated the rules of use of the site. Therefore you are not authorized to use the site.").format(site_name=_(site.name)))

    def get_success_url(self):
        if (self.step >= len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS) - 1):
            if (self.request.user.has_confirmed_email):
                self.request.user.speedy_match_profile.validate_profile_and_activate()
                if (self.request.user.speedy_match_profile.is_active):
                    return reverse_lazy('matches:list')
                else:
                    return reverse_lazy('accounts:activate', kwargs={'step': self.request.user.speedy_match_profile.activation_step})
            else:
                return reverse_lazy('accounts:edit_profile_emails')
        else:
            return reverse_lazy('accounts:activate', kwargs={'step': self.step + 1})

    def form_valid(self, form):
        super().form_valid(form=form)
        success_url = self.get_success_url()
        if (self.request.user.speedy_match_profile.is_active):
            self.display_welcome_message()
            site = Site.objects.get_current()
            logger.info('User {user} activated their account on {site_name} (registered {registered_days_ago} days ago).'.format(
                site_name=_(site.name),
                user=self.request.user,
                registered_days_ago=(now() - self.request.user.date_created).days,
            ))
            if (not (SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH <= self.request.user.speedy_match_profile.height <= SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH)):
                self.request.user.speedy_match_profile.not_allowed_to_use_speedy_match = True
                self.request.user.save_user_and_profile()
                logger.error('User {user} is not allowed to use Speedy Match (height={height}) (registered {registered_days_ago} days ago).'.format(
                    user=self.request.user,
                    height=self.request.user.speedy_match_profile.height,
                    registered_days_ago=(now() - self.request.user.date_created).days,
                ))
        elif (self.request.user.speedy_match_profile.not_allowed_to_use_speedy_match):
            self.display_not_allowed_to_use_speedy_match_message()
        return redirect(to=success_url)


class EditProfileNotificationsView(speedy_core_accounts_views.EditProfileNotificationsView):
    form_class = ProfileNotificationsForm


