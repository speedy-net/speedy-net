import factory
import factory.fuzzy

from django.conf import settings as django_settings


if (django_settings.LOGIN_ENABLED):
    from speedy.core.accounts.test.base_user_factories import DefaultUserFactory


    class InactiveUserFactory(DefaultUserFactory):
        @factory.post_generation
        def deactivate_profile(self, created, extracted, **kwargs):
            self.speedy_net_profile.deactivate()


    class ActiveUserFactory(DefaultUserFactory):
        @factory.post_generation
        def activate_profile(self, created, extracted, **kwargs):
            self.speedy_net_profile.activate()


