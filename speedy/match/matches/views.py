from django.views import generic
from rules.contrib.views import LoginRequiredMixin
from speedy.core.accounts.models import User
from speedy.core.base.utils import get_age_ranges_match


class MatchesListView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'matches/matches_list.html'

    def get_matches(self):
        user_profile = self.request.user.profile
        age_ranges = get_age_ranges_match(self.request.user.profile.min_age_match, self.request.user.profile.max_age_match)
        qs = User.objects.active(gender__in=user_profile.gender_to_match, date_of_birth__range=age_ranges).exclude(pk=self.request.user.pk)

        qs = [user for user in qs if self.request.user.profile.matching_function(other_profile=user.profile)]

        qs = sorted(qs, key=lambda user: (user.profile.rank, user.profile.last_visit), reverse=True)
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'matches': self.get_matches(),
        })
        return cd
