from django.conf import settings as django_settings
from django.conf.urls import url, include

from django.conf.urls.static import static

app_name = 'speedy.core'
urlpatterns = [
    url(regex=r'^about/', view=include('speedy.core.about.urls', namespace='about')),
    url(regex=r'^privacy/', view=include('speedy.core.privacy.urls', namespace='privacy')),
    url(regex=r'^terms/', view=include('speedy.core.terms.urls', namespace='terms')),
    url(regex=r'^contact/', view=include('speedy.core.feedback.urls', namespace='feedback')),
]

if (django_settings.DEBUG):
    urlpatterns = static(django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT) + urlpatterns

    if ('debug_toolbar' in django_settings.INSTALLED_APPS):
        import debug_toolbar
        urlpatterns += [
            url(regex=r'^__debug__/', view=include(debug_toolbar.urls)),
        ]


