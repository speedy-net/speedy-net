"""
Views for the contact by email app of Speedy Core, which define the Contact Us page.
"""
from speedy.core.base.views import StaticContactUsBaseView


class ContactUsView(StaticContactUsBaseView):
    """
    Renders the static contact-us page.

    Attributes:
        template_name (str): The template used to render the contact-us page.
    """
    template_name = 'contact_by_email/contact_us.html'


