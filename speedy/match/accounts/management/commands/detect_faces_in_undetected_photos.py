import logging
import boto3
from datetime import timedelta
from PIL import Image
from sorl.thumbnail import get_thumbnail

from django.core.management import BaseCommand
from django.utils.timezone import now
from django.template.loader import render_to_string

from speedy.core.accounts.models import User
from speedy.core.base.utils import is_animated, is_transparent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.active(
            photo__visible_on_website=True,
            photo__aws_facial_analysis_time=None,
            photo__date_created__lte=(now() - timedelta(minutes=5)),
            speedy_match_site_profile__active_languages__len__gt=0,
        ).distinct(
        ).order_by('photo__date_created')[:36]
        for user in users:
            if (len(user.speedy_match_profile.active_languages) > 0):
                image = user.photo
                if ((image is not None) and (image.visible_on_website) and (image.aws_facial_analysis_time is None) and (image.date_created <= (now() - timedelta(minutes=5)))):
                    photo_is_valid = False
                    faces_detected = 0
                    try:
                        profile_picture_html = render_to_string(template_name="accounts/tests/profile_picture_test_640.html", context={"user": user})
                        logger.debug('detect_faces_in_undetected_photos::user={user}, profile_picture_html={profile_picture_html}'.format(
                            user=user,
                            profile_picture_html=profile_picture_html,
                        ))
                        if (not ('speedy-core/images/user.svg' in profile_picture_html)):
                            with image.file, Image.open(image.file) as _image:
                                if (is_animated(image=_image)):
                                    photo_is_valid = False
                                    logger.error("detect_faces_in_undetected_photos::image is animated. user={user} (registered {registered_days_ago} days ago).".format(
                                        user=user,
                                        registered_days_ago=(now() - user.date_created).days,
                                    ))
                                elif (is_transparent(image=_image)):
                                    photo_is_valid = False
                                    logger.error("detect_faces_in_undetected_photos::image is transparent. user={user} (registered {registered_days_ago} days ago).".format(
                                        user=user,
                                        registered_days_ago=(now() - user.date_created).days,
                                    ))
                                else:
                                    photo_is_valid = True
                                    logger.debug("detect_faces_in_undetected_photos::photo is valid. user={user} (registered {registered_days_ago} days ago).".format(
                                        user=user,
                                        registered_days_ago=(now() - user.date_created).days,
                                    ))
                        else:
                            logger.error("detect_faces_in_undetected_photos::thumbnail failed. user={user} (registered {registered_days_ago} days ago).".format(
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                        if (photo_is_valid):
                            client = boto3.client('rekognition')
                            thumbnail = get_thumbnail(image.file, '640', crop='center 20%')  # Open the image of width 640px from profile_picture_test_640.html
                            image.aws_raw_facial_analysis_results = client.detect_faces(Image={'Bytes': thumbnail.read()}, Attributes=['ALL'])
                            for detected_face in image.aws_raw_facial_analysis_results['FaceDetails']:
                                if (detected_face["Confidence"] >= 99.0):
                                    if ((detected_face["AgeRange"]["Low"] >= 2) and (detected_face["AgeRange"]["High"] >= 8)):
                                        faces_detected += 1
                            image.number_of_faces = faces_detected
                            if (faces_detected >= 1):
                                user.speedy_match_profile.profile_picture_months_offset = 0
                            else:
                                user.speedy_match_profile.profile_picture_months_offset = 5
                            logger.debug("detect_faces_in_undetected_photos::{faces_detected} faces detected. user={user} (registered {registered_days_ago} days ago).".format(
                                faces_detected=faces_detected,
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                            image.aws_facial_analysis_time = now()
                            user.speedy_match_profile.save()
                            image.save()

                    except Exception as e:
                        logger.error('detect_faces_in_undetected_photos::user={user}, Exception={e} (registered {registered_days_ago} days ago)'.format(
                            user=user,
                            e=str(e),
                            registered_days_ago=(now() - user.date_created).days,
                        ))


