import logging

import boto3
from datetime import timedelta
from PIL import Image
from sorl.thumbnail import get_thumbnail

from django.core.management import BaseCommand
from django.utils.timezone import now
from django.template.loader import render_to_string

from speedy.core.accounts.models import User
from speedy.core.base.utils import is_animated, is_transparent, looks_like_one_color

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(
            photo__aws_image_moderation_time=None,
            photo__date_created__lte=(now() - timedelta(minutes=5)),
        ).distinct(
        ).order_by('photo__date_created')[:36]
        for user in users:
            image = user.photo
            if ((image is not None) and (image.aws_image_moderation_time is None) and (image.date_created <= (now() - timedelta(minutes=5)))):
                photo_is_valid = False
                delete_this_photo = False
                delete_this_photo_reason = None
                labels_detected = False
                not_allowed_labels_detected = False
                labels_detected_list = []
                try:
                    profile_picture_html = render_to_string(template_name="accounts/tests/profile_picture_test_640.html", context={"user": user})
                    logger.debug('moderate_unmoderated_photos::user={user}, profile_picture_html={profile_picture_html}'.format(
                        user=user,
                        profile_picture_html=profile_picture_html,
                    ))
                    if (not ('speedy-core/images/user.svg' in profile_picture_html)):
                        with image.file, Image.open(image.file) as _image:
                            if (is_animated(image=_image)):
                                photo_is_valid = False
                                logger.error("moderate_unmoderated_photos::image is animated. user={user} (registered {registered_days_ago} days ago).".format(
                                    user=user,
                                    registered_days_ago=(now() - user.date_created).days,
                                ))
                            elif (is_transparent(image=_image)):
                                photo_is_valid = False
                                logger.error("moderate_unmoderated_photos::image is transparent. user={user} (registered {registered_days_ago} days ago).".format(
                                    user=user,
                                    registered_days_ago=(now() - user.date_created).days,
                                ))
                            elif (looks_like_one_color(image=_image, _user=user)):
                                photo_is_valid = False
                                delete_this_photo = True
                                delete_this_photo_reason = "image is one color only"
                                logger.error("moderate_unmoderated_photos::image is one color only. user={user} (registered {registered_days_ago} days ago).".format(
                                    user=user,
                                    registered_days_ago=(now() - user.date_created).days,
                                ))
                            else:
                                photo_is_valid = True
                                logger.debug("moderate_unmoderated_photos::photo is valid. user={user} (registered {registered_days_ago} days ago).".format(
                                    user=user,
                                    registered_days_ago=(now() - user.date_created).days,
                                ))
                    else:
                        logger.error("moderate_unmoderated_photos::thumbnail failed. user={user} (registered {registered_days_ago} days ago).".format(
                            user=user,
                            registered_days_ago=(now() - user.date_created).days,
                        ))
                    if (photo_is_valid):
                        client = boto3.client('rekognition')
                        thumbnail = get_thumbnail(image.file, '640', crop='center 20%')  # Open the image of width 640px from profile_picture_test_640.html
                        image.aws_raw_image_moderation_results = client.detect_moderation_labels(Image={'Bytes': thumbnail.read()}, MinConfidence=85)
                        for label in image.aws_raw_image_moderation_results["ModerationLabels"]:
                            if (label["Name"] in ["Explicit Nudity", "Sexual Activity", "Graphic Male Nudity", "Graphic Female Nudity", "Barechested Male", "Partial Nudity", "Male Swimwear Or Underwear", "Weapon Violence", "Weapons", "Corpses"]):
                                labels_detected = True
                                labels_detected_list.append(label["Name"])
                                if (label["Name"] in ["Graphic Male Nudity"]):
                                    not_allowed_labels_detected = True
                        if (labels_detected):
                            image.visible_on_website = False
                            logger.warning("moderate_unmoderated_photos::{labels_detected_count} labels detected. user={user}, labels detected={labels_detected_list} (registered {registered_days_ago} days ago).".format(
                                user=user,
                                labels_detected_count=len(labels_detected_list),
                                labels_detected_list=labels_detected_list,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                        else:
                            labels_list = [label["Name"] for label in image.aws_raw_image_moderation_results["ModerationLabels"]]
                            if (len(labels_list) > 0):
                                logger.info("moderate_unmoderated_photos::{labels_count} labels. user={user}, labels={labels_list} (registered {registered_days_ago} days ago).".format(
                                    user=user,
                                    labels_count=len(labels_list),
                                    labels_list=labels_list,
                                    registered_days_ago=(now() - user.date_created).days,
                                ))
                            image.visible_on_website = True
                            logger.debug("moderate_unmoderated_photos::labels not detected. user={user} (registered {registered_days_ago} days ago).".format(
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                        image.aws_image_moderation_time = now()
                        image.save()
                        if (not_allowed_labels_detected):
                            user.speedy_match_profile.not_allowed_to_use_speedy_match = True
                            user.photo = None
                            user.speedy_net_profile.deactivate()
                            user.speedy_match_profile.deactivate()
                            user.save_user_and_profile()
                            logger.error("moderate_unmoderated_photos::{labels_detected_count} labels detected. User {user} is not allowed to use Speedy Match (height={height}), labels detected={labels_detected_list} (registered {registered_days_ago} days ago).".format(
                                user=user,
                                height=user.speedy_match_profile.height,
                                labels_detected_count=len(labels_detected_list),
                                labels_detected_list=labels_detected_list,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                    else:
                        image.visible_on_website = False
                        image.aws_image_moderation_time = now()
                        image.save()
                        if (delete_this_photo):
                            # Photo is removed from the user's profile picture, but not from the database.
                            user.photo = None
                            user.speedy_match_profile.deactivate()
                            user.save_user_and_profile()
                            logger.warning("moderate_unmoderated_photos::delete this photo. reason={reason}, user={user} (registered {registered_days_ago} days ago).".format(
                                reason=delete_this_photo_reason,
                                user=user,
                                registered_days_ago=(now() - user.date_created).days,
                            ))

                except Exception as e:
                    logger.error('moderate_unmoderated_photos::user={user}, Exception={e} (registered {registered_days_ago} days ago)'.format(
                        user=user,
                        e=str(e),
                        registered_days_ago=(now() - user.date_created).days,
                    ))


