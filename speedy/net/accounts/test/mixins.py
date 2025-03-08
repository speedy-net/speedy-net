from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import TestCaseMixin
    from speedy.core.accounts.models import User


    class SpeedyNetAccountsLanguageMixin(TestCaseMixin):
        def _delete_account_form_all_the_required_fields_keys(self):
            return [field_name.format(language_code=self.language_code) for field_name in ['password', 'delete_my_account_text']]

        def _delete_account_form_all_the_required_fields_are_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=self._delete_account_form_all_the_required_fields_keys())

        def _delete_my_account_text_is_required_errors_dict(self):
            return self._all_the_required_fields_are_required_errors_dict_by_required_fields(required_fields=['delete_my_account_text'])

        def _invalid_delete_my_account_text_errors_dict_by_gender(self, gender):
            return {'delete_my_account_text': [self._invalid_delete_my_account_text_error_message_dict_by_gender[gender]]}

        def set_up(self):
            super().set_up()

            _yes_delete_my_account_text_dict = {'en': 'Yes. Delete my account.', 'fr': 'Oui. Supprimer mon compte.', 'de': 'Ja. Lösche mein Konto.', 'es': 'Sí. Elimina mi cuenta.', 'pt': 'Sim. Excluir minha conta.', 'it': 'Sì. Elimina il mio account.', 'nl': 'Ja. Verwijder mijn account.', 'sv': 'Ja. Ta bort mitt konto.', 'ko': '네. 내 계정을 삭제하세요.', 'fi': 'Kyllä. Poista tilini.', 'he': 'כן. מחקו את החשבון שלי.'}

            _delete_account_text_dict_by_gender = {
                'en': {
                    **{gender: 'Delete Account' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Supprimer le compte' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Konto löschen' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Eliminar cuenta' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Excluir conta' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Elimina account' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Account verwijderen' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Radera konto' for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: '계정 삭제' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Poista tili' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "מחקי את החשבון",
                    User.GENDER_MALE_STRING: "מחק את החשבון",
                    User.GENDER_OTHER_STRING: "מחק/י את החשבון",
                },
            }

            _are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender = {
                'en': {
                    **{gender: 'Are you sure you want to delete your Speedy Net account? This is permanent and irreversible. Deleting your Speedy Net account will also delete your Speedy Match account. If you are sure, type "Yes. Delete my account." in this field, exactly and case sensitive.' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Êtes-vous sûr de vouloir supprimer votre compte Speedy Net ? C'est permanent et irréversible. La suppression de votre compte Speedy Net entraîne également la suppression de votre compte Speedy Match. Si vous êtes sûr, tapez « Oui. Supprimer mon compte. » dans ce champ, avec précision et distinction majuscules/minuscules." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sind Sie sicher, dass Sie Ihr Speedy Net-Konto löschen möchten? Dies ist dauerhaft und irreversibel. Durch das Löschen Ihres Speedy Net-Kontos wird auch Ihr Speedy Match-Konto gelöscht. Wenn Sie sich sicher sind, geben Sie „Ja. Lösche mein Konto.“ in dieses Feld, genau und beachte Groß- und Kleinschreibung.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: '¿Estás seguro de que deseas eliminar tu cuenta de Speedy Net? Esto es permanente e irreversible. Al eliminar tu cuenta de Speedy Net también se eliminará tu cuenta de Speedy Match. Si estás seguro, escribe «Sí. Elimina mi cuenta.» en este campo, exactamente y sin distinción entre mayúsculas y minúsculas.' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Tem certeza de que deseja excluir sua conta Speedy Net? Isso é permanente e irreversível. Excluir sua conta Speedy Net também excluirá sua conta Speedy Match. Se tiver certeza, digite “Sim. Excluir minha conta.” neste campo, com exatidão e distinção entre maiúsculas e minúsculas.' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "Sei sicuro di voler eliminare il tuo account Speedy Net? Questo è permanente e irreversibile. L'eliminazione del tuo account Speedy Net eliminerà anche il tuo account Speedy Match. Se sei sicuro, digita «Sì. Elimina il mio account.» in questo campo, esattamente e con distinzione tra maiuscole e minuscole." for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Weet je zeker dat je je Speedy Net-account wilt verwijderen? Dit is permanent en onomkeerbaar. Als u uw Speedy Net-account verwijdert, wordt ook uw Speedy Match-account verwijderd. Als je het zeker weet, typ dan „Ja. Verwijder mijn account.” in dit veld, precies en hoofdlettergevoelig.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Är du säker på att du vill ta bort ditt Speedy Net-konto? Detta är permanent och irreversibelt. Om du tar bort ditt Speedy Net-konto raderas också ditt Speedy Match-konto. Om du är säker, skriv ”Ja. Ta bort mitt konto.” i det här fältet, exakt och skiftlägeskänsligt.' for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: 'Speedy Net 계정을 삭제하시겠습니까? 이는 영구적이며 되돌릴 수 없습니다. Speedy Net 계정을 삭제하면 Speedy Match 계정도 삭제됩니다. 확실하다면 "네. 내 계정을 삭제하세요."라고 입력하세요. 이 필드에서는 정확하게 대소문자를 구분합니다.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Haluatko varmasti poistaa Speedy Net -tilisi? Tämä on pysyvää ja peruuttamatonta. Speedy Net -tilisi poistaminen poistaa myös Speedy Match -tilisi. Jos olet varma, kirjoita ”Kyllä. Poista tilini.” tässä kentässä, täsmälleen ja isot kirjaimet huomioon.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "האם את בטוחה שברצונך למחוק את החשבון שלך בספידי נט? זה קבוע ובלתי הפיך. מחיקת החשבון שלך בספידי נט תמחק גם את החשבון שלך בספידי מץ'. אם את בטוחה, הקלידי \"כן. מחקו את החשבון שלי.\" בשדה זה, בדיוק.",
                    User.GENDER_MALE_STRING: "האם אתה בטוח שברצונך למחוק את החשבון שלך בספידי נט? זה קבוע ובלתי הפיך. מחיקת החשבון שלך בספידי נט תמחק גם את החשבון שלך בספידי מץ'. אם אתה בטוח, הקלד \"כן. מחקו את החשבון שלי.\" בשדה זה, בדיוק.",
                    User.GENDER_OTHER_STRING: "האם את/ה בטוח/ה שברצונך למחוק את החשבון שלך בספידי נט? זה קבוע ובלתי הפיך. מחיקת החשבון שלך בספידי נט תמחק גם את החשבון שלך בספידי מץ'. אם את/ה בטוח/ה, הקלד/י \"כן. מחקו את החשבון שלי.\" בשדה זה, בדיוק.",
                },
            }

            _permanently_delete_your_speedy_net_account_text_dict_by_gender = {
                'en': {
                    **{gender: 'Permanently delete your Speedy Net account' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Supprimer définitivement votre compte Speedy Net' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Löschen Sie Ihr Speedy Net Konto dauerhaft' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Eliminar permanentemente tu cuenta de Speedy Net' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Excluir permanentemente sua conta no Speedy Net' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Elimina definitivamente il tuo account Speedy Net' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Verwijder je Speedy Net-account permanent' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Radera ditt Speedy Net-konto permanent' for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: 'Speedy Net 계정을 영구적으로 삭제하세요' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Poista Speedy Net-tilisi pysyvästi' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "מחקי את החשבון שלך בספידי נט לצמיתות",
                    User.GENDER_MALE_STRING: "מחק את החשבון שלך בספידי נט לצמיתות",
                    User.GENDER_OTHER_STRING: "מחק/י את החשבון שלך בספידי נט לצמיתות",
                },
            }

            _your_speedy_net_and_speedy_match_accounts_have_been_deleted_message_dict_by_gender = {
                'en': {
                    **{gender: 'Your Speedy Net and Speedy Match accounts have been deleted. Thank you for using Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Vos comptes Speedy Net et Speedy Match ont été supprimés. Merci d'avoir choisi Speedy Net." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Ihre Speedy Net- und Speedy Match-Konten wurden gelöscht. Vielen Dank, dass Sie Speedy Net verwenden.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Se eliminaron tus cuentas de Speedy Net y Speedy Match. Gracias por usar Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Suas contas Speedy Net e Speedy Match foram excluídas. Obrigado por usar o Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'I tuoi account Speedy Net e Speedy Match sono stati eliminati. Grazie per aver scelto Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Je Speedy Net- en Speedy Match-accounts zijn verwijderd. Bedankt voor het gebruik van Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Dina Speedy Net- och Speedy Match-konton har raderats. Tack för att du använder Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: '귀하의 Speedy Net 및 Speedy Match 계정이 삭제되었습니다. Speedy Net을(를) 이용해 주셔서 감사합니다.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Speedy Net- ja Speedy Match -tilisi on poistettu. Kiitos, että käytit Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    **{gender: "החשבונות שלך בספידי נט וספידי מץ' נמחקו. תודה שהשתמשת בספידי נט." for gender in User.ALL_GENDERS},
                },
            }

            _invalid_delete_my_account_text_error_message_dict_by_gender = _are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender

            self._yes_delete_my_account_text = _yes_delete_my_account_text_dict[self.language_code]

            self._delete_account_text_dict_by_gender = _delete_account_text_dict_by_gender[self.language_code]
            self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender = _are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender[self.language_code]
            self._permanently_delete_your_speedy_net_account_text_dict_by_gender = _permanently_delete_your_speedy_net_account_text_dict_by_gender[self.language_code]
            self._invalid_delete_my_account_text_error_message_dict_by_gender = _invalid_delete_my_account_text_error_message_dict_by_gender[self.language_code]
            self._your_speedy_net_and_speedy_match_accounts_have_been_deleted_message_dict_by_gender = _your_speedy_net_and_speedy_match_accounts_have_been_deleted_message_dict_by_gender[self.language_code]

            self.assertSetEqual(set1=set(self._delete_account_text_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._permanently_delete_your_speedy_net_account_text_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._invalid_delete_my_account_text_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._your_speedy_net_and_speedy_match_accounts_have_been_deleted_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))

            self.assertEqual(first=len(set(self._delete_account_text_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._are_you_sure_you_want_to_delete_your_speedy_net_account_text_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._permanently_delete_your_speedy_net_account_text_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._invalid_delete_my_account_text_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._your_speedy_net_and_speedy_match_accounts_have_been_deleted_message_dict_by_gender.keys())), second=3)


