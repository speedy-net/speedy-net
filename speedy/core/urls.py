from django.conf import settings as django_settings
from django.conf.urls import url, include

from django.conf.urls.static import static

app_name = 'speedy.core'
urlpatterns = [
    url(regex=r'^about/', view=include('speedy.core.about.urls', namespace='about')),
    url(regex=r'^privacy/', view=include('speedy.core.privacy.urls', namespace='privacy')),
    url(regex=r'^terms/', view=include('speedy.core.terms.urls', namespace='terms')),
]

# ~~~~ TODO: I'm not sure if it's a good idea to upload user images to the same server in production.
urlpatterns = static(prefix=django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT) + urlpatterns

if (django_settings.DEBUG):
    if ('debug_toolbar' in django_settings.INSTALLED_APPS):
        import debug_toolbar
        urlpatterns += [
            url(regex=r'^__debug__/', view=include(debug_toolbar.urls)),
        ]


