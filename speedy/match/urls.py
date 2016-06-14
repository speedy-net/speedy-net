from django.conf.urls import url, include

# from django.contrib import admin

urlpatterns = [
    url(r'^', include('speedy.match.accounts.urls', namespace='accounts')),
    # url(r'^admin/', admin.site.urls),
]
