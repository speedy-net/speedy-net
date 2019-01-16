from modeltranslation.translator import register, TranslationOptions
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


@register(SpeedyMatchSiteProfile)
class SpeedyMatchSiteProfileTranslationOptions(TranslationOptions):
    # fields = ('profile_description', 'city', 'children', 'more_children', 'match_description') # ~~~~ TODO: remove this line!
    fields = SpeedyMatchSiteProfile.LOCALIZABLE_FIELDS


