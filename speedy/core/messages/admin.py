from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Chat, Message


admin.site.register(Chat, ReadOnlyModelAdmin)
admin.site.register(Message, ReadOnlyModelAdmin)


