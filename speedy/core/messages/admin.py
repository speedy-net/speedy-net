from django.contrib import admin as django_admin

from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Chat, Message


class MessageInlineAdmin(django_admin.TabularInline):
    model = Message


admin.site.register(Chat, ReadOnlyModelAdmin)
admin.site.register(Message, ReadOnlyModelAdmin)


