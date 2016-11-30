from django.views import generic


class MainPageView(generic.TemplateView):
    template_name = 'main_page.html'

