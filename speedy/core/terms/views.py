"""
Views of the Speedy Core terms of service app (the terms of service page).
"""
from speedy.core.base.views import StaticTermsOfServiceBaseView


class TermsOfServiceView(StaticTermsOfServiceBaseView):
    """
    View for the static "terms of service" page.
    """
    template_name = 'terms/terms_of_service.html'


