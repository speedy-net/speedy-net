from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.net.profiles.views import UserMixin
from .forms import ImageUploadForm


class UploadView(UserMixin, PermissionRequiredMixin, generic.CreateView):
    permission_required = 'uploads.upload'
    form_class = ImageUploadForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'defaults': {
                'owner': self.user,
            },
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        return redirect(self.user)

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'files': [{
                'uuid': self.object.id,
                'name': self.object.basename,
                'type': 'image',
            }],
        })
