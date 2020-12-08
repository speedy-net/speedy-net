import logging
import boto3

from django.core.management import BaseCommand
from django.utils.timezone import now
from django.template.loader import render_to_string

from speedy.core.uploads.models import Image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        images = Image.objects.filter(aws_image_moderation_time=None)
        for image in images:
            if (image.aws_image_moderation_time is None):
                photo_is_valid = False
                labels_detected = False
                try:
                    profile_picture_html = render_to_string(template_name="accounts/tests/profile_picture_test_640.html", context={"user": user})
                    logger.debug('moderate_unmoderated_photos::user={user}, profile_picture_html={profile_picture_html}'.format(
                        user=user,
                        profile_picture_html=profile_picture_html,
                    ))
                    if (not ('speedy-core/images/user.svg' in profile_picture_html)):
                        with Image.open(image) as _image:
                            if (getattr(_image, "is_animated", False)):
                                photo_is_valid = False
                            else:
                                photo_is_valid = True
                    if (photo_is_valid):
                        client = boto3.client('rekognition')
                        with open(photo, 'rb') as _image:  # open the image of width 640px
                            image.aws_raw_image_moderation_results = client.detect_labels(Image={'Bytes': _image.read()})
                        for label in image.aws_raw_image_moderation_results['Labels']:
                            if (label['Name'] in ["Explicit Nudity", "Sexual Activity", "Graphic Male Nudity", "Graphic Female Nudity", "Barechested Male"]):
                                labels_detected = True
                        if (labels_detected):
                            image.visible_on_website = False
                        else:
                            image.visible_on_website = True
                        image.aws_image_moderation_time = now()
                        image.save()

                except Exception as e:
                    photo_is_valid = False  ####
                    logger.error('moderate_unmoderated_photos::user={user}, Exception={e} (registered {registered_days_ago} days ago)'.format(
                        user=user,
                        e=str(e),
                        registered_days_ago=(now() - user.date_created).days,
                    ))


