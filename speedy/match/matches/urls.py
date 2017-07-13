from django.conf.urls import url

from . import views

urlpatterns = [
    url('^$', views.MatchesListView.as_view(), name='list'),
]
