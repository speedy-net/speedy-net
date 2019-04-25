from django.conf.urls import url

from . import views

app_name = 'speedy.core.terms'
urlpatterns = [
    url(regex=r'', view=views.TermsOfServiceView.as_view(), name='terms_of_service'),
]


