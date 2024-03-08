from speedy.core.admin import sites as speedy_core_admin_sites
from django.urls import path

from . import views


class AdminSite(speedy_core_admin_sites.AdminSite):
    def get_urls(self):
        urlpatterns = super().get_urls()
        urlpatterns += [
            path(route='matches/', view=views.AdminMatchesListView.as_view(), name='matches_list'),
            path(route='matches/any/', view=views.AdminMatchesAnyLanguageListView.as_view(), name='matches_list_any_language'),
        ]
        return urlpatterns


admin_site = AdminSite()


