import factory

from speedy.net.accounts.test_factories import UserFactory
from .models import EntityLike


class EntityLikeFactory(factory.django.DjangoModelFactory):
    from_user = factory.SubFactory(UserFactory)
    to_entity = factory.SubFactory(UserFactory)

    class Meta:
        model = EntityLike
