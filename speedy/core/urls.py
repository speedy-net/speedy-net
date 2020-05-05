from django.conf import settings as django_settings
from django.urls import re_path, include

from django.conf.urls.static import static

app_name = 'speedy.core'
urlpatterns = [
    re_path(route=r'^about/', view=include('speedy.core.about.urls', namespace='about')),
]

if (django_settings.DEBUG):
    urlpatterns = static(prefix=django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT) + urlpatterns

    if ('debug_toolbar' in django_settings.INSTALLED_APPS):
        import debug_toolbar
        urlpatterns += [
            re_path(route=r'^__debug__/', view=include(debug_toolbar.urls)),
        ]


