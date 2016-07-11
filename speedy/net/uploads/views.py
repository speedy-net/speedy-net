from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from rules.contrib.views import LoginRequiredMixin

from .forms import ImageUploadForm


class UploadView(LoginRequiredMixin, generic.CreateView):
    form_class = ImageUploadForm

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'defaults': {
                'owner': self.request.user,
            },
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        return redirect(self.request.user)

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'files': [{
                'uuid': self.object.id,
                'name': self.object.basename,
                'type': 'image',
            }],
        })
