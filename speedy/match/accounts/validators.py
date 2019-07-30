from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from speedy.core.base.utils import string_is_not_empty
from speedy.core.accounts.models import User
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


def height_is_valid(height):
    return ((height is not None) and (height in SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES))


def age_match_is_valid(age_match):
    return (age_match in SpeedyMatchSiteProfile.AGE_MATCH_VALID_VALUES)


def gender_is_valid(gender):
    return (int(gender) in User.GENDER_VALID_VALUES)


def diet_is_valid(diet):
    return ((diet is not None) and (int(diet) in User.DIET_VALID_VALUES))


def smoking_status_is_valid(smoking_status):
    return ((smoking_status is not None) and (int(smoking_status) in User.SMOKING_STATUS_VALID_VALUES))


def marital_status_is_valid(marital_status):
    return ((marital_status is not None) and (int(marital_status) in User.MARITAL_STATUS_VALID_VALUES))


def rank_is_valid(rank):
    return (rank in SpeedyMatchSiteProfile.RANK_VALID_VALUES)


def validate_photo(photo):
    if (not (photo)):
        raise ValidationError(_("A profile picture is required."))


def validate_profile_description(profile_description):
    if (not (string_is_not_empty(profile_description))):
        raise ValidationError(_("Please write some text in this field."))


def validate_city(city):
    if (not (string_is_not_empty(city))):
        raise ValidationError(_("Please write where you live."))


def validate_children(children):
    if (not (string_is_not_empty(children))):
        raise ValidationError(_("Do you have children? How many?"))


def validate_more_children(more_children):
    if (not (string_is_not_empty(more_children))):
        raise ValidationError(_("Do you want (more) children?"))


def validate_match_description(match_description):
    if (not (string_is_not_empty(match_description))):
        raise ValidationError(_("Please write some text in this field."))


def validate_height(height):
    if (not (height_is_valid(height=height))):
        raise ValidationError(_("Height must be from 1 to 450 cm."))


def validate_diet(diet):
    if (not (diet_is_valid(diet=diet))):
        raise ValidationError(_("Your diet is required."))


def validate_smoking_status(smoking_status):
    if (not (smoking_status_is_valid(smoking_status=smoking_status))):
        raise ValidationError(_("Your smoking status is required."))


def validate_marital_status(marital_status):
    if (not (marital_status_is_valid(marital_status=marital_status))):
        raise ValidationError(_("Your marital status is required."))


def validate_gender_to_match(gender_to_match):
    if (not ((gender_to_match is not None) and (len(gender_to_match) > 0) and (len(gender_to_match) == len(set(gender_to_match))) and (all(gender_is_valid(gender=gender) for gender in gender_to_match)))):
        raise ValidationError(_("Gender to match is required."))


def validate_min_age_match(min_age_match):
    if (not (age_match_is_valid(age_match=min_age_match))):
        raise ValidationError(_("Minimal age to match must be from 0 to 180 years."))


def validate_max_age_match(max_age_match):
    if (not (age_match_is_valid(age_match=max_age_match))):
        raise ValidationError(_("Maximal age to match must be from 0 to 180 years."))


def validate_min_max_age_to_match(min_age_match, max_age_match):
    if ((age_match_is_valid(age_match=min_age_match)) and (age_match_is_valid(age_match=max_age_match))):
        if (not (min_age_match <= max_age_match)):
            raise ValidationError(_("Maximal age to match can't be less than minimal age to match."))


def validate_diet_match(diet_match):
    if (not ((set(diet_match.keys()) == {str(diet) for diet in User.DIET_VALID_VALUES}) and (all([((str(diet) in diet_match) and (rank_is_valid(rank=diet_match[str(diet)]))) for diet in User.DIET_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Please select di========et match."))
    if (not (max([diet_match[str(diet)] for diet in User.DIET_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one di========et match option should be 5 hearts."))


def validate_smoking_status_match(smoking_status_match):
    if (not ((set(smoking_status_match.keys()) == {str(smoking_status) for smoking_status in User.SMOKING_STATUS_VALID_VALUES}) and (all([((str(smoking_status) in smoking_status_match) and (rank_is_valid(rank=smoking_status_match[str(smoking_status)]))) for smoking_status in User.SMOKING_STATUS_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Please select sm======oking status match."))
    if (not (max([smoking_status_match[str(smoking_status)] for smoking_status in User.SMOKING_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one sm======oking status match option should be 5 hearts."))


def validate_marital_status_match(marital_status_match):
    if (not ((set(marital_status_match.keys()) == {str(marital_status) for marital_status in User.MARITAL_STATUS_VALID_VALUES}) and (all([((str(marital_status) in marital_status_match) and (rank_is_valid(rank=marital_status_match[str(marital_status)]))) for marital_status in User.MARITAL_STATUS_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Please select ma======rital status match."))
    if (not (max([marital_status_match[str(marital_status)] for marital_status in User.MARITAL_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one ma======rital status match option should be 5 hearts."))


