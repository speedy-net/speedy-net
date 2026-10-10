"""
Views of the Speedy Core privacy policy app (the privacy policy page).
"""
from speedy.core.base.views import StaticPrivacyPolicyBaseView


class PrivacyPolicyView(StaticPrivacyPolicyBaseView):
    """
    Renders the static privacy policy page.

    Attributes:
        template_name (str): The template used to render the privacy policy page.
    """
    template_name = 'privacy/privacy_policy.html'


