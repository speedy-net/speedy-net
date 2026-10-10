"""
Views for the Speedy Match matches app - the matches list view and the views to edit the match settings and the about me details.
"""
import logging

from django.urls import reverse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import redirect
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import LoginRequiredMixin

from speedy.core.base.views import PaginationMixin
from speedy.match.accounts import utils
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .forms import SpeedyMatchSettingsMiniForm, SpeedyMatchProfileFullMatchForm, SpeedyMatchProfileFullAboutMeForm

logger = logging.getLogger(__name__)


class MatchesListView(LoginRequiredMixin, PaginationMixin, generic.UpdateView):
    """
    Displays the authenticated user's list of matches along with an inline mini settings form.

    Methods:
        dispatch(self, request, *args, **kwargs): Redirects POST requests to the match settings edit view.
        redirect_on_exception(self): Returns a redirect to the matches list on exception.
        get_matches_list(self): Returns the list of matches for the authenticated user.
        get_object_list(self): Returns the object list for pagination, empty for POST requests.
        get_object(self, queryset=None): Returns the requesting user's Speedy Match site profile.
        get_context_data(self, **kwargs): Adds the matches list, active-members text, and conversion-tracking flag to the context.
    """
    template_name = 'matches/match_list.html'
    page_size = 24
    paginate_by = page_size
    form_class = SpeedyMatchSettingsMiniForm
    success_url = reverse_lazy(viewname='matches:list')

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects POST requests to the dedicated match settings edit view, otherwise dispatches normally.

        :param request: The HTTP request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: An HTTP response.
        """
        if (request.method == 'POST'):
            return redirect(to='matches:edit_match_settings')
        return super().dispatch(request=request, *args, **kwargs)

    def redirect_on_exception(self):
        """
        Returns a redirect response to the matches list, used when an exception occurs while rendering.

        :return: A redirect response to the matches list.
        """
        return redirect(to='matches:list')

    def get_matches_list(self):
        """
        Returns the list of matches for the authenticated user, or an empty list if not authenticated.

        :return: The list of matching users.
        :rtype: list
        """
        if (self.request.user.is_authenticated):
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.request.user)
        else:
            matches_list = []
        return matches_list

    def get_object_list(self):
        """
        Returns the object list used for pagination - empty for POST requests, otherwise the matches list.

        :return: The list of objects to paginate.
        :rtype: list
        """
        if (self.request.method == 'POST'):
            return []
        else:
            return self.get_matches_list()

    def get_object(self, queryset=None):
        """
        Returns the requesting user's Speedy Match site profile, used as the form's instance.

        :param queryset: An optional queryset (unused).
        :return: The requesting user's Speedy Match site profile.
        :rtype: speedy.match.accounts.models.SiteProfile
        """
        return self.request.user.speedy_match_profile

    def get_context_data(self, **kwargs):
        """
        Adds the matches list, active-members statistics text, and the conversion-tracking flag to the template context.

        :param kwargs: Additional keyword arguments.
        :return: The context data.
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
            'matches_list': self.page.object_list,
            'total_number_of_active_members_text': utils.get_total_number_of_active_members_text(),
            'include_in_conversions': include_in_conversions,
        })
        return cd


class MatchSettingsDefaultRedirectView(LoginRequiredMixin, generic.RedirectView):
    """
    Redirects to the match settings edit view.

    Methods:
        get_redirect_url(self, *args, **kwargs): Returns the URL of the match settings edit view.
    """

    def get_redirect_url(self, *args, **kwargs):
        """
        Returns the URL of the match settings edit view.

        :param args: Positional arguments (unused).
        :param kwargs: Keyword arguments (unused).
        :return: The redirect URL.
        :rtype: str
        """
        return reverse(viewname='matches:edit_match_settings')


class EditMatchSettingsView(LoginRequiredMixin, generic.UpdateView):
    """
    View for editing the user's matching preferences (full settings page).

    Methods:
        get_object(self, queryset=None): Returns the requesting user's Speedy Match site profile.
        form_valid(self, form): Saves the form and displays a success message.
    """
    template_name = 'matches/settings/about_my_match.html'
    form_class = SpeedyMatchProfileFullMatchForm
    success_url = reverse_lazy(viewname='matches:list')

    def get_object(self, queryset=None):
        """
        Returns the requesting user's Speedy Match site profile, used as the form's instance.

        :param queryset: An optional queryset (unused).
        :return: The requesting user's Speedy Match site profile.
        :rtype: speedy.match.accounts.models.SiteProfile
        """
        return self.request.user.speedy_match_profile

    def form_valid(self, form):
        """
        Saves the valid form and displays a success message to the user.

        :param form: The validated form.
        :return: The HTTP response from the parent implementation.
        """
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=_('Your match settings were saved.'))
        return response


class EditAboutMeView(LoginRequiredMixin, generic.UpdateView):
    """
    View for editing the user's "about me" profile fields (full settings page).

    Methods:
        get_object(self, queryset=None): Returns the requesting user's Speedy Match site profile.
        form_valid(self, form): Saves the form and displays a success message.
    """
    template_name = 'matches/settings/about_me.html'
    form_class = SpeedyMatchProfileFullAboutMeForm
    success_url = reverse_lazy(viewname='matches:list')

    def get_object(self, queryset=None):
        """
        Returns the requesting user's Speedy Match site profile, used as the form's instance.

        :param queryset: An optional queryset (unused).
        :return: The requesting user's Speedy Match site profile.
        :rtype: speedy.match.accounts.models.SiteProfile
        """
        return self.request.user.speedy_match_profile

    def form_valid(self, form):
        """
        Saves the valid form and displays a success message to the user.

        :param form: The validated form.
        :return: The HTTP response from the parent implementation.
        """
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=_('Your match settings were saved.'))
        return response


