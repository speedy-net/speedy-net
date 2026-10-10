"""
Validators of the Speedy Match accounts app for the profile fields (height, age to match, gender, diet, smoking status, relationship status, rank, city, children and descriptions).
"""
import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from speedy.core.base.utils import string_is_not_empty
from speedy.core.accounts.models import User
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

logger = logging.getLogger(__name__)


def height_is_valid(height):
    """
    Checks whether a height value is a valid Speedy Match height.

    :param height: The height value in centimeters.
    :type height: int or None
    :return: True if the height is valid, False otherwise.
    :rtype: bool
    """
    return ((height is not None) and (height in SpeedyMatchSiteProfile.HEIGHT_VALID_VALUES))


def age_to_match_is_valid(age_to_match):
    """
    Checks whether an age-to-match value is valid.

    :param age_to_match: The age value.
    :type age_to_match: int
    :return: True if the age is valid, False otherwise.
    :rtype: bool
    """
    return (age_to_match in SpeedyMatchSiteProfile.AGE_TO_MATCH_VALID_VALUES)


def gender_is_valid(gender):
    """
    Checks whether a gender value is one of the valid User genders.

    :param gender: The gender value.
    :type gender: int or str
    :return: True if the gender is valid, False otherwise.
    :rtype: bool
    """
    return (int(gender) in User.GENDER_VALID_VALUES)


def diet_is_valid(diet):
    """
    Checks whether a diet value is valid.

    :param diet: The diet value.
    :type diet: int or str or None
    :return: True if the diet is valid, False otherwise.
    :rtype: bool
    """
    return ((diet is not None) and (int(diet) in User.DIET_VALID_VALUES))


def smoking_status_is_valid(smoking_status):
    """
    Checks whether a smoking status value is valid.

    :param smoking_status: The smoking status value.
    :type smoking_status: int or str or None
    :return: True if the smoking status is valid, False otherwise.
    :rtype: bool
    """
    return ((smoking_status is not None) and (int(smoking_status) in User.SMOKING_STATUS_VALID_VALUES))


def relationship_status_is_valid(relationship_status):
    """
    Checks whether a relationship status value is valid.

    :param relationship_status: The relationship status value.
    :type relationship_status: int or str or None
    :return: True if the relationship status is valid, False otherwise.
    :rtype: bool
    """
    return ((relationship_status is not None) and (int(relationship_status) in User.RELATIONSHIP_STATUS_VALID_VALUES))


def rank_is_valid(rank):
    """
    Checks whether a rank value is a valid Speedy Match rank.

    :param rank: The rank value.
    :type rank: int
    :return: True if the rank is valid, False otherwise.
    :rtype: bool
    """
    return (rank in SpeedyMatchSiteProfile.RANK_VALID_VALUES)


def validate_profile_description(profile_description):
    """
    Validates that the profile description is not empty.

    :param profile_description: The profile description text.
    :type profile_description: str
    :raises django.core.exceptions.ValidationError: If the profile description is empty.
    """
    if (not (string_is_not_empty(s=profile_description))):
        raise ValidationError(_("Please write a few words about yourself."))


def validate_city(city):
    """
    Validates that the city is not empty.

    :param city: The city name.
    :type city: str
    :raises django.core.exceptions.ValidationError: If the city is empty.
    """
    if (not (string_is_not_empty(s=city))):
        raise ValidationError(_("Please write where you live."))


def validate_children(children):
    """
    Validates that the children field is not empty.

    :param children: The children description.
    :type children: str
    :raises django.core.exceptions.ValidationError: If the children field is empty.
    """
    if (not (string_is_not_empty(s=children))):
        raise ValidationError(_("Do you have children? How many?"))


def validate_more_children(more_children):
    """
    Validates that the more-children field is not empty.

    :param more_children: The more-children description.
    :type more_children: str
    :raises django.core.exceptions.ValidationError: If the more-children field is empty.
    """
    if (not (string_is_not_empty(s=more_children))):
        raise ValidationError(_("Do you want (more) children?"))


def validate_match_description(match_description):
    """
    Validates that the match description is not empty.

    :param match_description: The match description text.
    :type match_description: str
    :raises django.core.exceptions.ValidationError: If the match description is empty.
    """
    if (not (string_is_not_empty(s=match_description))):
        raise ValidationError(_("Who is your ideal partner?"))


def validate_height(height):
    """
    Validates that the height is valid.

    :param height: The height value in centimeters.
    :type height: int or None
    :raises django.core.exceptions.ValidationError: If the height is not valid.
    """
    if (not (height_is_valid(height=height))):
        raise ValidationError(_("Height must be from 1 to 450 cm."))


def validate_diet(diet):
    """
    Validates that the diet is valid.

    :param diet: The diet value.
    :type diet: int or str or None
    :raises django.core.exceptions.ValidationError: If the diet is not valid.
    """
    if (not (diet_is_valid(diet=diet))):
        raise ValidationError(_("Your diet is required."))


def validate_smoking_status(smoking_status):
    """
    Validates that the smoking status is valid.

    :param smoking_status: The smoking status value.
    :type smoking_status: int or str or None
    :raises django.core.exceptions.ValidationError: If the smoking status is not valid.
    """
    if (not (smoking_status_is_valid(smoking_status=smoking_status))):
        raise ValidationError(_("Your smoking status is required."))


