from django.contrib.admin import AdminSite as DjangoAdminSite
from django.urls import re_path

from . import views


class AdminSite(DjangoAdminSite):
    def get_urls(self):
        urlpatterns = super().get_urls()
        urlpatterns += [
            re_path(route=r'^users/$', view=views.AdminUsersListView.as_view(), name='users_list'),
            re_path(route=r'^users/with-details/$', view=views.AdminUsersWithDetailsListView.as_view(), name='users_with_details_list'),
            re_path(route=r'^user/(?P<slug>[-\._\w]+)/$', view=views.AdminUserDetailView.as_view(), name='user'),
        ]
        return urlpatterns


admin_site = AdminSite()


