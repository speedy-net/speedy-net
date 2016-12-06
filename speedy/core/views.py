from django.views import generic
from django.shortcuts import redirect


class StaticMainPageBaseView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        if (request.get_full_path() == "/"):
            return super().get(request=request, *args, **kwargs)
        else:
            return redirect(to="/", permanent=True)

    class Meta:
        abstract = True

