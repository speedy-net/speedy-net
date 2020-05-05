from django.urls import re_path, include

from speedy.core import admin
from speedy.core.urls_without_login import urlpatterns

app_name = 'speedy.composer'
urlpatterns += [
    re_path(route=r'^admin/', view=admin.site.urls),
    re_path(route=r'^', view=include('speedy.composer.main.urls', namespace='main')),
]


