from django.conf import settings as django_settings

from translated_fields import TranslatedFieldAdmin

from speedy.core.base.admin import ModelAdmin, ModelAdmin15000, ReadOnlyModelAdmin2500


class SiteProfileBaseAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin2500):
    """
    Base admin class for site profile models, read-only except for deletion, which is always permitted.
    """
    readonly_fields = ('date_created', 'date_updated')

    def has_delete_permission(self, request, obj=None):
        """
        Allow deletion of site profiles unconditionally.

        :param request: The current request.
        :type request: django.http.HttpRequest
        :param obj: The site profile instance being checked, if any.
        :type obj: django.db.models.Model or None
        :return: Always True.
        :rtype: bool
        """
        return True


if (django_settings.LOGIN_ENABLED):
    from speedy.core import admin
    from speedy.core.messages.admin import MessageInlineAdmin
    from speedy.core.accounts.utils import get_site_profile_model
    from .models import Entity, ReservedUsername, User, UserEmailAddress

    SiteProfile = get_site_profile_model()


    class EntityAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin2500):
        """
        Admin for the Entity model, read-only except for deletion, with inline messages.
        """
        readonly_fields = ('date_created', 'date_updated', 'id')
        inlines = [
            MessageInlineAdmin,
        ]

        def has_delete_permission(self, request, obj=None):
            """
            Allow deletion of entities unconditionally.

            :param request: The current request.
            :type request: django.http.HttpRequest
            :param obj: The entity instance being checked, if any.
            :type obj: django.db.models.Model or None
            :return: Always True.
            :rtype: bool
            """
            return True


    class ReservedUsernameAdmin(ModelAdmin15000):
        """
        Admin for the ReservedUsername model.
        """
        readonly_fields = ('date_created', 'date_updated', 'id')


    class UserAdmin(TranslatedFieldAdmin, ReadOnlyModelAdmin2500):
        """
        Admin for the User model, read-only except for deletion, with inline messages and ordering by last visit on the current site's profile.
        """
        readonly_fields = ('date_created', 'date_updated', 'id')
        inlines = [
            MessageInlineAdmin,
        ]
        ordering = ('-{}__last_visit'.format(SiteProfile.RELATED_NAME),)

        def has_delete_permission(self, request, obj=None):
            """
            Allow deletion of users unconditionally.

            :param request: The current request.
            :type request: django.http.HttpRequest
            :param obj: The user instance being checked, if any.
            :type obj: django.db.models.Model or None
            :return: Always True.
            :rtype: bool
            """
            return True


    class UserEmailAddressAdmin(ReadOnlyModelAdmin2500):
        """
        Read-only admin for the UserEmailAddress model, except for deletion, which is always permitted.
        """
        readonly_fields = ('date_created', 'date_updated', 'id')

        def has_delete_permission(self, request, obj=None):
            """
            Allow deletion of user email addresses unconditionally.

            :param request: The current request.
            :type request: django.http.HttpRequest
            :param obj: The user email address instance being checked, if any.
            :type obj: django.db.models.Model or None
            :return: Always True.
            :rtype: bool
            """
            return True


    admin.site.register(Entity, EntityAdmin)
    admin.site.register(ReservedUsername, ReservedUsernameAdmin)
    admin.site.register(User, UserAdmin)

    if (django_settings.DEBUG):
        class UserEmailAddressDebugAdmin(ModelAdmin):
            """
            Admin for the UserEmailAddress model used in debug mode, with full default permissions (not read-only).
            """
            readonly_fields = ('date_created', 'date_updated', 'id')


        admin.site.register(UserEmailAddress, UserEmailAddressDebugAdmin)
    else:
        admin.site.register(UserEmailAddress, UserEmailAddressAdmin)


