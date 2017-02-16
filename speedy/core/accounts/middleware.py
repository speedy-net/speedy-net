from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class SiteProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.profile.update_last_visit()
            if not request.user.has_verified_email:
                request.user.profile.deactivate()
            if not request.user.profile.is_active:
                for url in settings.DONT_REDIRECT_INACTIVE_USER:
                    if request.path.startswith(url):
                        return
                return redirect(to='accounts:activate')
