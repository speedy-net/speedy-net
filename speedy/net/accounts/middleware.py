from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import ugettext_lazy as _, get_language


class InactiveUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_active:
            for url in settings.DONT_REDIRECT_INACTIVE_USER:
                if request.path.startswith(url):
                    return
            return redirect('accounts:activate')


class SiteProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated() or not request.user.is_active:
            return
        profile = request.user.profile
        language_code = get_language()
        if not profile.is_active_for_language(language_code):
            profile.activate(language_code)
            site = Site.objects.get_current()
            messages.success(request, _('Welcome! This is the first time you visit {}!'.format(site.name)))
