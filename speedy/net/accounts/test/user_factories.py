from django.conf import settings as django_settings

if (django_settings.TESTS):
    if (django_settings.LOGIN_ENABLED):
        import factory

        from speedy.core.accounts.test.base_user_factories import DefaultUserFactory
        from speedy.core.accounts.test.user_email_address_factories import UserEmailAddressFactory


        class InactiveUserFactory(DefaultUserFactory):
            """
            This factory is used to create users who are inactive on Speedy Net and Speedy Match.
            """
            @factory.post_generation
            def deactivate_profile(self, created, extracted, **kwargs):
                self.speedy_net_profile.deactivate()


        class ActiveUserFactory(DefaultUserFactory):
            """
            This factory is used to create users who are active on Speedy Net, but inactive on Speedy Match.
            """
            @factory.post_generation
            def activate_profile(self, created, extracted, **kwargs):
                email = UserEmailAddressFactory(user=self, is_confirmed=True)
                email.save()
                email.make_primary()
                self.speedy_net_profile.activate()