def validate_relationship_status(relationship_status):
    """
    Validates that the relationship status is valid.

    :param relationship_status: The relationship status value.
    :type relationship_status: int or str or None
    :raises django.core.exceptions.ValidationError: If the relationship status is not valid.
    """
    if (not (relationship_status_is_valid(relationship_status=relationship_status))):
        raise ValidationError(_("Your relationship status is required."))


def validate_gender_to_match(gender_to_match):
    """
    Validates that the gender-to-match list is non-empty, contains no duplicates, and only valid genders.

    :param gender_to_match: The list of genders to match.
    :type gender_to_match: list
    :raises django.core.exceptions.ValidationError: If the gender-to-match list is not valid.
    """
    if (not ((gender_to_match is not None) and (len(gender_to_match) > 0) and (len(gender_to_match) == len(set(gender_to_match))) and (all(gender_is_valid(gender=gender) for gender in gender_to_match)))):
        raise ValidationError(_("Gender to match is required."))


def validate_min_age_to_match(min_age_to_match):
    """
    Validates that the minimal age to match is valid.

    :param min_age_to_match: The minimal age to match.
    :type min_age_to_match: int
    :raises django.core.exceptions.ValidationError: If the minimal age to match is not valid.
    """
    if (not (age_to_match_is_valid(age_to_match=min_age_to_match))):
        raise ValidationError(_("Minimal age to match must be from 0 to 180 years."))


def validate_max_age_to_match(max_age_to_match):
    """
    Validates that the maximal age to match is valid.

    :param max_age_to_match: The maximal age to match.
    :type max_age_to_match: int
    :raises django.core.exceptions.ValidationError: If the maximal age to match is not valid.
    """
    if (not (age_to_match_is_valid(age_to_match=max_age_to_match))):
        raise ValidationError(_("Maximal age to match must be from 0 to 180 years."))


def validate_min_max_age_to_match(min_age_to_match, max_age_to_match):
    """
    Validates that the minimal age to match is not greater than the maximal age to match, when both are individually valid.

    :param min_age_to_match: The minimal age to match.
    :type min_age_to_match: int
    :param max_age_to_match: The maximal age to match.
    :type max_age_to_match: int
    :raises django.core.exceptions.ValidationError: If the minimal age to match is greater than the maximal age to match.
    """
    if ((age_to_match_is_valid(age_to_match=min_age_to_match)) and (age_to_match_is_valid(age_to_match=max_age_to_match))):
        if (not (min_age_to_match <= max_age_to_match)):
            raise ValidationError(_("Maximal age to match can't be less than minimal age to match."))


def validate_diet_match(diet_match):
    """
    Validates the diet match dict, ensuring it covers every valid diet value with a valid rank, and that at least one option is ranked five hearts.

    :param diet_match: A mapping of diet value (as string) to rank.
    :type diet_match: dict
    :raises django.core.exceptions.ValidationError: If the diet match dict is incomplete, invalid, or has no five-heart option.
    """
    if (not ((set(diet_match.keys()) == {str(diet) for diet in User.DIET_VALID_VALUES}) and (all([((str(diet) in diet_match) and (rank_is_valid(rank=diet_match[str(diet)]))) for diet in User.DIET_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Diet match is required."))
    if (not (max([diet_match[str(diet)] for diet in User.DIET_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one diet match option should be five hearts."))


def validate_smoking_status_match(smoking_status_match):
    """
    Validates the smoking status match dict, ensuring it covers every valid smoking status with a valid rank, and that at least one option is ranked five hearts.

    :param smoking_status_match: A mapping of smoking status value (as string) to rank.
    :type smoking_status_match: dict
    :raises django.core.exceptions.ValidationError: If the smoking status match dict is incomplete, invalid, or has no five-heart option.
    """
    if (not ((set(smoking_status_match.keys()) == {str(smoking_status) for smoking_status in User.SMOKING_STATUS_VALID_VALUES}) and (all([((str(smoking_status) in smoking_status_match) and (rank_is_valid(rank=smoking_status_match[str(smoking_status)]))) for smoking_status in User.SMOKING_STATUS_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Smoking status match is required."))
    if (not (max([smoking_status_match[str(smoking_status)] for smoking_status in User.SMOKING_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one smoking status match option should be five hearts."))


def validate_relationship_status_match(relationship_status_match):
    """
    Validates the relationship status match dict, ensuring it covers every valid relationship status with a valid rank, and that at least one option is ranked five hearts.

    :param relationship_status_match: A mapping of relationship status value (as string) to rank.
    :type relationship_status_match: dict
    :raises django.core.exceptions.ValidationError: If the relationship status match dict is incomplete, invalid, or has no five-heart option.
    """
    if (not ((set(relationship_status_match.keys()) == {str(relationship_status) for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES}) and (all([((str(relationship_status) in relationship_status_match) and (rank_is_valid(rank=relationship_status_match[str(relationship_status)]))) for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES])))):
        # This may be due to values added later.
        raise ValidationError(_("Relationship status match is required."))
    if (not (max([relationship_status_match[str(relationship_status)] for relationship_status in User.RELATIONSHIP_STATUS_VALID_VALUES]) == SpeedyMatchSiteProfile.RANK_5)):
        raise ValidationError(_("At least one relationship status match option should be five hearts."))


