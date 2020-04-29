from datetime import timedelta

from django.utils.translation import get_language, gettext_lazy as _
from django.utils.timezone import now

from speedy.core.base.utils import to_attribute
from speedy.core.accounts.models import User
from speedy.core.accounts import validators as speedy_core_accounts_validators
from speedy.match.accounts import validators as speedy_match_accounts_validators
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


def get_steps_range():
    return range(1, len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))


def get_step_form_fields(step):
    form_fields = []
    for field_name in list(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS[step]):
        if (not (field_name in (User.LOCALIZABLE_FIELDS + SpeedyMatchSiteProfile.LOCALIZABLE_FIELDS))):
            form_fields.append(field_name)
        else:
            form_fields.append(to_attribute(name=field_name))
    return form_fields


def get_step_fields_to_validate(step):
    fields = get_step_form_fields(step=step)
    if (('min_age_to_match' in fields) or ('max_age_to_match' in fields)):
        fields.append('min_max_age_to_match')
    return fields


def validate_field(field_name, user):
    if (field_name in ['photo']):
        speedy_core_accounts_validators.validate_photo(photo=user.photo)
    elif (field_name in ['profile_description', to_attribute(name='profile_description')]):
        speedy_match_accounts_validators.validate_profile_description(profile_description=user.speedy_match_profile.profile_description)
    elif (field_name in ['city', to_attribute(name='city')]):
        speedy_match_accounts_validators.validate_city(city=user.city)
    elif (field_name in ['children', to_attribute(name='children')]):
        speedy_match_accounts_validators.validate_children(children=user.speedy_match_profile.children)
    elif (field_name in ['more_children', to_attribute(name='more_children')]):
        speedy_match_accounts_validators.validate_more_children(more_children=user.speedy_match_profile.more_children)
    elif (field_name in ['match_description', to_attribute(name='match_description')]):
        speedy_match_accounts_validators.validate_match_description(match_description=user.speedy_match_profile.match_description)
    elif (field_name in ['height']):
        speedy_match_accounts_validators.validate_height(height=user.speedy_match_profile.height)
    elif (field_name in ['diet']):
        speedy_match_accounts_validators.validate_diet(diet=user.diet)
    elif (field_name in ['smoking_status']):
        speedy_match_accounts_validators.validate_smoking_status(smoking_status=user.smoking_status)
    elif (field_name in ['relationship_status']):
        speedy_match_accounts_validators.validate_relationship_status(relationship_status=user.relationship_status)
    elif (field_name in ['gender_to_match']):
        speedy_match_accounts_validators.validate_gender_to_match(gender_to_match=user.speedy_match_profile.gender_to_match)
    elif (field_name in ['min_age_to_match']):
        speedy_match_accounts_validators.validate_min_age_to_match(min_age_to_match=user.speedy_match_profile.min_age_to_match)
    elif (field_name in ['max_age_to_match']):
        speedy_match_accounts_validators.validate_max_age_to_match(max_age_to_match=user.speedy_match_profile.max_age_to_match)
    elif (field_name in ['min_max_age_to_match']):
        speedy_match_accounts_validators.validate_min_max_age_to_match(min_age_to_match=user.speedy_match_profile.min_age_to_match, max_age_to_match=user.speedy_match_profile.max_age_to_match)
    elif (field_name in ['diet_match']):
        speedy_match_accounts_validators.validate_diet_match(diet_match=user.speedy_match_profile.diet_match)
    elif (field_name in ['smoking_status_match']):
        speedy_match_accounts_validators.validate_smoking_status_match(smoking_status_match=user.speedy_match_profile.smoking_status_match)
    elif (field_name in ['relationship_status_match']):
        speedy_match_accounts_validators.validate_relationship_status_match(relationship_status_match=user.speedy_match_profile.relationship_status_match)
    else:
        raise Exception("Unexpected: field_name={}".format(field_name))


def get_total_number_of_active_members_text():
    language_code = get_language()
    total_number_of_active_members_in_the_last_four_months = User.objects.active(
        speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
        speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
        speedy_match_site_profile__active_languages__contains=[language_code],
        speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
    ).count()
    total_number_of_active_members_in_the_last_week = User.objects.active(
        speedy_match_site_profile__height__range=(SpeedyMatchSiteProfile.settings.MIN_HEIGHT_TO_MATCH, SpeedyMatchSiteProfile.settings.MAX_HEIGHT_TO_MATCH),
        speedy_match_site_profile__not_allowed_to_use_speedy_match=False,
        speedy_match_site_profile__active_languages__contains=[language_code],
        speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
    ).count()
    # We only display this information on the website if the numbers are at least 300 and 50.
    if ((total_number_of_active_members_in_the_last_four_months >= 300) and (total_number_of_active_members_in_the_last_week >= 50)):
        total_number_of_active_members_text = _("The total number of active members on the site is {total_number_of_active_members_in_the_last_four_months}, of which {total_number_of_active_members_in_the_last_week} members entered the site in the last week.").format(
            total_number_of_active_members_in_the_last_four_months='{:,}'.format(total_number_of_active_members_in_the_last_four_months),
            total_number_of_active_members_in_the_last_week='{:,}'.format(total_number_of_active_members_in_the_last_week),
        )
    else:
        total_number_of_active_members_text = ""
    return total_number_of_active_members_text


