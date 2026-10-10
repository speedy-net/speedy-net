"""
Django admin configuration for the messages app of Speedy Core, which registers read-only admins for the Chat and Message models.
"""
from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin, ReadOnlyModelAdmin2000, ReadOnlyTabularInlinePaginatedModelAdmin
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile
from .models import Chat, Message


class MessageInlineAdmin(ReadOnlyTabularInlinePaginatedModelAdmin):
    """
    Read-only, paginated inline admin for displaying a chat's messages on the Chat admin page.

    Methods:
        get_queryset(self, request): Returns the messages queryset with related chat participants and senders prefetched.
    """
    model = Message
    per_page = 100
    readonly_fields = ('date_created', 'date_updated', 'id')

    def get_queryset(self, request):
        """
        Returns the messages queryset with the chat's participants and senders prefetched, to avoid extra queries in the admin list.

        :param request: The current admin request.
        :type request: django.http.HttpRequest
        :return: The queryset of Message instances.
        :rtype: django.db.models.QuerySet
        """
        return super().get_queryset(request=request).prefetch_related(
            'chat__ent1__user__{}'.format(SpeedyMatchSiteProfile.RELATED_NAME),
            'chat__ent1__user__{}'.format(SpeedyNetSiteProfile.RELATED_NAME),
            'chat__ent2__user__{}'.format(SpeedyMatchSiteProfile.RELATED_NAME),
            'chat__ent2__user__{}'.format(SpeedyNetSiteProfile.RELATED_NAME),
            'chat__messages__sender',
            'sender',
        )


class ChatAdmin(ReadOnlyModelAdmin):
    """
    Read-only admin for the Chat model, with the chat's messages shown as a read-only inline.
    """
    readonly_fields = ('date_created', 'date_updated', 'id')
    inlines = [
        MessageInlineAdmin,
    ]


class MessageAdmin(ReadOnlyModelAdmin2000):
    """
    Read-only admin for the Message model.
    """
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)


