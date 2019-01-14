import factory
from django.conf import settings as django_settings

from speedy.match.likes.models import UserLike

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.user_factories import ActiveUserFactory


if (django_settings.LOGIN_ENABLED):

    class UserLikeFactory(factory.django.DjangoModelFactory):
        from_user = factory.SubFactory(ActiveUserFactory)
        to_user = factory.SubFactory(ActiveUserFactory)

        class Meta:
            model = UserLike


