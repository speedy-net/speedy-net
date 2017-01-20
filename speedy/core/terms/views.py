from speedy.core.base.views import StaticTermsOfServiceBaseView


class TermsOfServiceView(StaticTermsOfServiceBaseView):
    template_name = '../templates/terms/terms_of_service.html'

