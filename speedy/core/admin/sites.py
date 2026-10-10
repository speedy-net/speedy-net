from django.contrib import admin as django_admin
from django.urls import path

from . import views


class AdminSite(django_admin.AdminSite):
    """
    Custom Django admin site that adds Speedy's own users-list and user-detail URLs.

    Attributes:
        final_catch_all_view (bool): Always False, disabling Django's default admin catch-all view.

    Methods:
        get_urls(self): Returns the admin site's URLs, including the users list, users-with-details list, and user detail routes.
    """
    final_catch_all_view = False

    def get_urls(self):
        """
        Returns the admin site's URL patterns, with Speedy's users list, users-with-details list, and user detail routes added.

        :return: The list of URL patterns.
        :rtype: list
        """
        urlpatterns = super().get_urls()
        urlpatterns += [
            path(route='users/', view=views.AdminUsersListView.as_view(), name='users_list'),
            path(route='users/with-details/', view=views.AdminUsersWithDetailsListView.as_view(), name='users_with_details_list'),
            path(route='user/<speedy_slug:slug>/', view=views.AdminUserDetailView.as_view(), name='user'),
        ]
        return urlpatterns


admin_site = AdminSite()


