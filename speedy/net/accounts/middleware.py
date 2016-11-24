from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class InactiveSiteProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.profile.is_active:
            for url in settings.DONT_REDIRECT_INACTIVE_USER:
                if request.path.startswith(url):
                    return
            return redirect('accounts:activate')
