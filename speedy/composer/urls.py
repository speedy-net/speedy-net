from django.conf.urls import url, include

from speedy.core.admin import admin_site
from speedy.core.urls_without_login import urlpatterns

app_name = 'speedy.composer'
urlpatterns += [
    url(regex=r'^admin/', view=admin_site.urls),
    url(regex=r'^', view=include('speedy.composer.main.urls', namespace='main')),
]


