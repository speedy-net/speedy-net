from modeltranslation.translator import TranslationOptions, register
from .models import SiteProfile


@register(SiteProfile)
class SiteProfileOptions(TranslationOptions):
    fields = ('profile_description', 'city', 'children', 'more_children', 'match_description')


