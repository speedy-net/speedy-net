from speedy.core.base.views import StaticTermsOfServiceBaseView


class TermsOfServiceView(StaticTermsOfServiceBaseView):
    template_name = 'terms/terms_of_service.html'


