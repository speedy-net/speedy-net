import logging

from speedy.core.profiles.widgets import Widget
from speedy.core.blocks.models import Block

logger = logging.getLogger(__name__)


class UserOnSpeedyNetWidget(Widget):
    template_name = 'profiles/user_on_speedy_net_widget.html'
    permission_required = 'accounts.view_user_on_speedy_net_widget'

    def is_active_and_there_is_no_block(self):
        # Should be always true. This widget should not be displayed if false.
        if (self.viewer.is_authenticated):
            if ((self.viewer.is_staff) and (self.viewer.is_superuser)):
                return True
        if (not (self.viewer.is_authenticated)):
            is_active_and_there_is_no_block = False  # This widget appears only for authenticated users on Speedy Match.
        else:
            is_active_and_there_is_no_block = ((self.user.speedy_net_profile.is_active) and (not (Block.objects.there_is_block(user_1=self.viewer, user_2=self.user))))
        if (not (is_active_and_there_is_no_block is True)):
            logger.error('UserOnSpeedyNetWidget::get inside "if (not (is_active_and_there_is_no_block is True)):", is_active_and_there_is_no_block={is_active_and_there_is_no_block}, self.viewer={viewer}, self.user={user}'.format(is_active_and_there_is_no_block=is_active_and_there_is_no_block, viewer=self.viewer, user=self.user))
        return is_active_and_there_is_no_block

    def get_context_data(self):
        cd = super().get_context_data()
        cd.update({
            'is_active_and_there_is_no_block': self.is_active_and_there_is_no_block(),
        })
        return cd


