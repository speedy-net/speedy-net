from django.conf import settings
from django.conf.urls import url, include

from . import views
from django.conf.urls.static import static

urlpatterns = [
    url(r'^feedback/', include('speedy.net.feedback.urls', namespace='feedback')),
    url(r'^', views.MainPageView.as_view(), name='main_page_view'),
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
