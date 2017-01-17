from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

urlpatterns = [
    url(r'^about/', include('speedy.core.about.urls', namespace='about')),
    url(r'^privacy/', include('speedy.core.privacy.urls', namespace='privacy')),
    url(r'^terms/', include('speedy.core.terms.urls', namespace='terms')),
    url(r'^contact/', include('speedy.core.feedback.urls', namespace='feedback')),
    url(r'^', include('speedy.composer.main.urls', namespace='main')),
]

if settings.DEBUG:
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns

try:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
except ImportError:
    pass
