from speedy.core.accounts.forms import ProfilePrivacyForm as BaseProfilePrivacyForm
from .models import SiteProfile


class ProfilePrivacyForm(BaseProfilePrivacyForm):

    class Meta(BaseProfilePrivacyForm.Meta):
        model = SiteProfile
        fields = ('access_dob_day_month', 'access_dob_year')
