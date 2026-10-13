"""
URL configuration for the Speedy Mail Software main page.
"""
from django.urls import re_path

from speedy.core.base.views import AppendSlashOrMainPageRedirectView

from . import views

app_name = 'speedy.mail.main'
urlpatterns = [
    re_path(route=r'^$', view=views.MainPageView.as_view(), name='main_page'),
    re_path(route=r'^(?!.*/$)', view=AppendSlashOrMainPageRedirectView.as_view(), name='append_slash'),
    re_path(route=r'', view=views.MainPageView.as_view(), name='main_page_catch_all'),
]


