import logging

from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rules.contrib.views import LoginRequiredMixin

from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .forms import SpeedyMatchSettingsMiniForm, SpeedyMatchProfileFullMatchForm, SpeedyMatchProfileFullAboutMeForm

logger = logging.getLogger(__name__)


class MatchesListView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/match_list.html'
    page_size = 24
    paginate_by = page_size
    form_class = SpeedyMatchSettingsMiniForm
    success_url = reverse_lazy('matches:list')

    def dispatch(self, request, *args, **kwargs):
        if (self.request.user.is_authenticated):
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(self.request.user.speedy_match_profile)
            page_number = self.request.GET.get('page', 1)
            paginator = Paginator(matches_list, self.page_size)
            try:
                page = paginator.page(page_number)
            except (PageNotAnInteger, EmptyPage):
                return redirect(to='matches:list')
            self.paginator = paginator
            self.page = page
        return super().dispatch(request=request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user.speedy_match_profile

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'paginator': self.paginator,
            'page_obj': self.page,
            'is_paginated': self.page.has_other_pages(),
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


