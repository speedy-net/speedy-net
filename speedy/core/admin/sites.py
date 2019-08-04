from django.contrib.admin import AdminSite as DjangoAdminSite
from django.conf.urls import url

from . import views


class AdminSite(DjangoAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(regex=r'^users/$', view=views.AdminUsersListView.as_view(), name='users_list'),
        ]
        return urls


admin_site = AdminSite()


