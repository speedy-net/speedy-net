from django.urls import path, include

from speedy.match import admin
from speedy.core.urls_with_login import urlpatterns

app_name = 'speedy.match'
urlpatterns += [
    path(route='matches/', view=include(arg='speedy.match.matches.urls', namespace='matches')),
    path(route='', view=include(arg='speedy.match.accounts.urls', namespace='accounts')),
    path(route='admin/', view=admin.site.urls),

    # always at the bottom
    path(route='<speedy_slug:slug>/friends/', view=include(arg='speedy.core.friends.urls', namespace='friends')),
    path(route='messages/', view=include(arg='speedy.core.messages.urls_private', namespace='messages')),
    path(route='messages/<speedy_slug:slug>/', view=include(arg='speedy.core.messages.urls_public', namespace='messages_entity')),
    path(route='<speedy_slug:slug>/likes/', view=include(arg='speedy.match.likes.urls', namespace='likes')),
    path(route='uploads/', view=include(arg='speedy.core.uploads.urls', namespace='uploads')),
    path(route='<speedy_slug:slug>/', view=include(arg='speedy.core.blocks.urls', namespace='blocks')),
    path(route='', view=include(arg='speedy.match.profiles.urls', namespace='profiles')),
]


