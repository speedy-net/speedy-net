from speedy.core.profiles.widgets import Widget


class UserOnSpeedyNetWidget(Widget):
    template_name = 'profiles/user_on_speedy_net_widget.html'
    permission_required = 'accounts.view_profile_header'

