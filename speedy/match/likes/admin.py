"""
Admin configuration for the user likes of Speedy Match. Registers the read-only UserLike admin.
"""
from speedy.core import admin
from speedy.core.base.admin import ReadOnlyModelAdmin
from .models import UserLike


class UserLikeAdmin(ReadOnlyModelAdmin):
    """
    Read-only admin configuration for the UserLike model.
    """
    readonly_fields = ('date_created', 'date_updated', 'id')


admin.site.register(UserLike, UserLikeAdmin)


