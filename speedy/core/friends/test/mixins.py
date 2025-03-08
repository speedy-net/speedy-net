from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import TestCaseMixin
    from speedy.core.base.utils import get_both_genders_context_from_genders
    from speedy.core.accounts.models import User


    class SpeedyCoreFriendsLanguageMixin(TestCaseMixin):
        def _you_already_have_friends_error_message_by_user_number_of_friends_and_gender(self, user_number_of_friends, gender):
            return self._you_already_have_friends_error_message_to_format_dict_by_gender[gender].format(user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

        def _this_user_already_has_friends_error_message_by_other_user_number_of_friends_and_both_genders(self, other_user_number_of_friends, both_genders):
            return self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders[both_genders].format(other_user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

        def set_up(self):
            super().set_up()

            _friendship_request_sent_success_message_dict = {'en': 'Friendship request sent.', 'fr': 'Demande d’amitié envoyée.', 'de': "Freundschaftsanfrage gesendet.", 'es': "Solicitud de amistad enviada.", 'pt': "Solicitação de amizade enviada.", 'it': "Richiesta di amicizia inviata.", 'nl': "Vriendschapsverzoek verzonden.", 'sv': "Vänskapsförfrågan skickad.", 'ko': "친구 요청 전송됨.", 'fi': "Ystävyyspyyntö lähetetty.", 'he': 'בקשת חברות נשלחה.'}
            _friendship_request_accepted_success_message_dict = {'en': 'Friendship request accepted.', 'fr': 'Demande d’amitié acceptée.', 'de': "Freundschaftsanfrage akzeptiert.", 'es': "Solicitud de amistad aceptada.", 'pt': "Solicitação de amizade aceita.", 'it': "Richiesta di amicizia accettata.", 'nl': "Vriendschapsverzoek geaccepteerd.", 'sv': "Vänskapsförfrågan accepterad.", 'ko': "친구 요청 수락됨.", 'fi': "Ystävyyspyyntö hyväksytty.", 'he': 'בקשת החברות התקבלה.'}
            _friendship_request_rejected_success_message_dict = {'en': 'Friendship request rejected.', 'fr': 'Demande d’amitié rejetée.', 'de': "Freundschaftsanfrage abgelehnt.", 'es': "Solicitud de amistad rechazada.", 'pt': "Solicitação de amizade recusada.", 'it': "Richiesta di amicizia rifiutata.", 'nl': "Vriendschapsverzoek afgewezen.", 'sv': "Vänskapsförfrågan avvisad.", 'ko': "친구 요청 거부됨.", 'fi': "Ystävyyspyyntö hylätty.", 'he': 'בקשת החברות נדחתה.'}

            _youve_cancelled_your_friendship_request_success_message_dict_by_gender = {
                'en': {
                    **{gender: "You've cancelled your friendship request." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Vous avez annulé votre demande d’amitié." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "Sie haben Ihre Freundschaftsanfrage gelöscht." for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: "Has cancelado tu solicitud de amistad." for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: "Tu cancelaste tua solicitação de amizade." for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "Hai annullato la tua richiesta di amicizia." for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "Je hebt je vriendschapsverzoek geannuleerd." for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "Du har avbrutit din vänskapsförfrågan." for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "친구 요청을 취소했습니다." for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "Olet peruuttanut ystävyyspyyntösi." for gender in User.ALL_GENDERS},
                },
                'he': {
                    **{gender: 'ביטלת את בקשת החברות שלך.' for gender in User.ALL_GENDERS},
                },
            }

            _you_have_removed_this_user_from_friends_success_message_dict_by_gender = {
                'en': {
                    **{gender: "You have removed this user from your friends." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Vous avez supprimé cet utilisateur de vos amis." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "Sie haben diesen Benutzer von Ihren Freunden entfernt." for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "Has eliminado a esta usuaria de tus amigos.",
                    User.GENDER_MALE_STRING: "Has eliminado a este usuario de tus amigos.",
                    User.GENDER_OTHER_STRING: "Has eliminado a este usuario de tus amigos.",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "Tu removeste esta utilizadora dos teus amigos.",
                    User.GENDER_MALE_STRING: "Tu removeste este utilizador dos teus amigos.",
                    User.GENDER_OTHER_STRING: "Tu removeste este utilizador dos teus amigos.",
                },
                'it': {
                    User.GENDER_FEMALE_STRING: "Hai rimosso questa utente dagli amici.",
                    User.GENDER_MALE_STRING: "Hai rimosso questo utente dagli amici.",
                    User.GENDER_OTHER_STRING: "Hai rimosso questo/a utente dagli amici.",
                },
                'nl': {
                    **{gender: "Je hebt deze gebruiker uit je vrienden verwijderd." for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "Du har tagit bort den här användaren från dina vänner." for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "귀하의 친구 목록에서 이 사용자를 지웠습니다." for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "Olet poistanut tämän käyttäjän ystävistäsi." for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "הסרת את המשתמשת הזאת מהחברים שלך.",
                    User.GENDER_MALE_STRING: "הסרת את המשתמש הזה מהחברים שלך.",
                    User.GENDER_OTHER_STRING: "הסרת את המשתמש/ת הזאת מהחברים שלך.",
                },
            }

            _you_already_requested_friendship_from_this_user_error_message_dict_by_gender = {
                'en': {
                    **{gender: "You already requested friendship from this user." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Vous avez déjà demandé à cet utilisateur d’être votre ami(e)." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "Sie haben bereits um die Freundschaft dieses Benutzers gebeten." for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "Ya solicitaste amistad a esta usuaria.",
                    User.GENDER_MALE_STRING: "Ya solicitaste amistad a este usuario.",
                    User.GENDER_OTHER_STRING: "Ya solicitaste amistad a este usuario.",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "Tu já solicitaste a amizade desta utilizadora.",
                    User.GENDER_MALE_STRING: "Tu já solicitaste a amizade deste utilizador.",
                    User.GENDER_OTHER_STRING: "Tu já solicitaste a amizade deste utilizador.",
                },
                'it': {
                    **{gender: "Hai già richiesto l’amicizia a questa utente." for gender in User.ALL_GENDERS},  # ~~~~ TODO: 'it': check translation, should be different per gender like 'es'.
                },
                'nl': {
                    **{gender: "Je hebt al om vriendschap van deze gebruiker gevraagd." for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "Du har redan begärt vänskap från den här användaren." for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "이미 이 사용자로부터 친구를 요청했습니다." for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "Olet jo lähettänyt ystäväpyynnön tälle käyttäjälle." for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "כבר ביקשת חברות מהמשתמשת הזאת.",
                    User.GENDER_MALE_STRING: "כבר ביקשת חברות מהמשתמש הזה.",
                    User.GENDER_OTHER_STRING: "כבר ביקשת חברות מהמשתמש/ת הזאת.",
                },
            }

            _this_user_already_requested_friendship_from_you_error_message_dict_by_gender = {
                'en': {
                    **{gender: "This user already requested friendship from you." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Cet utilisateur a déjà demandé à être votre ami(e)." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "Dieser Benutzer hat bereits um Ihre Freundschaft gebeten." for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "Esta usuaria ya te solicitó amistad.",
                    User.GENDER_MALE_STRING: "Este usuario ya te solicitó amistad.",
                    User.GENDER_OTHER_STRING: "Este usuario ya te solicitó amistad.",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "Esta utilizadora já solicitou a tua amizade.",
                    User.GENDER_MALE_STRING: "Este utilizador já solicitou a tua amizade.",
                    User.GENDER_OTHER_STRING: "Este utilizador já solicitou a tua amizade.",
                },
                'it': {
                    **{gender: "Questa utente ti ha già richiesto l'amicizia." for gender in User.ALL_GENDERS},  # ~~~~ TODO: 'it': check translation, should be different per gender like 'es'.
                },
                'nl': {
                    **{gender: "Deze gebruiker heeft je al om vriendschap gevraagd." for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "Denna användare har redan begärt vänskap från dig." for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "이 사용자는 이미 귀하로부터 친구를 요청했습니다." for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "Tämä käyttäjä on jo lähettänyt sinulle ystäväpyynnön." for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "המשתמשת הזאת כבר ביקשה ממך חברות.",
                    User.GENDER_MALE_STRING: "המשתמש הזה כבר ביקש ממך חברות.",
                    User.GENDER_OTHER_STRING: "המשתמש/ת הזאת כבר ביקש/ה ממך חברות.",
                },
            }

            _you_already_are_friends_with_this_user_error_message_dict_by_both_genders = {
                'en': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "You already are friends with this user." for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'fr': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Vous źtes déją amie avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Vous źtes déją amie avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Vous êtes déjà ami(e) avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Vous źtes déją ami avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Vous źtes déją ami avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Vous źtes déją ami avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Vous êtes déjà ami(e) avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "Vous êtes déjà ami(e) avec cet utilisateur.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Vous êtes déjà ami(e) avec cet utilisateur.",
                },
                'de': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Sie sind mit dieser Benutzerin bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Sie sind mit diesem Benutzer bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Sie sind mit diesem Benutzer bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Sie sind mit diesem Benutzer bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Sie sind mit diesem Benutzer bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Sie sind mit dieser Benutzerin bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Sie sind mit diesem Benutzer bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "Sie sind mit diesem Benutzer bereits befreundet.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Sie sind mit diesem Benutzer bereits befreundet.",
                },
                'es': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Ya eres amiga de esta usuaria.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Ya eres amiga de este usuario.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Ya eres amiga de este usuario.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Ya eres amigo de esta usuaria.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Ya eres amigo de este usuario.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Ya eres amigo de este usuario.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Ya eres amigo de esta usuaria.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "Ya eres amigo de este usuario.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Ya eres amigo de este usuario.",
                },
                'pt': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Tu já és amiga desta utilizadora.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Tu já és amiga deste utilizador.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Tu já és amiga deste utilizador.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Tu já és amigo desta utilizadora.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Tu já és amigo deste utilizador.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Tu já és amigo deste utilizador.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Tu já és amigo desta utilizadora.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "Tu já és amigo deste utilizador.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Tu já és amigo deste utilizador.",
                },
                'it': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Sei già amica di questa utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Sei già amica di questo utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Sei già amica di questo/a utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Sei già amico di questa utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "Sei già amico di questo utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Sei già amico di questo/a utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "Sei già amico/a di questa utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "Sei già amico/a di questo utente.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "Sei già amico/a di questo/a utente.",
                },
                'nl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "Je bent al vrienden met deze gebruiker." for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "Du är redan vän med den här användaren." for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "이미 이 사용자와 친구입니다." for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "Olet jo ystävä tämän käyttäjän kanssa." for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'he': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "את כבר חברה של המשתמשת הזאת.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "את כבר חברה של המשתמש הזה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "את כבר חברה של המשתמש/ת הזאת.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "אתה כבר חבר של המשתמשת הזאת.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "אתה כבר חבר של המשתמש הזה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "אתה כבר חבר של המשתמש/ת הזאת.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "את/ה כבר חבר/ה של המשתמשת הזאת.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "את/ה כבר חבר/ה של המשתמש הזה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "את/ה כבר חבר/ה של המשתמש/ת הזאת.",
                },
            }

            _you_cannot_be_friends_with_yourself_error_message_dict_by_gender = {
                'en': {
                    **{gender: "You cannot be friends with yourself." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "On ne peut pas être ami avec soi-même." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "Sie können nicht mit sich selbst befreundet sein." for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: "No puedes ser amiga de ti misma.",
                    User.GENDER_MALE_STRING: "No puedes ser amigo de ti mismo.",
                    User.GENDER_OTHER_STRING: "No puedes ser amigo de ti mismo.",
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: "Tu não podes ser amiga de ti mesma.",
                    User.GENDER_MALE_STRING: "Tu não podes ser amigo de ti mesmo.",
                    User.GENDER_OTHER_STRING: "Tu não podes ser amigo de ti mesmo.",
                },
                'it': {
                    User.GENDER_FEMALE_STRING: "Non puoi essere amica di te stessa.",
                    User.GENDER_MALE_STRING: "Non puoi essere amica di te stessa.",
                    User.GENDER_OTHER_STRING: "Non puoi essere amico/a di te stesso/a.",
                },
                'nl': {
                    **{gender: "Je kan geen vrienden zijn met jezelf." for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "Du kan inte vara vän med dig själv." for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "나 자신과 친구가 될 수 없습니다." for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "Et voi olla ystävä itsesi kanssa." for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "את לא יכולה להיות חברה של עצמך.",
                    User.GENDER_MALE_STRING: "אתה לא יכול להיות חבר של עצמך.",
                    User.GENDER_OTHER_STRING: "את/ה לא יכול/ה להיות חבר/ה של עצמך.",
                },
            }

            _you_already_have_friends_error_message_to_format_dict_by_gender = {
                'en': {
                    **{gender: "You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: "Vous avez déjà des amis sur {0}. Vous ne pouvez pas avoir plus de {1} ami(e)s sur Speedy Net. Veuillez supprimer des amis avant de continuer." for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: "Sie haben bereits {0} Freunde. Auf Speedy Net können Sie nicht mehr als {1} Freunde haben. Bitte entfernen Sie Freunde, bevor Sie weitermachen." for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: "Ya tienes {0} amigos. No puedes tener más de {1} amigos en Speedy Net. Elimina amigos antes de continuar." for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: "Tu já tens {0} amigos. Não podes ter mais que {1} amigos no Speedy Net. Remova amigos antes de continuar." for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "Hai già {0} amici. Non puoi avere più di {1} amici su Speedy Net. Cortesemente, rimuovi gli amici prima di procedere." for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "Je hebt al {0} vrienden. Je kunt niet meer dan {1} vrienden hebben op Speedy Net. Verwijder vrienden voordat je doorgaat." for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "Du har redan {0} vänner. Du kan inte ha fler än {1} vänner på Speedy Net. Ta bort vänner innan du fortsätter." for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "이미 {0}명의 친구가 있습니다. Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우시기 바랍니다." for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "Sinulla on jo {0} ystävää. Sinulla voi olla enintään {1} ystävää Speedy Netissä. Poista ystävät ennen kuin jatkat." for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסירי חברים/ות לפני שאת ממשיכה.",
                    User.GENDER_MALE_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר חברים/ות לפני שאתה ממשיך.",
                    User.GENDER_OTHER_STRING: "כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר/י חברים/ות לפני שאת/ה ממשיך/ה.",
                },
            }

            _this_user_already_has_friends_error_message_to_format_dict_by_both_genders = {
                'en': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "This user already has {0} friends. She can't have more than {1} friends on Speedy Net. Please ask her to remove friends before you proceed." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "This user already has {0} friends. He can't have more than {1} friends on Speedy Net. Please ask him to remove friends before you proceed." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed." for user_gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Cet utilisateur a déjà {0} amis. Elle ne peut pas avoir plus de {1} amis sur Speedy Net. Demandez-lui de retirer ses amis avant de continuer." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Cet utilisateur a déjà {0} amis. Il ne peut pas avoir plus de {1} amis sur Speedy Net. Demandez-lui de retirer ses amis avant de continuer." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Cet utilisateur a déjà {0} amis. Ils/Elles ne peuvent pas avoir plus de {1} ami(e)s sur Speedy Net. Demandez-leur de retirer leurs amis avant de continuer." for user_gender in User.ALL_GENDERS},
                },
                'de': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Dieser Benutzer hat bereits {0} Freunde. Sie können auf Speedy Net nicht mehr als {1} Freunde haben. Bitte bitten Sie sie, Freunde zu entfernen, bevor Sie weitermachen." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Dieser Benutzer hat bereits {0} Freunde. Sie können auf Speedy Net nicht mehr als {1} Freunde haben. Bitte bitten Sie sie, Freunde zu entfernen, bevor Sie weitermachen." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Dieser Benutzer hat bereits {0} Freunde. Sie können auf Speedy Net nicht mehr als {1} Freunde haben. Bitte bitten Sie sie, Freunde zu entfernen, bevor Sie weitermachen." for user_gender in User.ALL_GENDERS},
                },
                'es': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Esta usuaria ya tiene {0} amigos. No puede tener más de {1} amigos en Speedy Net. Pídele que elimine a sus amigos antes de continuar." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Este usuario ya tiene {0} amigos. No puede tener más de {1} amigos en Speedy Net. Pídele que elimine a sus amigos antes de continuar." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Este usuario ya tiene {0} amigos. No pueden tener más de {1} amigos en Speedy Net. Pídeles que eliminen a tus amigos antes de continuar." for user_gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Esse usuário já tem {0} amigos. Ela não pode ter mais de {1} amigos na Speedy Net. Peça que ela remova amigos antes de continuar." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Esse usuário já tem {0} amigos. Ele não pode ter mais de {1} amigos na Speedy Net. Peça que ele remova amigos antes de continuar." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Esse usuário já tem {0} amigos. Eles não podem ter mais de {1} amigos na Speedy Net. Peça que eles removam amigos antes de continuar." for user_gender in User.ALL_GENDERS},
                },
                'it': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Questo utente ha già {0} amici. Non può avere più di {1} amici su Speedy Net. Chiedile di rimuovere gli amici prima di procedere." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Questo utente ha già {0} amici. Non può avere più di {1} amici su Speedy Net. Chiedigli di rimuovere gli amici prima di procedere." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Questo utente ha già {0} amici. Non possono avere più di {1} amici su Speedy Net. Chiedi loro di rimuovere gli amici prima di procedere." for user_gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Deze gebruiker heeft al {0} vrienden. Ze mag niet meer dan {1} vrienden hebben op Speedy Net. Vraag haar om vrienden te verwijderen voordat je verder gaat." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Deze gebruiker heeft al {0} vrienden. Hij mag niet meer dan {1} vrienden hebben op Speedy Net. Vraag hem om vrienden te verwijderen voordat je verder gaat." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Deze gebruiker heeft al {0} vrienden. Ze kunnen niet meer dan {1} vrienden hebben op Speedy Net. Vraag ze alsjeblieft om vrienden te verwijderen voordat je verder gaat." for user_gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Den här användaren har redan {0} vänner. Hon kan inte ha mer än {1} vänner på Speedy Net. Be henne att ta bort vänner innan du fortsätter." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Den här användaren har redan {0} vänner. Han kan inte ha mer än {1} vänner på Speedy Net. Be honom att ta bort vänner innan du fortsätter." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Den här användaren har redan {0} vänner. De kan inte ha mer än {1} vänner på Speedy Net. Be dem att ta bort vänner innan du fortsätter." for user_gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "이 사용자에게는 이미 {0}명의 친구가 있습니다. 해당 사용자는 Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우도록 요청하세요." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "이 사용자에게는 이미 {0}명의 친구가 있습니다. 해당 사용자는 Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우도록 요청하세요." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "이 사용자에게는 이미 {0}명의 친구가 있습니다. 해당 사용자는 Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우도록 요청하세요." for user_gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "Tällä käyttäjällä on jo {0} ystävää. Hänellä ei voi olla yli {1} ystävää Speedy Netissä. Pyydä häntä poistamaan ystävät ennen kuin jatkat." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "Tällä käyttäjällä on jo {0} ystävää. Hänellä ei voi olla yli {1} ystävää Speedy Netissä. Pyydä häntä poistamaan ystävät ennen kuin jatkat." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Tällä käyttäjällä on jo {0} ystävää. Heillä ei voi olla enempää kuin {1} ystävää Speedy Netissä. Pyydä heitä poistamaan ystävät ennen kuin jatkat." for user_gender in User.ALL_GENDERS},
                },
                'he': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנה להסיר חברים/ות לפני שאת ממשיכה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנו להסיר חברים/ות לפני שאת ממשיכה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנו/ה להסיר חברים/ות לפני שאת ממשיכה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנה להסיר חברים/ות לפני שאתה ממשיך.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): "למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנו להסיר חברים/ות לפני שאתה ממשיך.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנו/ה להסיר חברים/ות לפני שאתה ממשיך.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): "למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנה להסיר חברים/ות לפני שאת/ה ממשיך/ה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): "למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנו להסיר חברים/ות לפני שאת/ה ממשיך/ה.",
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): "למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנו/ה להסיר חברים/ות לפני שאת/ה ממשיך/ה.",
                },
            }

            self._friendship_request_sent_success_message = _friendship_request_sent_success_message_dict[self.language_code]
            self._friendship_request_accepted_success_message = _friendship_request_accepted_success_message_dict[self.language_code]
            self._friendship_request_rejected_success_message = _friendship_request_rejected_success_message_dict[self.language_code]

            self._youve_cancelled_your_friendship_request_success_message_dict_by_gender = _youve_cancelled_your_friendship_request_success_message_dict_by_gender[self.language_code]
            self._you_have_removed_this_user_from_friends_success_message_dict_by_gender = _you_have_removed_this_user_from_friends_success_message_dict_by_gender[self.language_code]
            self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender = _you_already_requested_friendship_from_this_user_error_message_dict_by_gender[self.language_code]
            self._this_user_already_requested_friendship_from_you_error_message_dict_by_gender = _this_user_already_requested_friendship_from_you_error_message_dict_by_gender[self.language_code]
            self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders = _you_already_are_friends_with_this_user_error_message_dict_by_both_genders[self.language_code]
            self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender = _you_cannot_be_friends_with_yourself_error_message_dict_by_gender[self.language_code]
            self._you_already_have_friends_error_message_to_format_dict_by_gender = _you_already_have_friends_error_message_to_format_dict_by_gender[self.language_code]
            self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders = _this_user_already_has_friends_error_message_to_format_dict_by_both_genders[self.language_code]

            self.assertSetEqual(set1=set(self._youve_cancelled_your_friendship_request_success_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._you_have_removed_this_user_from_friends_success_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._this_user_already_requested_friendship_from_you_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders.keys()), set2={get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender) for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS})
            self.assertSetEqual(set1=set(self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._you_already_have_friends_error_message_to_format_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders.keys()), set2={get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender) for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS})

            self.assertEqual(first=len(set(self._youve_cancelled_your_friendship_request_success_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._you_have_removed_this_user_from_friends_success_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._this_user_already_requested_friendship_from_you_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders.keys())), second=3 ** 2)
            self.assertEqual(first=len(set(self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._you_already_have_friends_error_message_to_format_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders.keys())), second=3 ** 2)


