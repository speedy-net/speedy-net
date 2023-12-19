from django.conf import settings as django_settings
from django import template

from speedy.core.base.utils import to_attribute

register = template.Library()


def attribute_html(profile, attribute_name, default_value):
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
    return attribute_html(profile=speedy_match_profile, attribute_name="activation_step", default_value=2)


@register.filter
def number_of_matches_html(speedy_match_profile):
    return attribute_html(profile=speedy_match_profile, attribute_name="number_of_matches", default_value=None)


@register.filter
def number_of_friends_html(speedy_net_profile):
    return attribute_html(profile=speedy_net_profile, attribute_name="number_of_friends", default_value=None)


