from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.utils import get_both_genders_context_from_genders
    from speedy.core.accounts.models import User


    class SpeedyCoreFriendsLanguageMixin(object):
        def _you_already_have_friends_error_message_by_user_number_of_friends_and_gender(self, user_number_of_friends, gender):
            return self._you_already_have_friends_error_message_to_format_dict_by_gender[gender].format(user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

        def _this_user_already_has_friends_error_message_by_other_user_number_of_friends_and_both_genders(self, other_user_number_of_friends, both_genders):
            return self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders[both_genders].format(other_user_number_of_friends, User.settings.MAX_NUMBER_OF_FRIENDS_ALLOWED)

        def set_up(self):
            super().set_up()

            _friendship_request_sent_success_message_dict = {'en': 'Friendship request sent.', 'fr': 'Demande d’amitié envoyée.', 'de': "Freundschaftsanfrage gesendet.", 'es': "Solicitud de amistad enviada.", 'pt': "Solicitação de amizade enviada.", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'בקשת חברות נשלחה.'}
            _friendship_request_accepted_success_message_dict = {'en': 'Friendship request accepted.', 'fr': 'Demande d’amitié acceptée.', 'de': "Freundschaftsanfrage akzeptiert.", 'es': "Solicitud de amistad aceptada.", 'pt': "Solicitação de amizade aceita.", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'בקשת החברות התקבלה.'}
            _friendship_request_rejected_success_message_dict = {'en': 'Friendship request rejected.', 'fr': 'Demande d’amitié rejetée.', 'de': "Freundschaftsanfrage abgelehnt.", 'es': "Solicitud de amistad rechazada.", 'pt': "Solicitação de amizade recusada.", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'בקשת החברות נדחתה.'}
            _youve_cancelled_your_friendship_request_success_message_dict = {'en': "You've cancelled your friendship request.", 'fr': "Vous avez annulé votre demande d’amitié.", 'de': "Sie haben Ihre Freundschaftsanfrage gelöscht.", 'es': "Has cancelado tu solicitud de amistad.", 'pt': "Tu cancelaste tua solicitação de amizade.", 'it': "_____ # ~~~~ TODO", 'nl': "_____ # ~~~~ TODO", 'sv': "_____ # ~~~~ TODO", 'ko': "_____ # ~~~~ TODO", 'fi': "_____ # ~~~~ TODO", 'he': 'ביטלת את בקשת החברות שלך.'}

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
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
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
                    **{gender: "Tu já solicitaste a amizade deste utilizador." for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
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
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
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
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "_____ # ~~~~ TODO" for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "_____ # ~~~~ TODO" for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "_____ # ~~~~ TODO" for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "_____ # ~~~~ TODO" for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "_____ # ~~~~ TODO" for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
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
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
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
                    User.GENDER_FEMALE_STRING: "Sie haben bereits {0} Freunde. Auf Speedy Net können Sie nicht mehr als {1} Freunde haben. Bitte entfernen Sie Freunde, bevor Sie weitermachen.",
                    User.GENDER_MALE_STRING: "Sie haben bereits {0} Freunde. Auf Speedy Net können Sie nicht mehr als {1} Freundinnen haben. Bitte entfernen Sie Freundinnen, bevor Sie weitermachen.",
                    User.GENDER_OTHER_STRING: "Sie haben bereits {0} Freunde. Auf Speedy Net können Sie nicht mehr als {1} Freunde haben. Bitte entfernen Sie Freunde, bevor Sie weitermachen.",
                },
                'es': {
                    **{gender: "Ya tienes {0} amigos. No puedes tener más de {1} amigos en Speedy Net. Elimina amigos antes de continuar." for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: "Tu já tens {0} amigos. Não podes ter mais que {1} amigos no Speedy Net. Remova amigos antes de continuar." for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: "_____ # ~~~~ TODO" for gender in User.ALL_GENDERS},
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
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "_____ # ~~~~ TODO" for user_gender in User.ALL_GENDERS},
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
            self._youve_cancelled_your_friendship_request_success_message = _youve_cancelled_your_friendship_request_success_message_dict[self.language_code]

            self._you_have_removed_this_user_from_friends_success_message_dict_by_gender = _you_have_removed_this_user_from_friends_success_message_dict_by_gender[self.language_code]
            self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender = _you_already_requested_friendship_from_this_user_error_message_dict_by_gender[self.language_code]
            self._this_user_already_requested_friendship_from_you_error_message_dict_by_gender = _this_user_already_requested_friendship_from_you_error_message_dict_by_gender[self.language_code]
            self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders = _you_already_are_friends_with_this_user_error_message_dict_by_both_genders[self.language_code]
            self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender = _you_cannot_be_friends_with_yourself_error_message_dict_by_gender[self.language_code]
            self._you_already_have_friends_error_message_to_format_dict_by_gender = _you_already_have_friends_error_message_to_format_dict_by_gender[self.language_code]
            self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders = _this_user_already_has_friends_error_message_to_format_dict_by_both_genders[self.language_code]

            self.assertSetEqual(set1=set(self._you_have_removed_this_user_from_friends_success_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._this_user_already_requested_friendship_from_you_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders.keys()), set2={get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender) for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS})
            self.assertSetEqual(set1=set(self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._you_already_have_friends_error_message_to_format_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders.keys()), set2={get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender) for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS})

            self.assertEqual(first=len(set(self._you_have_removed_this_user_from_friends_success_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._you_already_requested_friendship_from_this_user_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._this_user_already_requested_friendship_from_you_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._you_already_are_friends_with_this_user_error_message_dict_by_both_genders.keys())), second=3 ** 2)
            self.assertEqual(first=len(set(self._you_cannot_be_friends_with_yourself_error_message_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._you_already_have_friends_error_message_to_format_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._this_user_already_has_friends_error_message_to_format_dict_by_both_genders.keys())), second=3 ** 2)


