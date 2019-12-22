from django.contrib.admin import AdminSite as DjangoAdminSite
from django.conf.urls import url

from . import views


class AdminSite(DjangoAdminSite):
    def get_urls(self):
        urlpatterns = super().get_urls()
        urlpatterns += [
            url(regex=r'^users/$', view=views.AdminUsersListView.as_view(), name='users_list'),
            url(regex=r'^users/with-details/$', view=views.AdminUsersWithDetailsListView.as_view(), name='users_with_details_list'),
            url(regex=r'^user/(?P<slug>[-\._\w]+)/$', view=views.AdminUserDetailView.as_view(), name='user'),
        ]
        return urlpatterns


admin_site = AdminSite()


