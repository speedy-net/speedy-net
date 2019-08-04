from django.conf.urls import url, include

from speedy.match.admin import admin_site
from speedy.core.urls_with_login import urlpatterns

app_name = 'speedy.match'
urlpatterns += [
    url(regex=r'^matches/', view=include('speedy.match.matches.urls', namespace='matches')),
    url(regex=r'^', view=include('speedy.match.accounts.urls', namespace='accounts')),
    url(regex=r'^admin/', view=admin_site.urls),
    url(regex=r'^i18n/', view=include('django.conf.urls.i18n')),

    # always at the bottom
    url(regex=r'^(?P<slug>[-\._\w]+)/friends/', view=include('speedy.core.friends.urls', namespace='friends')),
    url(regex=r'^messages/', view=include('speedy.core.messages.urls_private', namespace='messages')),
    url(regex=r'^messages/(?P<slug>[-\._\w]+)/', view=include('speedy.core.messages.urls_public', namespace='messages_entity')),
    url(regex=r'^(?P<slug>[-\._\w]+)/blocks/', view=include('speedy.core.blocks.urls', namespace='blocks')),
    url(regex=r'^(?P<slug>[-\._\w]+)/likes/', view=include('speedy.match.likes.urls', namespace='likes')),
    url(regex=r'^uploads/', view=include('speedy.core.uploads.urls', namespace='uploads')),
    url(regex=r'^', view=include('speedy.match.profiles.urls', namespace='profiles')),
]


