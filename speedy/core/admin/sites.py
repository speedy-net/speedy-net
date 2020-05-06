from django.contrib import admin as django_admin
from django.urls import path

from . import views


class AdminSite(django_admin.AdminSite):
    def get_urls(self):
        urlpatterns = super().get_urls()
        urlpatterns += [
            path(route='users/', view=views.AdminUsersListView.as_view(), name='users_list'),
            path(route='users/with-details/', view=views.AdminUsersWithDetailsListView.as_view(), name='users_with_details_list'),
            path(route='user/<slug:slug>/', view=views.AdminUserDetailView.as_view(), name='user'),
        ]
        return urlpatterns


admin_site = AdminSite()


