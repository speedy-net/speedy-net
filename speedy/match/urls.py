from django.conf import settings
from django.conf.urls import url, include

from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'^', include('speedy.match.accounts.urls', namespace='accounts')),
    url(r'^admin/', admin.site.urls),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # always at the bottom
    url(r'^(?P<slug>[-\._\w]+)/friends/', include('speedy.net.friends.urls', namespace='friends')),
    url(r'^messages/', include('speedy.net.im.urls_private', namespace='im')),
    url(r'^messages/(?P<slug>[-\._\w]+)/', include('speedy.net.im.urls_public', namespace='im_entity')),
    url(r'^(?P<slug>[-\._\w]+)/blocks/', include('speedy.net.blocks.urls', namespace='blocks')),
    url(r'^(?P<slug>[-\._\w]+)/likes/', include('speedy.match.likes.urls', namespace='likes')),
    url(r'^uploads/', include('speedy.net.uploads.urls', namespace='uploads')),
    url(r'^feedback/', include('speedy.net.feedback.urls', namespace='feedback')),
    url(r'^', include('speedy.net.profiles.urls', namespace='profiles')),
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
