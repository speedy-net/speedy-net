"""
Views of the Speedy Composer main app, containing the main page view.
"""
from speedy.core.base.views import StaticMainPageBaseView


class MainPageView(StaticMainPageBaseView):
    """
    View for the Speedy Composer main page.
    """
    template_name = 'main/main_page.html'


