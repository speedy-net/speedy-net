import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import ugettext_lazy as _
from rules.contrib.views import LoginRequiredMixin
from ..accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .forms import MatchSettingsMiniForm, MatchSettingsFullForm, AboutMeForm

log = logging.getLogger(__name__)


class MatchesListView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/match_list.html'
    form_class = MatchSettingsMiniForm
    success_url = reverse_lazy('matches:list')

    def get_matches(self):
        return SpeedyMatchSiteProfile.objects.get_matches(self.request.user.profile)

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches': self.get_matches(),
        })
        return cd


class EditMatchSettingsView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/settings/matches.html'
    form_class = MatchSettingsFullForm
    success_url = reverse_lazy('matches:list')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=_('Your match settings were saved.'))
        return response


class EditAboutMeView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/settings/about_me.html'
    form_class = AboutMeForm
    success_url = reverse_lazy('matches:list')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=_('Your match settings were saved.'))
        return response


