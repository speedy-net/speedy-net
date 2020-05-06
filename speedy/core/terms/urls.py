from django.urls import re_path

from . import views

app_name = 'speedy.core.terms'
urlpatterns = [
    re_path(route=r'', view=views.TermsOfServiceView.as_view(), name='terms_of_service'),
]


