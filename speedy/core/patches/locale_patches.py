from django.conf import settings as django_settings
from django.conf.locale import LANG_INFO
from django.utils import formats
from django.utils.translation.trans_real import translation


def patch():
    formats.FORMAT_SETTINGS = formats.FORMAT_SETTINGS.union(django_settings.FORMAT_SETTINGS)

    # Change translation('pt')._fallback[='en'] to translation('pt')._fallback[='pt-br'].
    # https://forum.djangoproject.com/t/missing-translations-in-pt-portuguese/23993
    # Note: translation('pt').add_fallback(translation('pt-br')) will set translation('pt')._fallback[='en']._fallback[='pt-br']
    translation('pt')._fallback = translation('pt-br')

    translation('zh')._fallback = translation('zh-hant')
    # translation('zh-hant')._fallback = translation('zh-tw')

    translation('no')._fallback = translation('nb')

    # Django has no 'zh' entry in LANG_INFO (only 'zh-hans' / 'zh-hant'), so get_language_info('zh') raises KeyError: "Unknown language code zh."
    # This is used by the about page (about_base.html, which renders the full LANGUAGES list, unlike other pages which use LANGUAGES_IN_HTML).
    # Register 'zh' as Chinese, keeping code='zh' so the zh.speedy.net subdomain routing (LocaleDomainMiddleware) would match.
    LANG_INFO['zh'] = {
        'bidi': False,
        'code': 'zh',
        'name': 'Chinese',
        'name_local': '中文',
    }

