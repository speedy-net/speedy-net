"""
Admin site of Speedy Net, extending the Speedy Core admin site.
"""
from speedy.core.admin import sites as speedy_core_admin_sites


# from django.urls import path

# from . import views


class AdminSite(speedy_core_admin_sites.AdminSite):
    """
    Admin site for Speedy Net. Uses the default admin URLs and views defined by the base admin site.
    """
    pass


admin_site = AdminSite()


