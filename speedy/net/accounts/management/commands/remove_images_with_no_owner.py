import logging
import os

from django.core.management import BaseCommand

from speedy.core.uploads.models import Image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        images = Image.objects.filter(owner=None).order_by('date_created')
        for image in images:
            if (image.owner is None):
                logger.info('remove_images_with_no_owner::Removing image {id} from ({image_path}).'.format(
                    id=image.id,
                    image_path=image.file.path,
                ))
                try:
                    os.remove(image.file.path)
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


