from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import get_language

from speedy.core.profiles.widgets import Widget


class UserOnSpeedyNetWidget(Widget):
    template_name = 'profiles/user_on_speedy_net_widget.html'
    permission_required = 'accounts.view_profile_header'

    def get_context_data(self):
        cd = super().get_context_data()
        language_code = get_language()
        SPEEDY_NET_SITE_ID = settings.SITE_PROFILES['net']['site_id']
        cd.update({
            'speedy_net_url': Site.objects.get(id=SPEEDY_NET_SITE_ID).domain,
            'LANGUAGE_CODE': language_code
        })
        return cd
