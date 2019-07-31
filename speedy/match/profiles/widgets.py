from django.utils.translation import gettext_lazy as _

from speedy.core.profiles.widgets import Widget
from speedy.core.accounts.models import User
from speedy.match.accounts import validators
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class UserRankWidget(Widget):
    template_name = 'profiles/user_rank_widget.html'
    permission_required = 'accounts.view_profile_rank'


class UserOnSpeedyMatchWidget(Widget):
    template_name = 'profiles/user_on_speedy_match_widget.html'
    permission_required = 'accounts.view_profile_info'

    def is_match(self):
        if (not (self.viewer.is_authenticated)):
            return False
        if (self.viewer == self.user):
            return False
        return self.user.speedy_match_profile.get_matching_rank(other_profile=self.viewer.speedy_match_profile) > SpeedyMatchSiteProfile.RANK_0

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
        diet = self.user.get_diet() if (validators.diet_is_valid(diet=diet_code)) else str(_("Unknown"))

        smoking_status_code = self.user.smoking_status
        smoking_status_list = [str(choice[1]) for choice in User.SMOKING_STATUS_CHOICES_WITH_DEFAULT if (choice[0] == smoking_status_code)]
        smoking_status = smoking_status_list[0] if (len(smoking_status_list) == 1) else str(_("Unknown"))

        relationship_status_code = self.user.relationship_status
        relationship_status_list = [str(choice[1]) for choice in User.RELATIONSHIP_STATUS_CHOICES_WITH_DEFAULT if (choice[0] == relationship_status_code)]
        relationship_status = relationship_status_list[0] if (len(relationship_status_list) == 1) else str(_("Unknown"))

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


