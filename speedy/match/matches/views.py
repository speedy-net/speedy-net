import logging

from django.urls import reverse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import LoginRequiredMixin

from speedy.core.base.views import PaginationMixin
from speedy.match.accounts import utils
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .forms import SpeedyMatchSettingsMiniForm, SpeedyMatchProfileFullMatchForm, SpeedyMatchProfileFullAboutMeForm

logger = logging.getLogger(__name__)


class MatchesListView(LoginRequiredMixin, PaginationMixin, generic.UpdateView):
    template_name = 'matches/match_list.html'
    page_size = 24
    paginate_by = page_size
    form_class = SpeedyMatchSettingsMiniForm
    success_url = reverse_lazy('matches:list')

    def dispatch(self, request, *args, **kwargs):
        if (request.method == 'POST'):
            return redirect(to='matches:edit_match_settings')
        return super().dispatch(request=request, *args, **kwargs)

    def redirect_on_exception(self):
        return redirect(to='matches:list')

    def get_matches_list(self):
        if (self.request.user.is_authenticated):
            matches_list = SpeedyMatchSiteProfile.objects.get_matches(user=self.request.user)
        else:
            matches_list = []
        return matches_list

    def get_object_list(self):
        if (self.request.method == 'POST'):
            return []
        else:
            return self.get_matches_list()

    def get_object(self, queryset=None):
        return self.request.user.speedy_match_profile

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches_list': self.page.object_list,
            'total_number_of_active_members_text': utils.get_total_number_of_active_members_text(),
        })
        return cd


class MatchSettingsDefaultRedirectView(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('matches:edit_match_settings')


class EditMatchSettingsView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'matches/settings/about_my_match.html'
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


