from django.contrib.admin import AdminSite as DjangoAdminSite
from django.urls import path

import speedy.core.base.path_converters
from . import views


class AdminSite(DjangoAdminSite):
    def get_urls(self):
        urlpatterns = super().get_urls()
        urlpatterns += [
            path(route='users/', view=views.AdminUsersListView.as_view(), name='users_list'),
            path(route='users/with-details/', view=views.AdminUsersWithDetailsListView.as_view(), name='users_with_details_list'),
            path(route='user/<slug:slug>/', view=views.AdminUserDetailView.as_view(), name='user'),
        ]
        return urlpatterns


admin_site = AdminSite()


