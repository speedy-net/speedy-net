from django.conf import settings as django_settings
from django import template

from speedy.core.base.utils import to_attribute

register = template.Library()


def attribute_html(profile, attribute_name, default_value):
    """
    Builds a human-readable string showing the per-language values of a multilingual attribute that differ from the default value.

    :param profile: Required. The profile instance to read the attribute from.
    :param attribute_name: Required. The base name of the multilingual attribute.
    :type attribute_name: str
    :param default_value: Required. The default value; languages whose value equals this are omitted.
    :return: A string listing the non-default language values, or "(none)" if there are none.
    :rtype: str
    """
    attribute_list = []
    for language_code, language_name in django_settings.LANGUAGES:
        attribute_lang = getattr(profile, to_attribute(name=attribute_name, language_code=language_code), None)
        if ((not (attribute_lang is None)) and (not (attribute_lang == default_value))):
            attribute_list.append("'{}':{}".format(language_code, attribute_lang))
    if (len(attribute_list) > 0):
        return "({})".format(", ".join(attribute_list))
    else:
        return "(none)"


@register.filter
def activation_step_html(speedy_match_profile):
    """
    Builds a human-readable string showing the per-language values of the Speedy Match profile's "activation_step" attribute, for use in the admin.

    :param speedy_match_profile: Required. The Speedy Match profile instance.
    :return: A string listing the non-default language values, or "(none)" if there are none.
    :rtype: str
    """
    return attribute_html(profile=speedy_match_profile, attribute_name="activation_step", default_value=2)


@register.filter
def number_of_matches_html(speedy_match_profile):
    """
    Builds a human-readable string showing the per-language values of the Speedy Match profile's "number_of_matches" attribute, for use in the admin.

    :param speedy_match_profile: Required. The Speedy Match profile instance.
    :return: A string listing the non-default language values, or "(none)" if there are none.
    :rtype: str
    """
    return attribute_html(profile=speedy_match_profile, attribute_name="number_of_matches", default_value=None)


