from speedy.core.profiles.widgets import Widget


class AdminUserFriendsWidget(Widget):
    template_name = 'admin/friends/user_friends_widget.html'

    def get_context_data(self):
        cd = super().get_context_data()
        cd.update({
            'friends': self.user.all_friends[:30]
        })
        return cd


