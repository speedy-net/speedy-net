"""
Profile widgets of Speedy Net. Defines the widget showing the Speedy Net profile of a user.
"""
import logging

from speedy.core.profiles.widgets import Widget
from speedy.core.blocks.models import Block

logger = logging.getLogger(__name__)


class UserOnSpeedyNetWidget(Widget):
    """
    Profile widget shown on other Speedy sites (e.g. Speedy Match) indicating whether the user is active on Speedy Net.

    Attributes:
        template_name (str): The template used to render this widget.
        permission_required (str): The permission required to view this widget.

    Methods:
        is_active_and_there_is_no_block(self): Checks whether the profile user is active on Speedy Net and not blocked by the viewer.
        get_context_data(self): Returns the template context data for this widget.
    """
    template_name = 'profiles/user_on_speedy_net_widget.html'
    permission_required = 'accounts.view_user_on_speedy_net_widget'

    def is_active_and_there_is_no_block(self):
        """
        Checks whether the profile user is active on Speedy Net and not blocked by the viewer.

        :return: True if the profile user is active on Speedy Net and there is no block between the viewer and the user, False otherwise.
        :rtype: bool
        """
        # Should be always true. This widget should not be displayed if false.
        if (self.viewer.is_authenticated):
            if ((self.viewer.is_staff) and (self.viewer.is_superuser)):
                return True
        if (not (self.viewer.is_authenticated)):
            is_active_and_there_is_no_block = False  # This widget appears only for authenticated users on Speedy Match.
        else:
            is_active_and_there_is_no_block = ((self.user.speedy_net_profile.is_active) and (not (Block.objects.there_is_block(entity_1=self.viewer, entity_2=self.user))))
        if (not (is_active_and_there_is_no_block is True)):
            logger.error('UserOnSpeedyNetWidget::get inside "if (not (is_active_and_there_is_no_block is True)):", is_active_and_there_is_no_block={is_active_and_there_is_no_block}, self.viewer={viewer}, self.user={user}'.format(is_active_and_there_is_no_block=is_active_and_there_is_no_block, viewer=self.viewer, user=self.user))
        return is_active_and_there_is_no_block

    def get_context_data(self):
        """
        Returns the template context data for this widget.

        :return: A dictionary of context data including whether the user is active and not blocked.
        :rtype: dict
        """
        cd = super().get_context_data()
        cd.update({
            'is_active_and_there_is_no_block': self.is_active_and_there_is_no_block(),
        })
        return cd


