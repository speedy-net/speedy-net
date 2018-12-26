from django.conf import settings

from speedy.core.base.utils import conditional_method_or_class as conditional_test


exclude_on_site = lambda site_id: conditional_test(conditional_function=lambda: (not (settings.SITE_ID == site_id)))
exclude_on_speedy_net = exclude_on_site(site_id=settings.SPEEDY_NET_SITE_ID)
exclude_on_speedy_match = exclude_on_site(site_id=settings.SPEEDY_MATCH_SITE_ID)
exclude_on_speedy_composer = exclude_on_site(site_id=settings.SPEEDY_COMPOSER_SITE_ID)
exclude_on_speedy_mail_software = exclude_on_site(site_id=settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

only_on_site = lambda site_id: conditional_test(conditional_function=lambda: (settings.SITE_ID == site_id))
only_on_speedy_net = only_on_site(site_id=settings.SPEEDY_NET_SITE_ID)
only_on_speedy_match = only_on_site(site_id=settings.SPEEDY_MATCH_SITE_ID)
only_on_speedy_composer = only_on_site(site_id=settings.SPEEDY_COMPOSER_SITE_ID)
only_on_speedy_mail_software = only_on_site(site_id=settings.SPEEDY_MAIL_SOFTWARE_SITE_ID)

only_on_sites = lambda site_id_list: conditional_test(conditional_function=lambda: (settings.SITE_ID in site_id_list))
only_on_sites_with_login = only_on_sites(site_id_list=settings.SITES_WITH_LOGIN)


