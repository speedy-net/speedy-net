from django.utils.translation import ugettext_lazy as _

from speedy.core.profiles.widgets import Widget
from speedy.core.accounts.models import User
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class UserRankWidget(Widget):
    template_name = 'profiles/user_rank_widget.html'
    permission_required = 'accounts.view_profile_info'


class UserOnSpeedyMatchWidget(Widget):
    template_name = 'profiles/user_on_speedy_match_widget.html'
    permission_required = 'accounts.view_profile_info'

    def get_entity_speedy_match_profile(self):
        return self.entity.get_profile(model=SpeedyMatchSiteProfile)

    def get_viewer_speedy_match_profile(self):
        if (not (self.viewer.is_authenticated)):
            return None
        return self.viewer.get_profile(model=SpeedyMatchSiteProfile)

    def is_match(self):
        if (not (self.viewer.is_authenticated)):
            return False
        if (self.viewer == self.entity):
            return False
        return self.get_entity_speedy_match_profile().get_matching_rank(other_profile=self.get_viewer_speedy_match_profile()) > SpeedyMatchSiteProfile.RANK_0

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

        # diet = _("Unknown")
        diet_code = self.entity.diet
        diet_list = [choice[1] for choice in User.DIET_CHOICES_WITH_DEFAULT if (choice[0] == diet_code)]
        diet = diet_list[0] if (len(diet_list) == 1) else _("Unknown")
        # for choice in User.DIET_CHOICES_WITH_DEFAULT:
        #     if (choice[0] == diet_code):
        #         diet = choice[1]

        # smoking_status = _("Unknown")
        smoking_status_code = self.entity.profile.smoking_status
        smoking_status_list = [choice[1] for choice in SpeedyMatchSiteProfile.SMOKING_STATUS_CHOICES_WITH_DEFAULT if (choice[0] == smoking_status_code)]
        smoking_status = smoking_status_list[0] if (len(smoking_status_list) == 1) else _("Unknown")
        # for choice in SpeedyMatchSiteProfile.SMOKING_STATUS_CHOICES_WITH_DEFAULT:
        #     if (choice[0] == smoking_status_code):
        #         smoking_status = choice[1]

        # marital_status = _("Unknown")
        marital_status_code = self.entity.profile.marital_status
        marital_status_list = [choice[1] for choice in SpeedyMatchSiteProfile.MARITAL_STATUS_CHOICES_WITH_DEFAULT if (choice[0] == marital_status_code)]
        marital_status = marital_status_list[0] if (len(marital_status_list) == 1) else _("Unknown")
        # for choice in SpeedyMatchSiteProfile.MARITAL_STATUS_CHOICES_WITH_DEFAULT:
        #     if (choice[0] == marital_status_code):
        #         marital_status = choice[1]

        # genders_to_match = []
        gender_codes = self.entity.profile.gender_to_match
        genders_to_match_list = [choice[1] for choice in User.GENDER_CHOICES if (choice[0] in gender_codes)]
        if (len(genders_to_match_list) == 0):
            genders_to_match_list.append(_("None"))
        genders_to_match = ", ".join(genders_to_match_list)
        # for choice in User.GENDER_CHOICES:
        #     if (choice[0] in gender_codes):
        #         genders_to_match.append(str(choice[1]))

        cd.update({
            'diet': diet,
            'smoking_status': smoking_status,
            'marital_status': marital_status,
            'gender_to_match': genders_to_match,
        })
        return cd
