from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import UserLike


admin.site.register(UserLike, ReadOnlyModelAdmin)


