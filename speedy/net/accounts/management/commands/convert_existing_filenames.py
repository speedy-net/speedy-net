import logging
import os

from django.core.management import BaseCommand

from speedy.core.uploads.models import File

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        files = File.objects.all().order_by('date_created')
        for file in files:
            old_path = file.file.path
            new_filename = file.file.field.generate_filename(file, file.file.name)
            file.file.name = new_filename
            new_path = file.file.path
            if (old_path == new_path):
                logger.debug('convert_existing_filenames::Skipped renaming file {id}.'.format(id=file.id))
            else:
                logger.info('convert_existing_filenames::Renaming file {id} from {old_path} to {new_path}.'.format(
                    id=file.id,
                    old_path=old_path,
                    new_path=new_path,
                ))
                try:
                    os.rename(old_path, new_path)
                    file.save()
                except Exception as e:
                    logger.error('convert_existing_filenames::file={file}, Exception={e}'.format(
                        file=file,
                        e=str(e),
                    ))


