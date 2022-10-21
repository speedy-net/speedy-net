from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import UserLike


class UserLikeAdmin(ReadOnlyModelAdmin):
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(UserLike, UserLikeAdmin)


