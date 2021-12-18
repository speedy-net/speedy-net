from django.urls import path, include

from speedy.net import admin
from speedy.core.urls_with_login import urlpatterns

app_name = 'speedy.net'
urlpatterns += [
    path(route='', view=include('speedy.net.accounts.urls', namespace='accounts')),
    path(route='admin/', view=admin.site.urls),

    # always at the bottom
    path(route='<slug:slug>/friends/', view=include('speedy.core.friends.urls', namespace='friends')),
    path(route='messages/', view=include('speedy.core.messages.urls_private', namespace='messages')),
    path(route='messages/<slug:slug>/', view=include('speedy.core.messages.urls_public', namespace='messages_entity')),
    path(route='uploads/', view=include('speedy.core.uploads.urls', namespace='uploads')),
    path(route='<slug:slug>/', view=include('speedy.net.blocks.urls', namespace='blocks')),
    path(route='', view=include('speedy.core.profiles.urls', namespace='profiles')),
]


