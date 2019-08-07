from speedy.core.admin.sites import AdminSite as CoreAdminSite
# from django.conf.urls import url

# from . import views


class AdminSite(CoreAdminSite):
    pass


admin_site = AdminSite()


