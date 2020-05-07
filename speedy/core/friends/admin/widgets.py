from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.profiles.widgets import Widget


class AdminUserFriendsWidget(Widget):
    template_name = 'admin/friends/user_friends_widget.html'

    def get_context_data(self):
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

        cd = super().get_context_data()
        SiteProfile = get_site_profile_model()
        all_friends = list(self.user.friends.all().prefetch_related("from_user", "from_user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "from_user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'from_user__photo').distinct().order_by('-from_user__{}__last_visit'.format(SiteProfile.RELATED_NAME)))
        cd.update({
            'friends': all_friends[:30],
            'friends_count': len(all_friends),
        })
        return cd


