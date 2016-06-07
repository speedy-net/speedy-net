from modeltranslation.translator import translator, TranslationOptions

from .models import User


class UserTranslationOptions(TranslationOptions):
    fields = ('first_name', 'last_name')


translator.register(User, UserTranslationOptions)
