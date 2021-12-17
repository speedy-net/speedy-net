from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import factory

        from speedy.core.uploads.models import File, Image

        from speedy.core.accounts.test.user_factories import ActiveUserFactory


        class FileFactory(factory.django.DjangoModelFactory):
            owner = factory.SubFactory(ActiveUserFactory)
            file = factory.django.FileField()

            class Meta:
                model = File


        class UserImageFactory(factory.django.DjangoModelFactory):
            file = factory.django.ImageField()

            class Meta:
                model = Image


