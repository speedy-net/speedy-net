from django.conf.urls import url, include

from speedy.core.urls import urlpatterns

urlpatterns += [
    url(r'^', include('speedy.composer.main.urls', namespace='main')),
]
