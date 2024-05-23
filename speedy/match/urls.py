from django.urls import path, include

from speedy.match import admin
from speedy.core.urls_with_login import urlpatterns

app_name = 'speedy.match'
urlpatterns += [
    path(route='matches/', view=include('speedy.match.matches.urls', namespace='matches')),
    path(route='', view=include('speedy.match.accounts.urls', namespace='accounts')),
    path(route='admin/', view=admin.site.urls),

    # always at the bottom
    path(route='<speedy_slug:slug>/friends/', view=include('speedy.core.friends.urls', namespace='friends')),
    path(route='messages/', view=include('speedy.core.messages.urls_private', namespace='messages')),
    path(route='messages/<speedy_slug:slug>/', view=include('speedy.core.messages.urls_public', namespace='messages_entity')),
    path(route='<speedy_slug:slug>/likes/', view=include('speedy.match.likes.urls', namespace='likes')),
    path(route='uploads/', view=include('speedy.core.uploads.urls', namespace='uploads')),
    path(route='<speedy_slug:slug>/', view=include('speedy.core.blocks.urls', namespace='blocks')),
    path(route='', view=include('speedy.match.profiles.urls', namespace='profiles')),
]


