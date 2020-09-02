import factory
from django.conf import settings as django_settings

from speedy.core.uploads.models import File, Image

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


if (django_settings.LOGIN_ENABLED):

    class FileFactory(factory.django.DjangoModelFactory):
        owner = factory.SubFactory(ActiveUserFactory)
        file = factory.django.FileField()

        class Meta:
            model = File


    class UserImageFactory(factory.django.DjangoModelFactory):
        file = factory.django.ImageField()

        class Meta:
            model = Image


