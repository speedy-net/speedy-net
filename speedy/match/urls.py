from django.urls import re_path, include

from speedy.match import admin
from speedy.core.urls_with_login import urlpatterns

app_name = 'speedy.match'
urlpatterns += [
    re_path(route=r'^matches/', view=include('speedy.match.matches.urls', namespace='matches')),
    re_path(route=r'^', view=include('speedy.match.accounts.urls', namespace='accounts')),
    re_path(route=r'^admin/', view=admin.site.urls),

    # always at the bottom
    re_path(route=r'^(?P<slug>[-\._\w]+)/friends/', view=include('speedy.core.friends.urls', namespace='friends')),
    re_path(route=r'^messages/', view=include('speedy.core.messages.urls_private', namespace='messages')),
    re_path(route=r'^messages/(?P<slug>[-\._\w]+)/', view=include('speedy.core.messages.urls_public', namespace='messages_entity')),
    re_path(route=r'^(?P<slug>[-\._\w]+)/likes/', view=include('speedy.match.likes.urls', namespace='likes')),
    re_path(route=r'^uploads/', view=include('speedy.core.uploads.urls', namespace='uploads')),
    re_path(route=r'^(?P<slug>[-\._\w]+)/', view=include('speedy.core.blocks.urls', namespace='blocks')),
    re_path(route=r'^', view=include('speedy.match.profiles.urls', namespace='profiles')),
]


