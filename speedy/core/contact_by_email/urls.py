from django.conf.urls import url

from . import views

app_name = 'speedy.core.contact_by_email'
urlpatterns = [
    url(regex=r'^$', view=views.ContactUsView.as_view(), name='contact_us'),
]
