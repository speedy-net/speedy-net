from django.conf import settings as django_settings
from django.urls import path, include
from django.conf.urls.static import static

# Define and register Speedy Core path converters.
import speedy.core.base.path_converters

app_name = 'speedy.core'
urlpatterns = [
    path(route='about/', view=include(arg='speedy.core.about.urls', namespace='about')),
]

if (django_settings.DEBUG):
    urlpatterns = static(prefix=django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT) + urlpatterns

    if ('debug_toolbar' in django_settings.INSTALLED_APPS):
        import debug_toolbar
        urlpatterns += [
            path(route='__debug__/', view=include(arg=debug_toolbar.urls)),
        ]


