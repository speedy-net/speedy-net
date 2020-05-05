from django.urls import re_path

from . import views

app_name = 'speedy.match.likes'
urlpatterns = [
    re_path(route=r'^$', view=views.LikeListDefaultRedirectView.as_view(), name='list'),
    re_path(route=r'^people-i-like/$', view=views.LikeListToView.as_view(), name='list_to'),
    re_path(route=r'^people-who-like-me/$', view=views.LikeListFromView.as_view(), name='list_from'),
    re_path(route=r'^mutual/$', view=views.LikeListMutualView.as_view(), name='list_mutual'),
    re_path(route=r'^like/$', view=views.LikeView.as_view(), name='like'),
    re_path(route=r'^unlike/$', view=views.UnlikeView.as_view(), name='unlike'),
]


