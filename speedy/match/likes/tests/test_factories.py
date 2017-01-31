import factory

from speedy.core.accounts.tests.test_factories import UserFactory
from ..models import UserLike


class UserLikeFactory(factory.django.DjangoModelFactory):
    from_user = factory.SubFactory(UserFactory)
    to_user = factory.SubFactory(UserFactory)

    class Meta:
        model = UserLike
