from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from base.models import (UserProfile, UserEmailAddress, Token, Identity)
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
    help = 'Removes expired user accounts_core and emails'

    def handle(self, *args, **options):
        expired_time = timezone.now() + timedelta(days=settings.EMAIL_TOKEN_EXPIRY)
        expired_emails = UserEmailAddress.objects.filter(token__created__gt=expired_time)

        for email in expired_emails:
            profile = email.profile
            if (UserEmailAddress.objects.filter(profile=profile).count) > 1:
                # user has more than email, delete only email
                email.delete()
                self.stdout.write(self.style.SUCCESS('Cleaned email "%s"' % email.email))
            else:
                # delete account and associated models as well
                user = profile.user
                identity = profile.identity
                identity.delete()
                user.delete()
                profile.delete()
                self.stdout.write(self.style.SUCCESS('Cleaned email "%s" and account "%s"' % (email.email, profile.identity.username)))
