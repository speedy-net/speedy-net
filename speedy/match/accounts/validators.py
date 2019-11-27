import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string

from speedy.core.base.utils import string_is_not_empty
from speedy.core.accounts.models import User
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from speedy.core.uploads.models import Image

logger = logging.getLogger(__name__)


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


def relationship_status_is_valid(relationship_status):
    return ((relationship_status is not None) and (int(relationship_status) in User.RELATIONSHIP_STATUS_VALID_VALUES))


def rank_is_valid(rank):
    return (rank in SpeedyMatchSiteProfile.RANK_VALID_VALUES)


def validate_photo(photo):
    if (not (photo)):
        raise ValidationError(_("A profile picture is required."))


def validate_photo_for_user(user, photo):
    validate_photo(photo=photo)
    user._photo = user.photo
    photo_is_valid = False
    try:
        user_image = Image(owner=user, file=photo)
        user_image.save()
        user.photo = user_image
        profile_picture_html = render_to_string(template_name="accounts/tests/profile_picture_test.html", context={"user": user})
        logger.debug('validate_photo_for_user::user={user}, profile_picture_html={profile_picture_html}'.format(
            user=user,
            profile_picture_html=profile_picture_html,
        ))
        if (not ('speedy-core/images/user.svg' in profile_picture_html)):
            photo_is_valid = True
    except Exception:
        photo_is_valid = False
    user.photo = user._photo
    try:
        user_image.delete()
    except Exception:
        pass
    if (not (photo_is_valid)):
        raise ValidationError(_("You can't use this format for your profile picture. Only JPEG or PNG formats are accepted."))


def validate_profile_description(profile_description):
    if (not (string_is_not_empty(profile_description))):
        raise ValidationError(_("Please write a few words about yourself."))


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
        raise ValidationError(_("Who is your ideal partner?"))


def validate_height(height):
    if (not (height_is_valid(height=height))):
        raise ValidationError(_("Height must be from 1 to 450 cm."))


def validate_diet(diet):
    if (not (diet_is_valid(diet=diet))):
        raise ValidationError(_("Your diet is required."))


def validate_smoking_status(smoking_status):
    if (not (smoking_status_is_valid(smoking_status=smoking_status))):
        raise ValidationError(_("Your smoking status is required."))


def validate_relationship_status(relationship_status):
    if (not (relationship_status_is_valid(relationship_status=relationship_status))):
        raise ValidationError(_("Your relationship status is required."))


def validate_gender_to_match(gender_to_match):
    if (not ((gender_to_match is not None) and (len(gender_to_match) > 0) and (len(gender_to_match) == len(set(gender_to_match))) and (all(gender_is_valid(gender=gender) for gender in gender_to_match)))):
        raise ValidationError(_("Gender to match is required."))


def validate_min_age_to_match(min_age_to_match):
    if (not (age_match_is_valid(age_match=min_age_to_match))):
        raise ValidationError(_("Minimal age to match must be from 0 to 180 years."))


def validate_max_age_to_match(max_age_to_match):
    if (not (age_match_is_valid(age_match=max_age_to_match))):
        raise ValidationError(_("Maximal age to match must be from 0 to 180 years."))


def validate_min_max_age_to_match(min_age_to_match, max_age_to_match):
    if ((age_match_is_valid(age_match=min_age_to_match)) and (age_match_is_valid(age_match=max_age_to_match))):
        if (not (min_age_to_match <= max_age_to_match)):
            raise ValidationError(_("Maximal age to match can't be less than minimal age to match."))


def validate_diet_match(diet_match):
    if (not ((set(diet_match.keys()) == {str(diet) for diet in User.DIET_VALID_VALUES}) and (all([((str(diet) in diet_match) and (rank_is_valid(rank=diet_match[str(diet)]))) for diet in User.DIET_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Diet match is required."))
    if (not (max([diet_match[str(diet)] for diet in User.DIET_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one diet match option should be five hearts."))


def validate_smoking_status_match(smoking_status_match):
    if (not ((set(smoking_status_match.keys()) == {str(smoking_status) for smoking_status in User.SMOKING_STATUS_VALID_VALUES}) and (all([((str(smoking_status) in smoking_status_match) and (rank_is_valid(rank=smoking_status_match[str(smoking_status)]))) for smoking_status in User.SMOKING_STATUS_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Smoking status match is required."))
    if (not (max([smoking_status_match[str(smoking_status)] for smoking_status in User.SMOKING_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one smoking status match option should be five hearts."))


def validate_relationship_status_match(relationship_status_match):
    if (not ((set(relationship_status_match.keys()) == {str(relationship_status) for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES}) and (all([((str(relationship_status) in relationship_status_match) and (rank_is_valid(rank=relationship_status_match[str(relationship_status)]))) for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Relationship status match is required."))
    if (not (max([relationship_status_match[str(relationship_status)] for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one relationship status match option should be five hearts."))


