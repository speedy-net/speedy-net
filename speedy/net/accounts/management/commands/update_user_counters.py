import logging

from django.core.management import BaseCommand

from speedy.core.accounts.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all(
        ).prefetch_related(
            "likes_to_user",
            "friends",
        )
        for user in users:
            # Users might have changed in the database, load them again.
            user = User.objects.get(pk=user.pk)
            if (user.speedy_match_profile.likes_to_user_count is None):
                user.speedy_match_profile.likes_to_user_count = len(user.likes_to_user.all())
                user.speedy_match_profile.save()
            if (user.speedy_net_profile.friends_count is None):
                user.speedy_net_profile.friends_count = len(user.friends.all())
                user.speedy_net_profile.save()


