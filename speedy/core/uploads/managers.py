from speedy.core.base.managers import BaseManager


class FileManager(BaseManager):
    def get_queryset(self):
        from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
        from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
        return super().get_queryset().prefetch_related('owner', 'owner__user', "owner__user__{}".format(SpeedyNetSiteProfile.RELATED_NAME), "owner__user__{}".format(SpeedyMatchSiteProfile.RELATED_NAME), 'owner__user__photo')


class ImageManager(FileManager):
    pass


