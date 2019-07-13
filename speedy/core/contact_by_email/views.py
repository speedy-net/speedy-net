from speedy.core.base.views import StaticContactUsBaseView


class ContactUsView(StaticContactUsBaseView):
    template_name = 'contact_by_email/contact_us.html'


