from django.conf import settings as django_settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class SiteProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (request.user.is_authenticated):
            if ((request.user.is_superuser) or (request.user.is_staff)):
                redirect_this_user = True
                for url in django_settings.DONT_REDIRECT_ADMIN:
                    if (request.path.startswith(url)):
                        redirect_this_user = False
                if (redirect_this_user):
                    return redirect(to='admin:index')
            update_last_visit = True
            for url in django_settings.IGNORE_LAST_VISIT:
                if (request.path.startswith(url)):
                    update_last_visit = False
            if (update_last_visit):
                request.user.profile.update_last_visit()
            if (not (request.user.has_confirmed_email_or_registered_now)):
                request.user.profile.deactivate()
            if (not (request.user.profile.is_active_and_valid)):
                redirect_this_user = True
                for url in django_settings.DONT_REDIRECT_INACTIVE_USER:
                    if (request.path.startswith(url)):
                        redirect_this_user = False
                if (redirect_this_user):
                    if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
                        if ((request.user.speedy_match_profile.is_active) and (not (request.user.has_confirmed_email))):
                            request.user.speedy_match_profile.validate_profile_and_activate()
                            return redirect(to='accounts:edit_profile_emails')
                        else:
                            if (request.user.is_active):
                                return redirect(to='accounts:activate', step=request.user.speedy_match_profile.activation_step)
                    return redirect(to='accounts:activate')


