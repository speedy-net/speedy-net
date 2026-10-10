"""
Profile widgets of Speedy Match - the user rank widget, the Speedy Match profile widget and the extra details widget.
"""
import logging

from django.utils.translation import gettext_lazy as _

from speedy.core.profiles.widgets import Widget
from speedy.core.accounts.models import User
from speedy.match.accounts import validators as speedy_match_accounts_validators
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

logger = logging.getLogger(__name__)


class UserRankWidget(Widget):
    """
    Profile widget displaying the matching rank (hearts) between the viewer and the viewed user.
    """
    template_name = 'profiles/user_rank_widget.html'
    permission_required = 'accounts.view_profile_rank'


class UserOnSpeedyMatchWidget(Widget):
    """
    Profile widget displayed on Speedy Net showing a link/preview to the viewed user's Speedy Match profile, when the viewer and user are a match.

    Methods:
        is_match(self): Checks whether the viewer and the viewed user are considered a match.
        get_context_data(self): Adds the match status to the widget's context.
    """
    template_name = 'profiles/user_on_speedy_match_widget.html'
    permission_required = 'accounts.view_user_on_speedy_match_widget'

    def is_match(self):
        """
        Checks whether the viewer and the viewed user are a Speedy Match match. Should always be true, since this widget is not displayed otherwise; logs an error if not.

        :return: True if the viewer and user are a match (or the viewer is a staff superuser), False otherwise.
        :rtype: bool
        """
        # Should be always true. This widget should not be displayed if false.
        if (self.viewer.is_authenticated):
            if ((self.viewer.is_staff) and (self.viewer.is_superuser)):
                return True
        if (not (self.viewer.is_authenticated)):
            is_match = False
        elif (self.viewer == self.user):
            is_match = False
        else:
            is_match = (self.viewer.speedy_match_profile.get_matching_rank(other_profile=self.user.speedy_match_profile) > SpeedyMatchSiteProfile.RANK_0)
        if (not (is_match is True)):
            logger.error('UserOnSpeedyMatchWidget::get inside "if (not (is_match is True)):", is_match={is_match}, self.viewer={viewer}, self.user={user}'.format(is_match=is_match, viewer=self.viewer, user=self.user))
        return is_match

    def get_context_data(self):
        """
        Adds the match status to the widget's template context.

        :return: The context data.
        :rtype: dict
        """
        cd = super().get_context_data()
        cd.update({
            'is_match': self.is_match(),
        })
        return cd


class UserExtraDetailsWidget(Widget):
    """
    Profile widget showing extra Speedy Match details about the viewed user (diet, smoking status, relationship status, genders to match).

    Methods:
        get_context_data(self): Adds the formatted extra details to the widget's context.
    """
    template_name = 'profiles/user_extra_info_widget.html'
    permission_required = 'accounts.view_profile_info'

    def get_context_data(self):
        """
        Adds the formatted diet, smoking status, relationship status and genders-to-match text to the widget's template context.

        :return: The context data.
        :rtype: dict
        """
        cd = super().get_context_data()

        diet_code = self.user.diet
        diet = self.user.get_diet() if (speedy_match_accounts_validators.diet_is_valid(diet=diet_code)) else str(_("Unknown"))

        smoking_status_code = self.user.smoking_status
        smoking_status = self.user.get_smoking_status() if (speedy_match_accounts_validators.smoking_status_is_valid(smoking_status=smoking_status_code)) else str(_("Unknown"))

        relationship_status_code = self.user.relationship_status
        relationship_status = self.user.get_relationship_status() if (speedy_match_accounts_validators.relationship_status_is_valid(relationship_status=relationship_status_code)) else str(_("Unknown"))

        gender_codes = self.user.speedy_match_profile.gender_to_match
        genders_to_match_list = [str(choice[1]) for choice in User.GENDER_CHOICES if (choice[0] in gender_codes)]
        if (len(genders_to_match_list) == 0):
            genders_to_match_list.append(str(_("None")))
        genders_to_match = ", ".join(genders_to_match_list)

        cd.update({
            'diet': diet,
            'smoking_status': smoking_status,
            'relationship_status': relationship_status,
            'gender_to_match': genders_to_match,
        })
        return cd


