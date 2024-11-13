from django.urls import path, include

from speedy.core import admin
from speedy.core.urls_without_login import urlpatterns

app_name = 'speedy.composer'
urlpatterns += [
    path(route='admin/', view=admin.site.urls),
    path(route='', view=include(arg='speedy.composer.main.urls', namespace='main')),
]


