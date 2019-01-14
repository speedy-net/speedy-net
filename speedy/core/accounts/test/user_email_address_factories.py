import factory
import factory.fuzzy

from django.conf import settings as django_settings

from speedy.core.accounts.models import UserEmailAddress


if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.base_user_factories import DefaultUserFactory


    class UserEmailAddressFactory(factory.DjangoModelFactory):
        user = factory.SubFactory(DefaultUserFactory)
        email = factory.Faker('email')

        class Meta:
            model = UserEmailAddress


