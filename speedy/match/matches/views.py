import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rules.contrib.views import LoginRequiredMixin

from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .forms import SpeedyMatchSettingsMiniForm, SpeedyMatchProfileFullMatchForm, SpeedyMatchProfileFullAboutMeForm

logger = logging.getLogger(__name__)


class MatchesListView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/match_list.html'
    paginate_by = 3 ##
    form_class = SpeedyMatchSettingsMiniForm
    success_url = reverse_lazy('matches:list')

    def get_matches(self):
        matches_list = SpeedyMatchSiteProfile.objects.get_matches(self.request.user.speedy_match_profile)
        page = self.request.GET.get('page', 1)

        self.paginator = Paginator(matches_list, self.paginate_by)
        try:
            matches_list = self.paginator.page(page)
        except PageNotAnInteger:
            matches_list = self.paginator.page(1)
        except EmptyPage:
            matches_list = self.paginator.page(self.paginator.num_pages)
        return matches_list
        # return SpeedyMatchSiteProfile.objects.get_matches(self.request.user.speedy_match_profile)[:60] # ~~~~ TODO: We need pagination.
        # return SpeedyMatchSiteProfile.objects.get_matches(self.request.user.speedy_match_profile)[:3] # ~~~~ TODO: We need pagination.

    def get_object(self, queryset=None):
        return self.request.user.speedy_match_profile

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        matches_list = self.get_matches()
        cd.update({
            'matches_list': matches_list,
            'paginator': self.paginator,
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


