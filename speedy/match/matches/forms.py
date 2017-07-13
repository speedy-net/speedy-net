from django import forms

from speedy.match.accounts.forms import SpeedyMatchProfileActivationForm
from speedy.match.accounts.models import SiteProfile


class MatchSettingsMiniForm(SpeedyMatchProfileActivationForm):
    zzz= forms.CharField()

    def get_fields(self):
        return ('diet_match', 'min_age_match', 'max_age_match')
