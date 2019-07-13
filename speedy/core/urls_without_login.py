from django.conf.urls import url, include

from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    url(regex=r'^contact/', view=include('speedy.core.contact_by_email.urls', namespace='contact')),
]


