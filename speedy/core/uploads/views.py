from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from rules.contrib.views import LoginRequiredMixin

from .forms import ImageUploadForm


class UploadView(LoginRequiredMixin, generic.CreateView):
    """
    View handling AJAX image uploads for a logged-in user.

    Attributes:
        form_class (type): The form class used to validate and save the uploaded image.

    Methods:
        dispatch(self, request, *args, **kwargs): Dispatch the request, exempting it from CSRF protection.
        get_form_kwargs(self): Add the current user as the default owner of the uploaded image.
        get(self, request, *args, **kwargs): Redirect GET requests to the current user's profile page.
        form_valid(self, form): Save the uploaded image and return a JSON response describing it.
    """
    form_class = ImageUploadForm

    @method_decorator(decorator=csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request, exempting it from CSRF protection (since it is called from a dedicated upload flow).

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response.
        :rtype: django.http.HttpResponse
        """
        return super().dispatch(request=request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Get the keyword arguments for instantiating the form, adding the current user as the default owner.

        :return: The keyword arguments for the form.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'defaults': {
                'owner': self.request.user,
            },
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Redirect GET requests to the current user's profile page, since this view only supports uploads via POST.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the current user's profile page.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.request.user)

    def form_valid(self, form):
        """
        Save the uploaded image and return a JSON response describing it.

        :param form: The validated upload form.
        :type form: speedy.core.uploads.forms.ImageUploadForm
        :return: A JSON response containing the uploaded file's id, name and type.
        :rtype: django.http.JsonResponse
        """
        self.object = form.save()
        return JsonResponse({
            'files': [{
                'uuid': self.object.id,
                'name': self.object.basename,
                'type': 'image',
            }],
        })


