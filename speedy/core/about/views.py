"""
Views of the Speedy Core about app, containing the about page view.
"""
from speedy.core.base.views import StaticAboutBaseView


class AboutView(StaticAboutBaseView):
    """
    View for the static "about" page.
    """
    template_name = 'about/about.html'


