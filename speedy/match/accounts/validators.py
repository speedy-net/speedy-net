from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from speedy.core.accounts.models import User
from django.conf import settings


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
    if not(height is not None and (1 <= height <= 450)):
        raise ValidationError(_("Height must be from 1 to 450 cm."))


def validate_diet(diet):
    if not (diet is not None and (User.DIET_UNKNOWN < int(diet) < User.DIET_MAX_VALUE_PLUS_ONE)):
        raise ValidationError(_("Your diet is required."))


def validate_smoking(smoking):
    from .models import SiteProfile
    if not (smoking is not None and (SiteProfile.SMOKING_UNKNOWN < smoking < SiteProfile.SMOKING_MAX_VALUE_PLUS_ONE)):
        raise ValidationError(_("Your smoking status is required."))


def validate_marital_status(marital_status):
    from .models import SiteProfile
    if not (SiteProfile.MARITAL_STATUS_UNKNOWN < marital_status < SiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE):
        raise ValidationError(_("Your marital status is required."))


def validate_gender_to_match(gender_to_match):
    if not ((len(gender_to_match) > 0) and (all((User.GENDER_UNKNOWN <= gender < User.GENDER_MAX_VALUE_PLUS_ONE) for gender in gender_to_match))):
        raise ValidationError(_("Gender to match is required."))


def validate_min_age_match(min_age_match):
    if not (settings.MIN_AGE_ALLOWED <= min_age_match <= settings.MAX_AGE_ALLOWED):
        raise ValidationError(_("Minimal age to match must be from 0 to 180 years."))


def validate_max_age_match(max_age_match):
    if not (settings.MIN_AGE_ALLOWED <= max_age_match <= settings.MAX_AGE_ALLOWED):
        raise ValidationError(_("Maximal age to match must be from 0 to 180 years."))


def validate_diet_match(diet_match):
    from .models import SiteProfile
    if not (all([((str(diet) in diet_match) and (SiteProfile.RANK_0 <= diet_match[str(diet)] <= SiteProfile.RANK_5)) for diet in range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)])):
        # This may be due to values added later.
        raise ValidationError(_("Please select diet match."))
    if not (max([diet_match[str(diet)] for diet in range(User.DIET_UNKNOWN + 1, User.DIET_MAX_VALUE_PLUS_ONE)]) == SiteProfile.RANK_5):
        raise ValidationError(_("At least one diet match option should be 5 hearts."))


def validate_smoking_match(smoking_match):
    from .models import SiteProfile
    if not (all([((str(smoking) in smoking_match) and (SiteProfile.RANK_0 <= smoking_match[str(smoking)] <= SiteProfile.RANK_5)) for smoking in range(SiteProfile.SMOKING_UNKNOWN + 1, SiteProfile.SMOKING_MAX_VALUE_PLUS_ONE)])):
        # This may be due to values added later.
        raise ValidationError(_("Please select smoking status match."))
    if not (max([smoking_match[str(smoking)] for smoking in range(SiteProfile.SMOKING_UNKNOWN + 1, SiteProfile.SMOKING_MAX_VALUE_PLUS_ONE)]) == SiteProfile.RANK_5):
        raise ValidationError(_("At least one smoking status match option should be 5 hearts."))


def validate_marital_status_match(marital_status_match):
    from .models import SiteProfile
    if not (all([((str(marital_status) in marital_status_match) and (SiteProfile.RANK_0 <= marital_status_match[str(marital_status)] <= SiteProfile.RANK_5)) for marital_status in range(SiteProfile.MARITAL_STATUS_UNKNOWN + 1, SiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)])):
        # This may be due to values added later.
        raise ValidationError( _("Please select marital status match."))
    elif not (max([marital_status_match[str(marital_status)] for marital_status in range(SiteProfile.MARITAL_STATUS_UNKNOWN + 1, SiteProfile.MARITAL_STATUS_MAX_VALUE_PLUS_ONE)]) == SiteProfile.RANK_5):
        raise ValidationError(_("At least one marital status match option should be 5 hearts."))


def validate_min_max_age_to_match(min_age_match, max_age_match):
    if not (min_age_match <= max_age_match):
        raise ValidationError(_("Maximal age to match can't be less than minimal age to match."))
