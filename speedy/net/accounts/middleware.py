from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _


class InactiveUserMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_active:
            for url in settings.DONT_REDIRECT_INACTIVE_USER:
                if request.path.startswith(url):
                    return
            return redirect('accounts:activate')


class SiteProfileMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated() or not request.user.is_active:
            return
        profile = request.user.profile
        if not profile.is_active:
            profile.activate()
            messages.success(request, _('Welcome! This is the first time you visit {}!'.format(settings.SITE_NAME)))
