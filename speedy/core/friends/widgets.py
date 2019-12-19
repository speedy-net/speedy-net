import random

from speedy.core.profiles.widgets import Widget


class UserFriendsWidget(Widget):
    template_name = 'friends/user_friends_widget.html'

    def get_random_friends(self, count):
        """
        Select <count> random friends from the list of user's friends, without repetition.
        If there are less than <count> friends, return all of them in random order.
        """
        user_friends = self.user.all_friends
        friends_to_return = min(len(user_friends), count)
        random_friends = random.sample(user_friends, friends_to_return)
        return random_friends

    def get_context_data(self):
        cd = super().get_context_data()
        cd.update({
            'friends': self.get_random_friends(count=6)
        })
        return cd


