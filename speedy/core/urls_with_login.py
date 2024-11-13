from django.urls import path, include

from speedy.core.urls import app_name, urlpatterns

urlpatterns += [
    path(route='privacy/', view=include(arg='speedy.core.privacy.urls', namespace='privacy')),
    path(route='terms/', view=include(arg='speedy.core.terms.urls', namespace='terms')),
    path(route='contact/', view=include(arg='speedy.core.contact_by_form.urls', namespace='contact')),
]


