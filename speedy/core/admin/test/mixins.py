from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import TestCaseMixin

    class SpeedyCoreAdminLanguageMixin(TestCaseMixin):
        def set_up(self):
            super().set_up()

            _permission_denied_h1_dict = {'en': "Permission Denied", 'fr': "Permission Refusée", 'de': "Erlaubnisse Abgelehnt", 'es': "Permiso Denegado", 'pt': "Permissão Recusada", 'it': "Autorizzazione Negata", 'nl': "Geen Toestemming", 'sv': "Tillträde Nekat", 'ko': "권한 거부됨", 'fi': "Lupa Kielletty", 'he': "ההרשאה נדחתה"}
            _speedy_is_sorry_but_this_page_is_private_alert_dict = {'en': "Speedy is sorry, but this page is private.", 'fr': "Speedy est désolée, mais cette page est privée.", 'de': "Speedy tut es leid, aber diese Seite ist privat.", 'es': "Speedy lo siente, pero esta página es privada.", 'pt': "A Speedy lamenta, mas esta página é privativa.", 'it': "Speedy è spiacente, ma questa pagina è privata.", 'nl': "Het spijt Speedy, maar deze pagina is privé.", 'sv': "Speedy beklagar, men den här sidan är privat.", 'ko': "Speedy에서 죄송하게 생각합니다만, 이 페이지는 비공개입니다.", 'fi': "Speedy pahoittelee, mutta tämä sivu on yksityinen.", 'he': "ספידי מצטערת, אבל הדף הזה פרטי."}
            _speedy_net_profiles_dict = {'en': "Speedy Net Profiles", 'fr': "Profils Speedy Net", 'de': "Speedy Net-Profile", 'es': "Perfiles de Speedy Net", 'pt': "Perfis do Speedy Net", 'it': "Profili Speedy Net", 'nl': "Speedy Net Profielen", 'sv': "Speedy Net-profiler", 'ko': "Speedy Net 프로필", 'fi': "Speedy Net Profiilit", 'he': "פרופילים ספידי נט"}  # ~~~~ TODO: 'fi': check translation of "Speedy Net Profiles" and "Speedy Match Profiles".
            _speedy_match_profiles_dict = {'en': "Speedy Match Profiles", 'fr': "Profils Speedy Match", 'de': "Speedy Match-Profile", 'es': "Perfiles de Speedy Match", 'pt': "Perfis do Speedy Match", 'it': "Profili Speedy Match", 'nl': "Speedy Match Profielen", 'sv': "Speedy Match-profiler", 'ko': "Speedy Match 프로필", 'fi': "Speedy Match Profiilit", 'he': "פרופילים ספידי מץ'"}  # ~~~~ TODO: 'fi': check translation of "Speedy Net Profiles" and "Speedy Match Profiles".

            self._permission_denied_h1 = _permission_denied_h1_dict[self.language_code]
            self._speedy_is_sorry_but_this_page_is_private_alert = _speedy_is_sorry_but_this_page_is_private_alert_dict[self.language_code]
            self._speedy_net_profiles = _speedy_net_profiles_dict[self.language_code]
            self._speedy_match_profiles = _speedy_match_profiles_dict[self.language_code]


