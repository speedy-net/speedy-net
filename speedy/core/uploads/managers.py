from speedy.core.base.managers import BaseManager


class FileManager(BaseManager):
    """
    Manager for the File model, prefetching related owner data for efficient queries.
    """
    def get_queryset(self):
        """
        Get the queryset of File instances, with the owner and the owner's site profiles and photo prefetched.

        :return: The queryset with related data prefetched.
        :rtype: django.db.models.QuerySet
        """
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
        return super().get_queryset().prefetch_related('owner', 'owner__user', "owner__user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "owner__user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'owner__user__photo')


class ImageManager(FileManager):
    """
    Manager for the Image model. Identical to FileManager.
    """
    pass


