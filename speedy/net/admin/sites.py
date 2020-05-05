from speedy.core.admin.sites import AdminSite as CoreAdminSite
# from django.urls import re_path

# from . import views


class AdminSite(CoreAdminSite):
    pass


admin_site = AdminSite()


