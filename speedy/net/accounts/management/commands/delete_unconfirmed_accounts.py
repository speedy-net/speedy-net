import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from friendship.models import Friend, FriendshipRequest

from speedy.core.accounts.models import User, UserEmailAddress
from speedy.core.blocks.models import Block
from speedy.match.likes.models import UserLike

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        emails = UserEmailAddress.objects.filter(
            is_confirmed=False,
            date_created__lte=(now() - timedelta(days=10)),
            confirmation_sent__gte=2,
        ).exclude(user__is_staff=True)
        for email in emails:
            user = email.user
            if (not (user.is_staff)):
                if (email.date_created <= now() - timedelta(days=10)):
                    if ((email.is_confirmed is False) and (email.confirmation_sent >= 2)):
                        logger.warning("Deleting email {} of user {} - unconfirmed. Confirmation sent {} times, Added on {}.".format(email, user, email.confirmation_sent, email.date_created))
                        email.delete()

        users = User.objects.filter(
            date_created__lte=(now() - timedelta(days=14)),
            date_created__gte=(now() - timedelta(days=18)),
            has_confirmed_email=False,
        ).exclude(is_staff=True)
        for user in users:
            if (not (user.is_staff)):
                if ((user.date_created <= now() - timedelta(days=14)) and (user.date_created >= now() - timedelta(days=18))):
                    user._update_has_confirmed_email_field()
                    if (not (user.has_confirmed_email)):
                        try:
                            logger.warning("Deleting user {user} - no confirmed email. Registered on {date_created} (registered {registered_days_ago} days ago).".format(
                                user=user,
                                date_created=user.date_created,
                                registered_days_ago=(now() - user.date_created).days,
                            ))
                            user.delete()
                        except Exception as e:
                            logger.error("Can't delete user {user} - exception {e} (registered {registered_days_ago} days ago).".format(
                                user=user,
                                e=e,
                                registered_days_ago=(now() - user.date_created).days,
                            ))

        users = User.objects.filter(
            is_deleted=True,
            is_deleted_time__lt=(now() - timedelta(days=60)),
            date_created__lt=(now() - timedelta(days=60)),
            speedy_match_site_profile__last_visit__lt=now() - timedelta(days=60),
            speedy_net_site_profile__last_visit__lt=now() - timedelta(days=60),
        ).exclude(is_staff=True)
        for user in users:
            if (not (user.is_staff)):
                if ((user.is_deleted is True) and (user.is_deleted_time is not None)):
                    if (not ((user.username == user.id) and (user.slug == user.id))):
                        if ((user.is_deleted_time < now() - timedelta(days=60)) and (user.date_created < now() - timedelta(days=60)) and (user.speedy_match_profile.last_visit < now() - timedelta(days=60)) and (user.speedy_net_profile.last_visit < now() - timedelta(days=60))):
                            try:
                                logger.warning("Permanently marking user as deleted - {user}. Registered on {date_created} (registered {registered_days_ago} days ago).".format(
                                    user=user,
                                    date_created=user.date_created,
                                    registered_days_ago=(now() - user.date_created).days,
                                ))
                                # The following code should already be done by UserManager::mark_a_user_as_deleted, but we do it here again just in case.
                                assert (user.is_deleted is True)
                                user.set_unusable_password()
                                user.save()
                                user.speedy_net_profile.deactivate()
                                user.speedy_match_profile.deactivate()
                                user.photo = None
                                user.save()
                                user.save_user_and_profile()
                                for e1 in user.email_addresses.all():
                                    e1.delete()
                                # Remove user's username and slug, and set them to the user's id. Also set the user's special_username to True (this is required for username==id).
                                user.username, user.slug, user.special_username = user.id, user.id, False  #### True
                                user.save_user_and_profile()  #### ~~~~ TODO: should raise exception if special_username is False.
                                # Remove all likes from user, but keep the likes to user.
                                UserLike.objects.remove_all_likes_from_user(from_user=user)
                                # Remove all friendships of user.
                                for fr in user.friends.all():
                                    other_user = fr.from_user
                                    Friend.objects.remove_friend(from_user=user, to_user=other_user)
                                # Remove all sent friendship requests of user, but keep the received friendship requests.
                                for fr in FriendshipRequest.objects.filter(from_user=user):
                                    fr.cancel()
                                # Remove all blocks by user, but keep the blocks of user.
                                Block.objects.remove_all_blocks_by_entity(blocker=user)
                            except Exception as e:
                                logger.error("Can't permanently mark user as deleted {user} - exception {e} (registered {registered_days_ago} days ago).".format(
                                    user=user,
                                    e=e,
                                    registered_days_ago=(now() - user.date_created).days,
                                ))


