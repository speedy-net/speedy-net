import factory

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from ..models import File, Image


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = File

    owner = factory.SubFactory(ActiveUserFactory)
    file = factory.django.FileField()


class UserImageFactory(factory.DjangoModelFactory):
    file = factory.django.ImageField()

    class Meta:
        model = Image


