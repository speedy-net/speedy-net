import logging
import os

from django.core.management import BaseCommand

from speedy.core.uploads.models import Image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        images = Image.objects.filter(
            owner__isnull=True,
        ).order_by('date_created')
        for image in images:
            if (image.owner is None):
                logger.debug('remove_images_with_no_owner::Removing image {id} from ({image_path}).'.format(
                    id=image.id,
                    image_path=image.file.path,
                ))
                try:
                    try:
                        os.remove(image.file.path)
                    except FileNotFoundError as e:
                        logger.debug('remove_images_with_no_owner::image={image}, FileNotFoundError Exception={e}'.format(
                            image=image,
                            e=str(e),
                        ))
                    image.delete()
                except Exception as e:
                    logger.error('remove_images_with_no_owner::image={image}, Exception={e}'.format(
                        image=image,
                        e=str(e),
                    ))
            else:
                logger.error("remove_images_with_no_owner::Can't remove image {id} (owner={owner}).".format(
                    id=image.id,
                    owner=image.owner,
                ))


