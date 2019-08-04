from speedy.core.admin.sites import AdminSite as CoreAdminSite
from django.conf.urls import url

from . import views


class AdminSite(CoreAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(regex=r'^matches/$', view=views.AdminMatchesListView.as_view(), name='matches_list'),
        ]
        return urls


admin_site = AdminSite()


