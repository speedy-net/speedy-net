from django.conf.urls import url, include

# from django.contrib import admin

urlpatterns = [
    url(r'^', include('speedy.net.accounts.urls', namespace='accounts')),
    # url(r'^admin/', admin.site.urls),

    # always at the bottom
    url(r'^(?P<username>[-\w]+)/friends/', include('speedy.net.friends.urls', namespace='friends')),
    url(r'^', include('speedy.net.profiles.urls', namespace='profiles')),
]
