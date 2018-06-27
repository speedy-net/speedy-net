from django.conf.urls import url, include

from speedy.core.urls import urlpatterns

app_name = 'speedy.composer'
urlpatterns += [
    url(r'^', include('speedy.composer.main.urls', namespace='main')),
]
