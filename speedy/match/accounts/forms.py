from speedy.net.accounts.forms import ProfilePrivacyForm as NetAccountPrivacyForm

from .models import SiteProfile


class AccountPrivacyForm(NetAccountPrivacyForm):
    class Meta(NetAccountPrivacyForm.Meta):
        model = SiteProfile
        fields = ('access_dob_day_month', 'access_dob_year')
