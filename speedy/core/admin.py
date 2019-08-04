from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        return urls


admin_site = AdminSite()


