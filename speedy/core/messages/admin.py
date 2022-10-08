from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin, ReadOnlyModelAdmin2000, ReadOnlyTabularInlinePaginatedModelAdmin
from .models import Chat, Message


class MessageInlineAdmin(ReadOnlyTabularInlinePaginatedModelAdmin):
    model = Message
    per_page = 100


admin.site.register(Chat, ReadOnlyModelAdmin)
admin.site.register(Message, ReadOnlyModelAdmin2000)


