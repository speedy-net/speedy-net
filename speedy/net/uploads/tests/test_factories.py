import factory

from speedy.net.accounts.tests.test_factories import UserFactory
from ..models import File


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = File

    owner = factory.SubFactory(UserFactory)
    file = factory.django.FileField()
