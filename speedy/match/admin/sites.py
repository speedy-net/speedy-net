"""
Admin site of Speedy Match, extending the Speedy Core admin site with the Speedy Match admin URLs.
"""
from speedy.core.admin import sites as speedy_core_admin_sites
from django.urls import path

from . import views


class AdminSite(speedy_core_admin_sites.AdminSite):
    """
    Custom admin site for Speedy Match, adding the matches list admin pages.

    Methods:
        get_urls(self): Returns the admin URL patterns, including the Speedy Match matches list views.
    """
    def get_urls(self):
        """
        Returns the admin URL patterns, extending the parent site's patterns with the Speedy Match matches-list admin views.

        :return: The combined list of URL patterns.
        :rtype: list
        """
        urlpatterns = super().get_urls()
        urlpatterns += [
            path(route='matches/', view=views.AdminMatchesListView.as_view(), name='matches_list'),
            path(route='matches/any/', view=views.AdminMatchesAnyLanguageListView.as_view(), name='matches_list_any_language'),
        ]
        return urlpatterns


admin_site = AdminSite()


