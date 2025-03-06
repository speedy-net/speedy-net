import logging
import os
from datetime import timedelta

from django.core.management import BaseCommand
from django.db.models import F, Q
from django.utils.timezone import now

from speedy.core.uploads.models import Image
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        images = Image.objects.filter(
            **{
                "owner__isnull": False,
                "owner__user__{}__last_visit__lt".format(SpeedyMatchSiteProfile.RELATED_NAME): now() - timedelta(days=540),
                "owner__user__{}__last_visit__lt".format(SpeedyNetSiteProfile.RELATED_NAME): now() - timedelta(days=540),
            }
        ).filter(
            (Q(owner__user__photo__isnull=True) | ~Q(owner__user__photo__pk=F('pk')))
        ).order_by('date_created')
        for image in images:
            if ((not (image.owner is None)) and (image.owner.user.speedy_match_profile.last_visit < now() - timedelta(days=540)) and (image.owner.user.speedy_net_profile.last_visit < now() - timedelta(days=540))):
                if ((image.owner.user.photo is None) or (not (image.owner.user.photo.pk == image.pk))):
                    logger.debug('remove_unused_images_of_users_who_didnt_visit_both_sites_in_18_months::Removing image {id} from ({image_path}).'.format(
                        id=image.id,
                        image_path=image.file.path,
                    ))
                    try:
                        try:
                            os.remove(image.file.path)
                        except FileNotFoundError as e:
                            logger.debug('remove_unused_images_of_users_who_didnt_visit_both_sites_in_18_months::image={image}, FileNotFoundError Exception={e}'.format(
                                image=image,
                                e=str(e),
                            ))
                        image.delete()
                    except Exception as e:
                        logger.error('remove_unused_images_of_users_who_didnt_visit_both_sites_in_18_months::image={image}, Exception={e}'.format(
                            image=image,
                            e=str(e),
                        ))


