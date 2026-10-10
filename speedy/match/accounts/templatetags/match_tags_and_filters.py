from django import template

from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

register = template.Library()


@register.filter
def rank_description(rank):
    """
    Template filter returning the human-readable description of a match rank.

    :param rank: The numeric match rank value.
    :type rank: int
    :return: The description of the rank.
    :rtype: str
    """
    return SpeedyMatchSiteProfile.get_rank_description(rank)


