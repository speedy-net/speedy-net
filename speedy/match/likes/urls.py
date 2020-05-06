from django.urls import path

import speedy.core.base.path_converters
from . import views

app_name = 'speedy.match.likes'
urlpatterns = [
    path(route='', view=views.LikeListDefaultRedirectView.as_view(), name='list'),
    path(route='people-i-like/', view=views.LikeListToView.as_view(), name='list_to'),
    path(route='people-who-like-me/', view=views.LikeListFromView.as_view(), name='list_from'),
    path(route='mutual/', view=views.LikeListMutualView.as_view(), name='list_mutual'),
    path(route='like/', view=views.LikeView.as_view(), name='like'),
    path(route='unlike/', view=views.UnlikeView.as_view(), name='unlike'),
]


