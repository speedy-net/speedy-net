from django.conf import settings as django_settings


if (django_settings.TESTS):
    class SpeedyCoreAdminLanguageMixin(object):
        def set_up(self):
            super().set_up()

            _permission_denied_h1_dict = {'en': "Permission Denied", 'fr': "Permission Refusée", 'de': "Erlaubnisse Abgelehnt", 'es': "Permiso Denegado", 'pt': "Permissão Recusada", 'he': "ההרשאה נדחתה"}
            _speedy_is_sorry_but_this_page_is_private_alert_dict = {'en': "Speedy is sorry, but this page is private.", 'fr': "Speedy est désolée, mais cette page est privée.", 'de': "Speedy tut es leid, aber diese Seite ist privat.", 'es': "Speedy lo siente, pero esta página es privada.", 'pt': "A Speedy lamenta, mas esta página é privativa.", 'he': "ספידי מצטערת, אבל הדף הזה פרטי."}
            _speedy_net_profiles_dict = {'en': "Speedy Net Profiles", 'fr': "Profils Speedy Net", 'de': "Speedy Net-Profile", 'es': "Perfiles de Speedy Net", 'pt': "Perfis do Speedy Net", 'he': "פרופילים ספידי נט"}
            _speedy_match_profiles_dict = {'en': "Speedy Match Profiles", 'fr': "Profils Speedy Match", 'de': "Speedy Match-Profile", 'es': "Perfiles de Speedy Match", 'pt': "Perfis do Speedy Match", 'he': "פרופילים ספידי מץ'"}

            self._permission_denied_h1 = _permission_denied_h1_dict[self.language_code]
            self._speedy_is_sorry_but_this_page_is_private_alert = _speedy_is_sorry_but_this_page_is_private_alert_dict[self.language_code]
            self._speedy_net_profiles = _speedy_net_profiles_dict[self.language_code]
            self._speedy_match_profiles = _speedy_match_profiles_dict[self.language_code]


