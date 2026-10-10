"""
Widgets for the friends app of Speedy Core, which define the UserFriendsWidget.
"""
import random

from speedy.core.profiles.widgets import Widget


class UserFriendsWidget(Widget):
    """
    Widget that displays a random sample of a user's friends.

    Attributes:
        template_name (str): The template used to render the widget.

    Methods:
        get_random_friends(self, count): Returns up to ``count`` random friends of the user, without repetition.
        get_context_data(self): Returns the context data for rendering the widget, including the random friends.
    """
    template_name = 'friends/user_friends_widget.html'

    def get_random_friends(self, count):
        """
        Select <count> random friends from the list of user's friends, without repetition.
        If there are less than <count> friends, return all of them in random order.

        :param count: The maximum number of random friends to select.
        :type count: int
        :return: A list of up to <count> random friends, in random order.
        :rtype: list
        """
        user_friends = self.user.site_friends
        friends_to_return = min(len(user_friends), count)
        random_friends = random.sample(user_friends, friends_to_return)
        return random_friends

    def get_context_data(self):
        """
        Return the context data for rendering the widget, including 6 random friends of the user.

        :return: The context data for the widget.
        :rtype: dict
        """
        cd = super().get_context_data()
        cd.update({
            'friends': self.get_random_friends(count=6),
        })
        return cd


