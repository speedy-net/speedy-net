from django.conf import settings
from django.conf.urls import url, include

from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'^', include('speedy.net.accounts.urls', namespace='accounts')),
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # always at the bottom
    url(r'^(?P<username>[-\w]+)/friends/', include('speedy.net.friends.urls', namespace='friends')),
    url(r'^(?P<username>[-\w]+)/messages/', include('speedy.net.im.urls', namespace='im')),
    url(r'^(?P<username>[-\w]+)/blocks/', include('speedy.net.blocks.urls', namespace='blocks')),
    url(r'^uploads/', include('speedy.net.uploads.urls', namespace='uploads')),
    url(r'^feedback/', include('speedy.net.feedback.urls', namespace='feedback')),
    url(r'^', include('speedy.net.profiles.urls', namespace='profiles')),
]

if settings.DEBUG:
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns
