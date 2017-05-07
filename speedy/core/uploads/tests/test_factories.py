import factory

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from ..models import File


class FileFactory(factory.DjangoModelFactory):
    class Meta:
        model = File

    owner = factory.SubFactory(ActiveUserFactory)
    file = factory.django.FileField()
