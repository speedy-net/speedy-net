from speedy.core.admin import AdminSite as CoreAdminSite
from django.conf.urls import url

from . import admin_views


class AdminSite(CoreAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(regex=r'^matches/$', view=admin_views.AdminMatchesListView.as_view(), name='matches_list'),
        ]
        return urls


admin_site = AdminSite()


