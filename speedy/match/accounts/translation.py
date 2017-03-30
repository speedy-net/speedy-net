from modeltranslation.translator import TranslationOptions, register
from .models import SiteProfile


@register(SiteProfile)
class SiteProfileOptions(TranslationOptions):

    fields = ('children', 'more_children', 'profile_description', 'city', 'match_description')
