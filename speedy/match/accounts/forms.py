from speedy.net.accounts.forms import AccountPrivacyForm as NetAccountPrivacyForm

from .models import SiteProfile


class AccountPrivacyForm(NetAccountPrivacyForm):
    class Meta(NetAccountPrivacyForm.Meta):
        model = SiteProfile
        fields = ('public_email',)
