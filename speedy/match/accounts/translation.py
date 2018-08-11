from modeltranslation.translator import TranslationOptions, register
from .models import SiteProfile as SpeedyMatchSiteProfile


@register(SpeedyMatchSiteProfile)
class SiteProfileOptions(TranslationOptions):
    fields = ('profile_description', 'city', 'children', 'more_children', 'match_description')


