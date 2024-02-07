import logging

from django.conf import settings as django_settings
from django.contrib.auth import logout as django_auth_logout
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sites.models import Site
from django.utils.timezone import now
from django.utils.translation import get_language, gettext_lazy as _

logger = logging.getLogger(__name__)


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
            if (request.user.is_deleted):
                django_auth_logout(request=request)
                return redirect(to='accounts:index')
            update_last_visit = True
            for url in django_settings.IGNORE_LAST_VISIT:
                if (request.path.startswith(url)):
                    update_last_visit = False
            if (update_last_visit):
                request.user.profile.update_last_visit()
                request.user.update_last_ip_address_used(request=request)
            if (not (request.user.has_confirmed_email_or_registered_now)):
                if (not ((request.user.is_superuser) or (request.user.is_staff))):
                    _user_is_active = (request.user.is_active or request.user.speedy_net_profile.is_active)
                    request.user.speedy_net_profile.deactivate()
                    if (not (_user_is_active == (request.user.is_active or request.user.speedy_net_profile.is_active))):
                        speedy_net_site = Site.objects.get(pk=django_settings.SPEEDY_NET_SITE_ID)
                        language_code = get_language()
                        logger.info('User {user} was deactivated on {site_name} - no confirmed email (registered {registered_days_ago} days ago), language_code={language_code}.'.format(
                            site_name=_(speedy_net_site.name),
                            user=request.user,
                            registered_days_ago=(now() - request.user.date_created).days,
                            language_code=language_code,
                        ))
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


