from django.conf.urls import url, include

from speedy.core.urls import urlpatterns

app_name = 'speedy.mail'
urlpatterns += [
    url(r'^', include('speedy.mail.main.urls', namespace='main')),
]


