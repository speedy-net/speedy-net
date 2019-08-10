from django.contrib.admin import AdminSite as DjangoAdminSite
from django.conf.urls import url

from . import views


class AdminSite(DjangoAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        urls += [
            url(regex=r'^users/$', view=views.AdminUsersListView.as_view(), name='users_list'),
            url(regex=r'^users/with-details/$', view=views.AdminUsersWithDetailsListView.as_view(), name='users_with_details_list'),
        ]
        return urls


admin_site = AdminSite()


