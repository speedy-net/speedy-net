from django import template

from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

register = template.Library()


@register.filter
def rank_description(rank):
    return SpeedyMatchSiteProfile.get_rank_description(rank)


