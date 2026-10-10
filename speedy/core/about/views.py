from speedy.core.base.views import StaticAboutBaseView


class AboutView(StaticAboutBaseView):
    """
    View for the static "about" page.
    """
    template_name = 'about/about.html'


