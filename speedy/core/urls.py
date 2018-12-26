from django.conf import settings as django_settings
from django.conf.urls import url, include

from django.conf.urls.static import static

app_name = 'speedy.core'
urlpatterns = [
    url(r'^about/', include('speedy.core.about.urls', namespace='about')),
    url(r'^privacy/', include('speedy.core.privacy.urls', namespace='privacy')),
    url(r'^terms/', include('speedy.core.terms.urls', namespace='terms')),
    url(r'^contact/', include('speedy.core.feedback.urls', namespace='feedback')),
]

if (django_settings.DEBUG):
    urlpatterns = static(django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT) + urlpatterns

try:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass


