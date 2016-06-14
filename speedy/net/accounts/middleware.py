from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


class SiteProfileMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        profile = request.user.profile
        if not profile.is_active:
            profile.activate()
            messages.success(request, _('Welcome! This is the first time you visit {}!'.format(settings.SITE_NAME)))
