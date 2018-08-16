from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
# from django.conf import settings

from speedy.core.accounts.models import User
from .models import SiteProfile as SpeedyMatchSiteProfile


def height_is_valid(height):
    return ((height is not None) and (height in SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES))


def age_is_valid(age):
    return (age in SpeedyMatchSiteProfile.AGE_VALID_VALUES)


def gender_is_valid(gender):
    return (int(gender) in User.GENDER_VALID_VALUES)


def diet_is_valid(diet):
    return ((diet is not None) and (int(diet) in User.DIET_VALID_VALUES))


def smoking_status_is_valid(smoking_status):
    return ((smoking_status is not None) and (int(smoking_status) in SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES))


def marital_status_is_valid(marital_status):
    return ((marital_status is not None) and (int(marital_status) in SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES))


def rank_is_valid(rank):
    return (rank in SpeedyMatchSiteProfile.RANK_VALID_VALUES)


def validate_photo(photo):
    if not photo:
        raise ValidationError(_("A profile picture is required."))


def validate_profile_description(profile_description):
    if not ((profile_description is not None) and (len(profile_description) > 0)):
        raise ValidationError(_("Please write some text in this field."))


def validate_city(city):
    if not ((city is not None) and (len(city) > 0)):
        raise ValidationError(_("Please write where you live."))


def validate_children(children):
    if not ((children is not None) and (len(children) > 0)):
        raise ValidationError(_("Do you have children? How many?"))


def validate_more_children(more_children):
    if not ((more_children is not None) and (len(more_children) > 0)):
        raise ValidationError(_("Do you want (more) children?"))


def validate_match_description(match_description):
    if not ((match_description is not None) and (len(match_description) > 0)):
        raise ValidationError(_("Please write some text in this field."))


def validate_height(height):
    if not (height_is_valid(height=height)):
        raise ValidationError(_("Height must be from 1 to 450 cm."))


def validate_diet(diet):
    # ~~~~ TODO: assert that diet is in DIET_VALID_CHOICES (and smoking status and marital_status)
    # ~~~~ TODO: instead of range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)]), define a list in the model and create a test to assert that the list is equal to the range.
    # if not ((diet is not None) and (User.DIET_UNKNOWN < int(diet) < User.DIET_MAX_VALUE_PLUS_ONE)):
    if not (diet_is_valid(diet=diet)):
        raise ValidationError(_("Your diet is required."))


def validate_smoking_status(smoking_status):
    # from .models import SiteProfile as SpeedyMatchSiteProfile
    # if not ((smoking_status is not None) and (SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN < int(smoking_status) < SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE)):
    if not (smoking_status_is_valid(smoking_status=smoking_status)):
        raise ValidationError(_("Your smoking status is required."))


def validate_marital_status(marital_status):
    # from .models import SiteProfile as SpeedyMatchSiteProfile
    # if not ((marital_status is not None) and (SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN < int(marital_status) < SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)):
    if not (marital_status_is_valid(marital_status=marital_status)):
        raise ValidationError(_("Your marital status is required."))


def validate_gender_to_match(gender_to_match):
    # if not ((gender_to_match is not None) and (len(gender_to_match) > 0) and (all((User.GENDER_UNKNOWN < gender < User.GENDER_MAX_VALUE_PLUS_ONE) for gender in gender_to_match))):
    if not ((gender_to_match is not None) and (len(gender_to_match) > 0) and (len(gender_to_match) == len(set(gender_to_match))) and (all(gender_is_valid(gender=gender) for gender in gender_to_match))):
        raise ValidationError(_("Gender to match is required."))


def validate_min_age_match(min_age_match):
    if not (age_is_valid(age=min_age_match)):
        raise ValidationError(_("Minimal age to match must be from 0 to 180 years."))


def validate_max_age_match(max_age_match):
    if not (age_is_valid(age=max_age_match)):
        raise ValidationError(_("Maximal age to match must be from 0 to 180 years."))


def validate_min_max_age_to_match(min_age_match, max_age_match):
    if ((age_is_valid(age=min_age_match)) and (age_is_valid(age=max_age_match))):
        if not (min_age_match <= max_age_match):
            raise ValidationError(_("Maximal age to match can't be less than minimal age to match."))


def validate_diet_match(diet_match):
    # from .models import SiteProfile as SpeedyMatchSiteProfile
    # if not (all([((str(diet) in diet_match) and (SpeedyMatchSiteProfile.RANK_0 <= diet_match[str(diet)] <= SpeedyMatchSiteProfile.RANK_5)) for diet in range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)])):
    if not (all([((str(diet) in diet_match) and (rank_is_valid(rank=diet_match[str(diet)]))) for diet in User.DIET_VALID_VALUES])):
        # This may be due to values added later.
        raise ValidationError(_("Please select diet match."))
    # if not (max([diet_match[str(diet)] for diet in range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)]) == SpeedyMatchSiteProfile.RANK_5):
    if not (max([diet_match[str(diet)] for diet in User.DIET_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5):
        raise ValidationError(_("At least one diet match option should be 5 hearts."))


def validate_smoking_status_match(smoking_status_match):
    # from .models import SiteProfile as SpeedyMatchSiteProfile
    # if not (all([((str(smoking_status) in smoking_status_match) and (SpeedyMatchSiteProfile.RANK_0 <= smoking_status_match[str(smoking_status)] <= SpeedyMatchSiteProfile.RANK_5)) for smoking_status in range(SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE)])):
    if not (all([((str(smoking_status) in smoking_status_match) and (rank_is_valid(rank=smoking_status_match[str(smoking_status)]))) for smoking_status in SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES])):
        # This may be due to values added later.
        raise ValidationError(_("Please select smoking status match."))
    # if not (max([smoking_status_match[str(smoking_status)] for smoking_status in range(SpeedyMatchSiteProfile.SMOKING_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.SMOKING_STATUS_MAX_VALUE_PLUS_ONE)]) == SpeedyMatchSiteProfile.RANK_5):
    if not (max([smoking_status_match[str(smoking_status)] for smoking_status in SpeedyMatchSiteProfile.SMOKING_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5):
        raise ValidationError(_("At least one smoking status match option should be 5 hearts."))


def validate_marital_status_match(marital_status_match):
    # from .models import SiteProfile as SpeedyMatchSiteProfile
    # if not (all([((str(marital_status) in marital_status_match) and (SpeedyMatchSiteProfile.RANK_0 <= marital_status_match[str(marital_status)] <= SpeedyMatchSiteProfile.RANK_5)) for marital_status in range(SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)])):
    if not (all([((str(marital_status) in marital_status_match) and (rank_is_valid(rank=marital_status_match[str(marital_status)]))) for marital_status in SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES])):
        # This may be due to values added later.
        raise ValidationError( _("Please select marital status match."))
    # elif not (max([marital_status_match[str(marital_status)] for marital_status in range(SpeedyMatchSiteProfile.MARITAL_STATUS_UNKNOWN + 1, SpeedyMatchSiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)]) == SpeedyMatchSiteProfile.RANK_5):
    elif not (max([marital_status_match[str(marital_status)] for marital_status in SpeedyMatchSiteProfile.MARITAL_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5):
        raise ValidationError(_("At least one marital status match option should be 5 hearts."))


