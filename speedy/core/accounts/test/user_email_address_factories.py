from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from typing import TYPE_CHECKING

        import factory

        from speedy.core.accounts.test.base_user_factories import DefaultUserFactory

        from speedy.core.base.utils import generate_regular_udid as generate_random_id
        from speedy.core.accounts.models import UserEmailAddress

        UserEmailAddressTypeHintMixin = object
        if (TYPE_CHECKING):
            UserEmailAddressTypeHintMixin = UserEmailAddress


        class UserEmailAddressFactory(factory.django.DjangoModelFactory, UserEmailAddressTypeHintMixin):
            user = factory.SubFactory(DefaultUserFactory)
            email = factory.LazyAttribute(lambda o: '{id}@example.speedy.net'.format(id=generate_random_id()).lower())

            class Meta:
                model = UserEmailAddress


