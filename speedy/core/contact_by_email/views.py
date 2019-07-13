from speedy.core.base.views import StaticContactBaseView


class ContactView(StaticContactBaseView):
    template_name = 'contact_by_email/contact_us.html'


