from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.LikeListDefaultRedirectView.as_view(), name='list'),
    url('^to/$', views.LikeListToView.as_view(), name='list_to'),
    url('^from/$', views.LikeListFromView.as_view(), name='list_from'),
    url('^mutual/$', views.LikeListMutualView.as_view(), name='list_mutual'),
    url('^like/$', views.LikeView.as_view(), name='like'),
    url('^unlike/$', views.UnlikeView.as_view(), name='unlike'),
]
