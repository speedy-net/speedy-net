from speedy.core.admin import admin_site
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import Chat, Message


admin_site.register(Chat, ReadOnlyModelAdmin)
admin_site.register(Message, ReadOnlyModelAdmin)


