from speedy.core.base.views import StaticTermsOfServiceBaseView


class TermsOfServiceView(StaticTermsOfServiceBaseView):
    """
    View for the static "terms of service" page.
    """
    template_name = 'terms/terms_of_service.html'


