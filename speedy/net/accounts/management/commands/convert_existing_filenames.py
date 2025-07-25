import logging
import os

from django.core.management import BaseCommand

from speedy.core.uploads.models import File

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A Django management command to convert existing filenames in the database.

    This command iterates over all files in the database, generates new filenames
    for them, and renames the files on the filesystem accordingly.

    Methods:
        handle(*args, **options): Main entry point for the command. Processes all files.
    """

    def handle(self, *args, **options):
        """
        Main entry point for the command. Processes all files.

        This method retrieves all files from the database, generates new filenames,
        and renames the files on the filesystem. If the renaming is successful, the
        file record is updated in the database.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        files = File.objects.all().order_by('date_created')
        for file in files:
            old_path = file.file.path
            new_filename = file.file.field.generate_filename(file, file.file.name)
            file.file.name = new_filename
            new_path = file.file.path
            if (old_path == new_path):
                logger.debug('convert_existing_filenames::Skipped renaming file {id}.'.format(id=file.id))
            else:
                logger.debug('convert_existing_filenames::Renaming file {id} from {old_path} to {new_path}.'.format(
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
                    # logger.info('convert_existing_filenames::Deleting file={file}, path={path}.'.format(
                    #     file=file,
                    #     path=old_path,
                    # ))
                    # file.delete()


