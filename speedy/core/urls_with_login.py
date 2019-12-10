from django.conf.urls import url, include

from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    url(regex=r'^privacy/', view=include('speedy.core.privacy.urls', namespace='privacy')),
    url(regex=r'^terms/', view=include('speedy.core.terms.urls', namespace='terms')),
    url(regex=r'^contact/', view=include('speedy.core.contact_by_form.urls', namespace='contact')),
]


