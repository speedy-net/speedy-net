from django.urls import re_path, include

from speedy.core import admin
from speedy.core.urls_with_login import urlpatterns

app_name = 'speedy.net'
urlpatterns += [
    re_path(route=r'^', view=include('speedy.net.accounts.urls', namespace='accounts')),
    re_path(route=r'^admin/', view=admin.site.urls),

    # always at the bottom
    re_path(route=r'^(?P<slug>[-\._\w]+)/friends/', view=include('speedy.core.friends.urls', namespace='friends')),
    re_path(route=r'^messages/', view=include('speedy.core.messages.urls_private', namespace='messages')),
    re_path(route=r'^messages/(?P<slug>[-\._\w]+)/', view=include('speedy.core.messages.urls_public', namespace='messages_entity')),
    re_path(route=r'^uploads/', view=include('speedy.core.uploads.urls', namespace='uploads')),
    re_path(route=r'^(?P<slug>[-\._\w]+)/', view=include('speedy.core.blocks.urls', namespace='blocks')),
    re_path(route=r'^', view=include('speedy.core.profiles.urls', namespace='profiles')),
]


