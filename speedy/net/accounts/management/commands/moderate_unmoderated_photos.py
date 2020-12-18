import logging
import boto3
from datetime import timedelta
from io import BytesIO
from PIL import Image

from django.core.management import BaseCommand
from django.utils.timezone import now
from django.template.loader import render_to_string

from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(
            photo__aws_image_moderation_time=None,
            photo__date_created__lte=(now() - timedelta(minutes=5)),
        ).distinct(
        ).order_by('photo__date_created')
        for user in users:
            image = user.photo
            if ((image.aws_image_moderation_time is None) and (image.date_created <= (now() - timedelta(minutes=5)))):
                photo_is_valid = False
                labels_detected = False
                labels_detected_list=[]
                try:
                    profile_picture_html = render_to_string(template_name="accounts/tests/profile_picture_test_640.html", context={"user": user})
                    logger.debug('moderate_unmoderated_photos::user={user}, profile_picture_html={profile_picture_html}'.format(
                        user=user,
                        profile_picture_html=profile_picture_html,
                    ))
                    if (not ('speedy-core/images/user.svg' in profile_picture_html)):
                        with Image.open(image.file) as _image:
                            if (getattr(_image, "is_animated", False)):
                                photo_is_valid = False
                            else:
                                photo_is_valid = True
                    if (photo_is_valid):
                        client = boto3.client('rekognition')
                        with Image.open(image.file) as _image:
                            _image = _image.resize((640, 640 * _image.height // _image.width))  # Resize the image to width 640px
                            _image_buffer = BytesIO()
                            _image.save(_image_buffer, format='PNG')
                            image.aws_raw_image_moderation_results = client.detect_moderation_labels(Image={'Bytes': _image_buffer.getvalue()})
                        for label in image.aws_raw_image_moderation_results["ModerationLabels"]:
                            if (label["Name"] in ["Explicit Nudity", "Sexual Activity", "Graphic Male Nudity", "Graphic Female Nudity", "Barechested Male"]):
                                labels_detected = True
                                labels_detected_list.append(label["Name"])
                        if (labels_detected):
                            image.visible_on_website = False
                            logger.warning("moderate_unmoderated_photos::labels detected. user={user}, labels detected={labels_detected_list}, registered {registered_days_ago} days ago).".format(
                                user=user,
                                labels_detected_list=labels_detected_list,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                        else:
                            image.visible_on_website = True
                            logger.debug("moderate_unmoderated_photos::labels not detected. user={user}, registered {registered_days_ago} days ago).".format(
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                        image.aws_image_moderation_time = now()
                        image.save()

                except Exception as e:
                    photo_is_valid = False  ####
                    logger.error('moderate_unmoderated_photos::user={user}, Exception={e} (registered {registered_days_ago} days ago)'.format(
                        user=user,
                        e=str(e),
                        registered_days_ago=(now() - user.date_created).days,
                    ))


