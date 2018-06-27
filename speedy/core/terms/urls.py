from django.conf.urls import url

from . import views

app_name = 'speedy.core.terms'
urlpatterns = [
    url(r'', views.TermsOfServiceView.as_view(), name='terms_of_service'),
]
