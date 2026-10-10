"""
Views of the Speedy Match accounts app: registration, the index page, the site profile activation wizard and editing the profile notifications.
"""
import logging

from django.contrib import messages
from django.contrib.sites.models import Site
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.utils.translation import get_language, pgettext_lazy, gettext_lazy as _

from speedy.core.accounts import views as speedy_core_accounts_views
from speedy.match.accounts import utils
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

from .forms import ProfileNotificationsForm

logger = logging.getLogger(__name__)


class RegistrationView(speedy_core_accounts_views.RegistrationView):
    """
    Registration view for Speedy Match, adding the total number of active members text to the template context.

    Methods:
        get_context_data(self, **kwargs): Adds the active members count text to the context.
    """

    def get_context_data(self, **kwargs):
        """
        Adds the active members count text to the template context.

        :param kwargs: Keyword arguments passed to the parent view.
        :return: The updated context dictionary.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'total_number_of_active_members_text': utils.get_total_number_of_active_members_text(),
        })
        return cd


class IndexView(speedy_core_accounts_views.IndexView):
    """
    Speedy Match home page view, redirecting authenticated users to their matches list.
    """
    redirect_authenticated_users_to = 'matches:list'
    registration_view = RegistrationView


class ActivateSiteProfileView(speedy_core_accounts_views.ActivateSiteProfileView):
    """
    Multi-step activation view for the Speedy Match site profile, guiding the user through the profile activation wizard steps.

    Methods:
        get_context_data(self, **kwargs): Adds step and conversion-tracking info to the context.
        get_form_kwargs(self): Adds the current step to the form's keyword arguments.
        dispatch(self, request, *args, **kwargs): Validates and redirects based on the requested step and the user's state.
        get(self, request, *args, **kwargs): Handles GET requests, redirecting when the step is invalid or already completed.
        get_account_activation_url(self): Returns the URL for the current activation step.
        display_welcome_message(self): Displays a welcome message after successful activation.
        display_not_allowed_to_use_speedy_match_message(self): Displays a message informing the user they are not authorized to use the site.
        get_success_url(self): Returns the URL to redirect to after a successful form submission.
        form_valid(self, form): Handles a valid form submission, activating the account and displaying relevant messages.
    """

    def get_context_data(self, **kwargs):
        """
        Adds the step range, current and previous step numbers, and the conversion-tracking flag (true for users registered within the last 7 days) to the template context.

        :param kwargs: Keyword arguments passed to the parent view.
        :return: The updated context dictionary.
        :rtype: dict
        """
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
        """
        Adds the current activation step to the form's keyword arguments.

        :return: The updated keyword arguments for instantiating the form.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs['step'] = self.step
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """
        Validates the requested step against the user's authentication and activation state, redirecting to the correct activation step (or the activation entry point) when needed, before dispatching to the parent view.

        :param request: The current HTTP request.
        :param args: Positional arguments passed to the parent view.
        :param kwargs: Keyword arguments passed to the parent view; may include "step".
        :return: The HTTP response, either a redirect or the parent view's response.
        """
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
            if (('step' in kwargs) or (not (request.path == reverse(viewname='accounts:activate')))):
                return redirect(to='accounts:activate')
        return super().dispatch(request=request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests: redirects to profile editing or the matches list when appropriate, redirects to the correct step when the requested step is invalid or beyond the user's progress, then delegates to the parent view.

        :param request: The current HTTP request.
        :param args: Positional arguments passed to the parent view.
        :param kwargs: Keyword arguments passed to the parent view.
        :return: The HTTP response, either a redirect or the parent view's response.
        """
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
        """
        Returns the URL for the current activation step.

        :return: The activation step URL.
        :rtype: str
        """
        return reverse_lazy(viewname='accounts:activate', kwargs={'step': self.step})

    def display_welcome_message(self):
        """
        Displays a success message welcoming the user to the site, after they successfully activate their profile.
        """
        site = Site.objects.get_current()
        messages.success(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Welcome to {site_name}!').format(site_name=_(site.name)))

    def display_not_allowed_to_use_speedy_match_message(self):
        """
        Displays an error message informing the user that they are not authorized to use the site.
        """
        site = Site.objects.get_current()
        messages.error(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message="We're sorry, but you are not authorized to use the {site_name} website. We have found that some of the information you provided when registering on the site is incorrect or that you have violated the rules of use of the site. Therefore you are not authorized to use the site.").format(site_name=_(site.name)))

    def get_success_url(self):
        """
        Returns the URL to redirect to after a successful form submission: the next activation step, the matches list if the profile is now fully active, the email confirmation page if the user hasn't confirmed their email yet, or back to the current step if validation still isn't complete.

        :return: The success URL.
        :rtype: str
        """
        if (self.step >= len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS) - 1):
            if (self.request.user.has_confirmed_email):
                self.request.user.speedy_match_profile.validate_profile_and_activate()
                if (self.request.user.speedy_match_profile.is_active):
                    return reverse_lazy(viewname='matches:list')
                else:
                    return reverse_lazy(viewname='accounts:activate', kwargs={'step': self.request.user.speedy_match_profile.activation_step})
            else:
                return reverse_lazy(viewname='accounts:edit_profile_emails')
        else:
            return reverse_lazy(viewname='accounts:activate', kwargs={'step': self.step + 1})

    def form_valid(self, form):
        """
        Handles a valid form submission: saves the form, activates the account and displays a welcome message when the profile becomes fully active (disabling Speedy Match for an unmatchable height), displays the "not allowed" message if the profile was rejected, and redirects to the success URL.

        :param form: The validated form.
        :return: A redirect response to the success URL.
        """
        super().form_valid(form=form)
        success_url = self.get_success_url()
        if (self.request.user.speedy_match_profile.is_active):
            self.display_welcome_message()
            site = Site.objects.get_current()
            language_code = get_language()
            logger.info('User {user} activated their account on {site_name} (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                site_name=_(site.name),
                user=self.request.user,
                registered_days_ago=(now() - self.request.user.date_created).days,
                language_code=language_code,
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
    """
    View for editing Speedy Match notification preferences, using the Speedy Match specific notifications form.
    """
    form_class = ProfileNotificationsForm


