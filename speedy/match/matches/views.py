import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import LoginRequiredMixin

from speedy.core.base.views import PaginationMixin
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .forms import SpeedyMatchSettingsMiniForm, SpeedyMatchProfileFullMatchForm, SpeedyMatchProfileFullAboutMeForm

logger = logging.getLogger(__name__)


class MatchesListView(LoginRequiredMixin, PaginationMixin, generic.UpdateView):
    template_name = 'matches/match_list.html'
    page_size = 24
    paginate_by = page_size
    form_class = SpeedyMatchSettingsMiniForm
    success_url = reverse_lazy('matches:list')

    def get_matches_list(self):
        if (self.request.user.is_authenticated):
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(self.request.user.speedy_match_profile)
        else:
            matches_list = []
        return matches_list

    def get_object_list(self):
        return self.get_matches_list()

    def get_object(self, queryset=None):
        return self.request.user.speedy_match_profile

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches_list': self.page.object_list,
        })
        return cd


class EditMatchSettingsView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/settings/matches.html'
    form_class = SpeedyMatchProfileFullMatchForm
    success_url = reverse_lazy('matches:list')

    def get_object(self, queryset=None):
        return self.request.user.speedy_match_profile

    def form_valid(self, form):
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=_('Your match settings were saved.'))
        return response


class EditAboutMeView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/settings/about_me.html'
    form_class = SpeedyMatchProfileFullAboutMeForm
    success_url = reverse_lazy('matches:list')

    def get_object(self, queryset=None):
        return self.request.user.speedy_match_profile

    def form_valid(self, form):
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=_('Your match settings were saved.'))
        return response


