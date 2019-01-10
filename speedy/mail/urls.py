from django.conf.urls import url, include
from django.contrib import admin

from speedy.core.urls import urlpatterns

app_name = 'speedy.mail'
urlpatterns += [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('speedy.mail.main.urls', namespace='main')),
]


