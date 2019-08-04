from django.conf.urls import url

from . import views

app_name = 'speedy.match.likes'
urlpatterns = [
    url(regex=r'^$', view=views.LikeListDefaultRedirectView.as_view(), name='list'),
    url(regex=r'^people-i-like/$', view=views.LikeListToView.as_view(), name='list_to'),
    url(regex=r'^people-who-like-me/$', view=views.LikeListFromView.as_view(), name='list_from'),
    url(regex=r'^mutual/$', view=views.LikeListMutualView.as_view(), name='list_mutual'),
    url(regex=r'^like/$', view=views.LikeView.as_view(), name='like'),
    url(regex=r'^unlike/$', view=views.UnlikeView.as_view(), name='unlike'),
]


