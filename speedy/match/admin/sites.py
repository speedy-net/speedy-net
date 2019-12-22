from speedy.core.admin.sites import AdminSite as CoreAdminSite
from django.conf.urls import url

from . import views


class AdminSite(CoreAdminSite):
    def get_urls(self):
        urlpatterns = super().get_urls()
        urlpatterns += [
            url(regex=r'^matches/$', view=views.AdminMatchesListView.as_view(), name='matches_list'),
        ]
        return urlpatterns


admin_site = AdminSite()


