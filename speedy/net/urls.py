from django.conf.urls import url, include

# from django.contrib import admin

urlpatterns = [
    url(r'^', include('speedy.net.accounts.urls', namespace='accounts')),
    # url(r'^admin/', admin.site.urls),
]
