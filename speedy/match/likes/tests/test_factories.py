import factory

from speedy.core.accounts.tests.test_factories import ActiveUserFactory
from ..models import UserLike


class UserLikeFactory(factory.django.DjangoModelFactory):
    from_user = factory.SubFactory(ActiveUserFactory)
    to_user = factory.SubFactory(ActiveUserFactory)

    class Meta:
        model = UserLike
