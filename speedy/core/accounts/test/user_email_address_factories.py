import factory
import factory.fuzzy

from django.conf import settings as django_settings

from speedy.core.base.utils import generate_regular_udid as generate_random_id
from speedy.core.accounts.models import UserEmailAddress

if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.base_user_factories import DefaultUserFactory


    class UserEmailAddressFactory(factory.DjangoModelFactory):
        user = factory.SubFactory(DefaultUserFactory)
        email = factory.LazyAttribute(lambda o: '{id}@example.speedy.net'.format(id=generate_random_id()).lower())

        class Meta:
            model = UserEmailAddress


