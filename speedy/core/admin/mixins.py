"""
Mixins of the Speedy Core admin app, which restrict views to admin users.
"""
from rules.contrib.views import LoginRequiredMixin


class OnlyAdminMixin(LoginRequiredMixin):
    """
    View mixin that restricts access to authenticated superuser/staff users only.

    Attributes:
        raise_exception (bool): Always True, so unauthenticated/unauthorized access raises rather than redirecting to login.

    Methods:
        dispatch(self, request, *args, **kwargs): Denies access unless the user is authenticated and both a superuser and staff.
    """
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        """
        Denies access (via handle_no_permission) unless the requesting user is authenticated and is both a superuser and staff; otherwise dispatches normally.

        :param request: The current HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments passed to the parent implementation.
        :param kwargs: Additional keyword arguments passed to the parent implementation.
        :return: The HTTP response.
        :rtype: django.http.HttpResponse
        """
        if (not (request.user.is_authenticated)):
            return self.handle_no_permission()
        if (not ((request.user.is_superuser) and (request.user.is_staff))):
            return self.handle_no_permission()
        return super().dispatch(request=request, *args, **kwargs)


