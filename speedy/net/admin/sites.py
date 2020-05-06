from speedy.core.admin import sites as speedy_core_admin_sites
# from django.urls import path

# from . import views


class AdminSite(speedy_core_admin_sites.AdminSite):
    pass


admin_site = AdminSite()


