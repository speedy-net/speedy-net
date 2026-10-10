from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        from typing import TYPE_CHECKING

        import factory

        from speedy.core.accounts.test.user_factories import ActiveUserFactory

        from speedy.core.uploads.models import File, Image

        FileTypeHintMixin = object
        ImageTypeHintMixin = object
        if (TYPE_CHECKING):
            FileTypeHintMixin = File
            ImageTypeHintMixin = Image


        class FileFactory(factory.django.DjangoModelFactory, FileTypeHintMixin):
            """
            Factory for creating File instances for tests, owned by a newly created active user.
            """
            owner = factory.SubFactory(ActiveUserFactory)
            file = factory.django.FileField()

            class Meta:
                model = File


        class UserImageFactory(factory.django.DjangoModelFactory, ImageTypeHintMixin):
            """
            Factory for creating Image instances for tests.
            """
            file = factory.django.ImageField()

            class Meta:
                model = Image


