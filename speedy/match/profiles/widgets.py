import logging

from django.utils.translation import gettext_lazy as _

from speedy.core.profiles.widgets import Widget
from speedy.core.accounts.models import User
from speedy.match.accounts import validators as speedy_match_accounts_validators
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

logger = logging.getLogger(__name__)


class UserRankWidget(Widget):
    template_name = 'profiles/user_rank_widget.html'
    permission_required = 'accounts.view_profile_rank'


class UserOnSpeedyMatchWidget(Widget):
    template_name = 'profiles/user_on_speedy_match_widget.html'
    permission_required = 'accounts.view_user_on_speedy_match_widget'

    def is_match(self):
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
        cd = super().get_context_data()
        cd.update({
            'is_match': self.is_match(),
        })
        return cd


class UserExtraDetailsWidget(Widget):
    template_name = 'profiles/user_extra_info_widget.html'
    permission_required = 'accounts.view_profile_info'

    def get_context_data(self):
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


