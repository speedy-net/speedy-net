"""
Views of the Speedy Mail Software main app (the main page).
"""
from speedy.core.base.views import StaticMainPageBaseView


class MainPageView(StaticMainPageBaseView):
    """
    View for the Speedy Mail Software main page.
    """
    template_name = 'main/main_page.html'


