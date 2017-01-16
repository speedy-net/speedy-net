from speedy.core.profiles.widgets import Widget


class UserFriendsWidget(Widget):
    template_name = 'friends/user_friends_widget.html'

    def get_random_friends(self, count):
        return self.entity.friends.order_by('?')[:count]

    def get_context_data(self):
        cd = super().get_context_data()
        cd.update({
            'friends': self.get_random_friends(6)
        })
        return cd
