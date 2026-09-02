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

            _friendship_request_sent_success_message_dict = {'en': 'Friendship request sent.', 'fr': 'Demande d’amitié envoyée.', 'de': 'Freundschaftsanfrage gesendet.', 'es': 'Solicitud de amistad enviada.', 'pt': 'Pedido de amizade enviado.', 'it': 'Richiesta di amicizia inviata.', 'nl': 'Vriendschapsverzoek verzonden.', 'ja': 'フレンドシップリクエストが送信されました。', 'ru': 'Запрос на дружбу отправлен.', 'zh': '已發送好友請求。', 'pl': 'Wysłano prośbę o dodanie do znajomych.', 'fa': 'درخواست دوستی ارسال شد.', 'he': 'בקשת חברות נשלחה.', 'ko': '친구 요청 전송됨.', 'ar': 'تم إرسال طلب الصداقة.', 'id': 'Permintaan pertemanan terkirim.', 'uk': 'Запит на дружбу надіслано.', 'tr': 'Arkadaşlık isteği gönderildi.', 'vi': 'Yêu cầu kết bạn đã được gửi.', 'cs': 'Žádost o přátelství odeslána.', 'sv': 'Vänskapsförfrågan skickad.', 'fi': 'Ystävyyspyyntö lähetetty.', 'hu': 'Barátsági felkérés elküldve.', 'th': 'ส่งคำขอเป็นเพื่อนแล้ว', 'el': 'Το αίτημα φιλίας εστάλη.', 'ms': 'Permintaan persahabatan dihantar.', 'sr': 'Захтев за пријатељство је послат.', 'ro': 'Solicitare de prietenie trimisă.', 'bn': 'বন্ধুত্বের অনুরোধ পাঠানো হয়েছে।', 'ca': "S'ha enviat una sol·licitud d'amistat.", 'no': 'Venneforespørsel sendt.', 'bg': 'Молбата за приятелство е изпратена.', 'da': 'Venskabsanmodning sendt.', 'sk': 'Žiadosť o priateľstvo bola odoslaná.', 'hi': 'मित्रता अनुरोध भेजा गया.', 'et': 'Sõbrakutse saadetud.', 'hr': 'Zahtjev za prijateljstvo poslan.', 'az': 'Dostluq istəyi göndərildi.'}

            _friendship_request_accepted_success_message_dict = {'en': 'Friendship request accepted.', 'fr': 'Demande d’amitié acceptée.', 'de': 'Freundschaftsanfrage akzeptiert.', 'es': 'Solicitud de amistad aceptada.', 'pt': 'Pedido de amizade aceita.', 'it': 'Richiesta di amicizia accettata.', 'nl': 'Vriendschapsverzoek geaccepteerd.', 'ja': 'フレンド申請受け付けました。', 'ru': 'Запрос на дружбу принят.', 'zh': '已接受好友請求。', 'pl': 'Prośba o przyjaźń została zaakceptowana.', 'fa': 'درخواست دوستی پذیرفته شد', 'he': 'בקשת החברות התקבלה.', 'ko': '친구 요청 수락됨.', 'ar': 'تم قبول طلب الصداقة.', 'id': 'Permintaan pertemanan diterima.', 'uk': 'Запит на дружбу прийнято.', 'tr': 'Arkadaşlık isteği kabul edildi.', 'vi': 'Yêu cầu kết bạn được chấp nhận.', 'cs': 'Žádost o přátelství přijata.', 'sv': 'Vänskapsförfrågan accepterad.', 'fi': 'Ystävyyspyyntö hyväksytty.', 'hu': 'Baráti felkérés elfogadva.', 'th': 'ยอมรับคำขอเป็นเพื่อนแล้ว', 'el': 'Αίτημα φιλίας δεκτό.', 'ms': 'Permintaan persahabatan diterima.', 'sr': 'Захтев за пријатељство је прихваћен.', 'ro': 'Cerere de prietenie acceptată.', 'bn': 'বন্ধুত্বের অনুরোধ গৃহীত।', 'ca': "S'ha acceptat la sol·licitud d'amistat.", 'no': 'Venneforespørsel akseptert.', 'bg': 'Молбата за приятелство е приета.', 'da': 'Venskabsanmodning accepteret.', 'sk': 'Žiadosť o priateľstvo bola prijatá.', 'hi': 'मित्रता अनुरोध स्वीकार किया गया.', 'et': 'Sõbrakutse vastu võetud.', 'hr': 'Zahtjev za prijateljstvo prihvaćen.', 'az': 'Dostluq istəyi qəbul edildi.'}
            _friendship_request_rejected_success_message_dict = {'en': 'Friendship request rejected.', 'fr': 'Demande d’amitié rejetée.', 'de': 'Freundschaftsanfrage abgelehnt.', 'es': 'Solicitud de amistad rechazada.', 'pt': 'Pedido de amizade recusada.', 'it': 'Richiesta di amicizia rifiutata.', 'nl': 'Vriendschapsverzoek afgewezen.', 'ja': 'フレンド申請は拒否されました。', 'ru': 'Запрос на дружбу отклонен.', 'zh': '好友請求被拒絕。', 'pl': 'Prośba o przyjaźń została odrzucona.', 'fa': 'درخواست دوستی رد شد.', 'he': 'בקשת החברות נדחתה.', 'ko': '친구 요청 거부됨.', 'ar': 'تم رفض طلب الصداقة.', 'id': 'Permintaan pertemanan ditolak.', 'uk': 'Запит на дружбу відхилено.', 'tr': 'Arkadaşlık isteği reddedildi.', 'vi': 'Yêu cầu kết bạn bị từ chối.', 'cs': 'Žádost o přátelství zamítnuta.', 'sv': 'Vänskapsförfrågan avvisad.', 'fi': 'Ystävyyspyyntö hylätty.', 'hu': 'A barátkozási kérelmet elutasították.', 'th': 'คำขอเป็นเพื่อนถูกปฏิเสธ', 'el': 'Το αίτημα φιλίας απορρίφθηκε.', 'ms': 'Permintaan persahabatan ditolak.', 'sr': 'Захтев за пријатељство је одбијен.', 'ro': 'Solicitarea de prietenie a fost respinsă.', 'bn': 'বন্ধুত্বের অনুরোধ প্রত্যাখ্যান করা হয়েছে।', 'ca': "S'ha rebutjat la sol·licitud d'amistat.", 'no': 'Venneforespørsel avvist.', 'bg': 'Молбата за приятелство е отхвърлена.', 'da': 'Venskabsanmodning afvist.', 'sk': 'Žiadosť o priateľstvo bola zamietnutá.', 'hi': 'मित्रता अनुरोध अस्वीकृत.', 'et': 'Sõprustaotlus lükati tagasi.', 'hr': 'Zahtjev za prijateljstvo odbijen.', 'az': 'Dostluq istəyi rədd edildi.'}

            _youve_cancelled_your_friendship_request_success_message_dict_by_gender = {
                'en': {
                    **{gender: "You've cancelled your friendship request." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Vous avez annulé votre demande d’amitié.' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sie haben Ihre Freundschaftsanfrage gelöscht.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Has cancelado tu solicitud de amistad.' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Cancelaste o teu pedido de amizade.' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Hai annullato la tua richiesta di amicizia.' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Je hebt je vriendschapsverzoek geannuleerd.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: '友達申請をキャンセルしました。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Вы отменили свой запрос на дружбу.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '您已取消好友請求。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Anulowałeś swoją prośbę o dodanie do znajomych.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شما درخواست دوستی خود را لغو کردید.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    **{gender: 'ביטלת את בקשת החברות שלך.' for gender in User.ALL_GENDERS},
                },
                'ko': {
                    **{gender: '친구 요청을 취소했습니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'لقد ألغيت طلب الصداقة الخاص بك.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Anda telah membatalkan permintaan pertemanan Anda.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Ви скасували свій запит на дружбу.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Arkadaşlık isteğinizi iptal ettiniz.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn đã hủy yêu cầu kết bạn của mình.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Zrušili jste svou žádost o přátelství.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Du har avbrutit din vänskapsförfrågan.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Olet peruuttanut ystävyyspyyntösi.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Lemondtad a barátkozási kérelmed.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณได้ยกเลิกคำขอเป็นเพื่อนแล้ว' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Ακυρώσατε το αίτημα φιλίας σας.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Anda telah membatalkan permintaan persahabatan anda.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Отказали сте свој захтев за пријатељство.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Ți-ai anulat cererea de prietenie.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনি আপনার বন্ধুত্বের অনুরোধ বাতিল করেছেন।' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: "Has cancel·lat la teva sol·licitud d'amistat." for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Du har kansellert venneforespørselen din.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Отменихте заявката си за приятелство.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Du har annulleret din venskabsanmodning.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Zrušili ste svoju žiadosť o priateľstvo.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'आपने अपना मित्रता अनुरोध रद्द कर दिया है.' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Olete oma sõbrakutse tühistanud.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Otkazali ste svoj zahtjev za prijateljstvo.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Dostluq istəyinizi ləğv etdiniz.' for gender in User.ALL_GENDERS},
                },
            }

            _you_have_removed_this_user_from_friends_success_message_dict_by_gender = {
                'en': {
                    **{gender: 'You have removed this user from your friends.' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Vous avez supprimé cet utilisateur de vos amis.' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sie haben diesen Benutzer von Ihren Freunden entfernt.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: 'Has eliminado a esta usuaria de tus amigos.',
                    User.GENDER_MALE_STRING: 'Has eliminado a este usuario de tus amigos.',
                    User.GENDER_OTHER_STRING: 'Has eliminado a este usuario de tus amigos.',
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: 'Tu removeste esta utilizadora dos teus amigos.',
                    User.GENDER_MALE_STRING: 'Tu removeste este utilizador dos teus amigos.',
                    User.GENDER_OTHER_STRING: 'Tu removeste este utilizador dos teus amigos.',
                },
                'it': {
                    User.GENDER_FEMALE_STRING: 'Hai rimosso questa utente dagli amici.',
                    User.GENDER_MALE_STRING: 'Hai rimosso questo utente dagli amici.',
                    User.GENDER_OTHER_STRING: 'Hai rimosso questo/a utente dagli amici.',
                },
                'nl': {
                    **{gender: 'Je hebt deze gebruiker uit je vrienden verwijderd.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'このユーザーを友達から削除しました。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Вы удалили этого пользователя из друзей.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '您已將此使用者從您的好友中刪除。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Usunąłeś tego użytkownika ze swoich znajomych.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شما این کاربر را از دوستان خود حذف کرده اید.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'הסרת את המשתמשת הזאת מהחברים שלך.',
                    User.GENDER_MALE_STRING: 'הסרת את המשתמש הזה מהחברים שלך.',
                    User.GENDER_OTHER_STRING: 'הסרת את המשתמש/ת הזאת מהחברים שלך.',
                },
                'ko': {
                    **{gender: '귀하의 친구 목록에서 이 사용자를 지웠습니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'لقد قمت بإزالة هذا المستخدم من أصدقائك.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Anda telah menghapus pengguna ini dari teman Anda.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Ви видалили цього користувача зі своїх друзів.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Bu kullanıcıyı arkadaşlarınızdan kaldırdınız.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn đã xóa người dùng này khỏi bạn bè của bạn.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Odebrali jste tohoto uživatele ze svých přátel.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Du har tagit bort den här användaren från dina vänner.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Olet poistanut tämän käyttäjän ystävistäsi.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Eltávolította ezt a felhasználót az ismerősei közül.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณได้ลบผู้ใช้รายนี้ออกจากเพื่อนของคุณแล้ว' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Έχετε αφαιρέσει αυτόν τον χρήστη από τους φίλους σας.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Anda telah mengalih keluar pengguna ini daripada rakan anda.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Уклонили сте овог корисника из својих пријатеља.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Ai eliminat acest utilizator dintre prietenii tăi.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনি এই ব্যবহারকারীকে আপনার বন্ধুদের থেকে সরিয়ে দিয়েছেন৷' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Heu eliminat aquest usuari dels vostres amics.' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Du har fjernet denne brukeren fra vennene dine.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Премахнахте този потребител от вашите приятели.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Du har fjernet denne bruger fra dine venner.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Tohto používateľa ste odstránili zo svojich priateľov.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'आपने इस उपयोगकर्ता को अपने मित्रों से हटा दिया है.' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Olete selle kasutaja oma sõprade hulgast eemaldanud.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Uklonili ste ovog korisnika iz svojih prijatelja.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Bu istifadəçini dostlarınızdan sildiniz.' for gender in User.ALL_GENDERS},
                },
            }

            _you_already_requested_friendship_from_this_user_error_message_dict_by_gender = {
                'en': {
                    **{gender: 'You already requested friendship from this user.' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Vous avez déjà demandé à cet utilisateur d’être votre ami(e).' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sie haben bereits um die Freundschaft dieses Benutzers gebeten.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: 'Ya solicitaste amistad a esta usuaria.',
                    User.GENDER_MALE_STRING: 'Ya solicitaste amistad a este usuario.',
                    User.GENDER_OTHER_STRING: 'Ya solicitaste amistad a este usuario.',
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: 'Tu já solicitaste a amizade desta utilizadora.',
                    User.GENDER_MALE_STRING: 'Tu já solicitaste a amizade deste utilizador.',
                    User.GENDER_OTHER_STRING: 'Tu já solicitaste a amizade deste utilizador.',
                },
                'it': {
                    **{gender: 'Hai già richiesto l’amicizia a questa utente.' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Je hebt al om vriendschap van deze gebruiker gevraagd.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'あなたはすでにこのユーザーにフレンドシップをリクエストしました。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Вы уже запросили дружбу у этого пользователя.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '您已經要求與該用戶建立友誼。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Już poprosiłeś tego użytkownika o przyjaźń.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شما قبلاً از این کاربر درخواست دوستی کرده اید.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'כבר ביקשת חברות מהמשתמשת הזאת.',
                    User.GENDER_MALE_STRING: 'כבר ביקשת חברות מהמשתמש הזה.',
                    User.GENDER_OTHER_STRING: 'כבר ביקשת חברות מהמשתמש/ת הזאת.',
                },
                'ko': {
                    **{gender: '이미 이 사용자로부터 친구를 요청했습니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'لقد طلبت الصداقة بالفعل من هذا المستخدم.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Anda sudah meminta pertemanan dari pengguna ini.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Ви вже запитували дружбу від цього користувача.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Bu kullanıcıdan zaten arkadaşlık talebinde bulundunuz.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn đã yêu cầu kết bạn từ người dùng này.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Od tohoto uživatele jste již požádali o přátelství.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Du har redan begärt vänskap från den här användaren.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Olet jo lähettänyt ystäväpyynnön tälle käyttäjälle.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Már kértél barátságot ettől a felhasználótól.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณได้ร้องขอมิตรภาพจากผู้ใช้รายนี้แล้ว' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Έχετε ήδη ζητήσει φιλία από αυτόν τον χρήστη.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Anda sudah meminta persahabatan daripada pengguna ini.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Већ сте тражили пријатељство од овог корисника.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Ai cerut deja prietenia acestui utilizator.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনি ইতিমধ্যে এই ব্যবহারকারীর কাছ থেকে বন্ধুত্বের অনুরোধ করেছেন৷' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Ja has sol·licitat amistat a aquest usuari.' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Du har allerede bedt om vennskap fra denne brukeren.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Вече поискахте приятелство от този потребител.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Du har allerede anmodet om venskab fra denne bruger.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Od tohto používateľa ste už požiadali o priateľstvo.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'आप पहले ही इस उपयोगकर्ता से मित्रता का अनुरोध कर चुके हैं।' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Olete sellelt kasutajalt juba sõprust taotlenud.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Već ste zatražili prijateljstvo od ovog korisnika.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Siz artıq bu istifadəçiyə dostluq istəyi göndərmisiniz.' for gender in User.ALL_GENDERS},
                },
            }

            _this_user_already_requested_friendship_from_you_error_message_dict_by_gender = {
                'en': {
                    **{gender: 'This user already requested friendship from you.' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Cet utilisateur a déjà demandé à être votre ami(e).' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Dieser Benutzer hat bereits um Ihre Freundschaft gebeten.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: 'Esta usuaria ya te solicitó amistad.',
                    User.GENDER_MALE_STRING: 'Este usuario ya te solicitó amistad.',
                    User.GENDER_OTHER_STRING: 'Este usuario ya te solicitó amistad.',
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: 'Esta utilizadora já solicitou a tua amizade.',
                    User.GENDER_MALE_STRING: 'Este utilizador já solicitou a tua amizade.',
                    User.GENDER_OTHER_STRING: 'Este utilizador já solicitou a tua amizade.',
                },
                'it': {
                    **{gender: "Questa utente ti ha già richiesto l'amicizia." for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Deze gebruiker heeft je al om vriendschap gevraagd.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'このユーザーはすでにあなたにフレンドシップをリクエストしています。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Этот пользователь уже запросил у вас дружбу.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '該用戶已要求與您建立友誼。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Ten użytkownik poprosił Cię już o przyjaźń.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'این کاربر قبلاً از شما درخواست دوستی کرده است.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'המשתמשת הזאת כבר ביקשה ממך חברות.',
                    User.GENDER_MALE_STRING: 'המשתמש הזה כבר ביקש ממך חברות.',
                    User.GENDER_OTHER_STRING: 'המשתמש/ת הזאת כבר ביקש/ה ממך חברות.',
                },
                'ko': {
                    **{gender: '이 사용자는 이미 귀하로부터 친구를 요청했습니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'هذا المستخدم طلب صداقتك بالفعل.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Pengguna ini sudah meminta pertemanan dari Anda.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Цей користувач уже запросив дружбу з вами.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Bu kullanıcı zaten sizden arkadaşlık talebinde bulundu.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Người dùng này đã yêu cầu kết bạn từ bạn.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Tento uživatel od vás již požádal o přátelství.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Denna användare har redan begärt vänskap från dig.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Tämä käyttäjä on jo lähettänyt sinulle ystäväpyynnön.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Ez a felhasználó már barátságot kért tőled.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'ผู้ใช้รายนี้ร้องขอมิตรภาพจากคุณแล้ว' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Αυτός ο χρήστης έχει ήδη ζητήσει φιλία από εσάς.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Pengguna ini telah meminta persahabatan daripada anda.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Овај корисник је већ затражио пријатељство од вас.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Acest utilizator a cerut deja prietenie de la tine.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'এই ব্যবহারকারী ইতিমধ্যেই আপনার কাছ থেকে বন্ধুত্বের অনুরোধ করেছে৷' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: "Aquest usuari ja t'ha sol·licitat amistat." for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Denne brukeren har allerede bedt om vennskap fra deg.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Този потребител вече поиска приятелство от вас.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Denne bruger har allerede anmodet om venskab fra dig.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Tento používateľ už od vás požiadal o priateľstvo.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'यह उपयोगकर्ता पहले ही आपसे मित्रता का अनुरोध कर चुका है.' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'See kasutaja on juba sinult sõprust taotlenud.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Ovaj korisnik je već zatražio prijateljstvo od vas.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Bu istifadəçi sizə artıq dostluq istəyi göndərib.' for gender in User.ALL_GENDERS},
                },
            }

            _you_already_are_friends_with_this_user_error_message_dict_by_both_genders = {
                'en': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'You already are friends with this user.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'fr': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Vous źtes déją amie avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Vous źtes déją amie avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Vous êtes déjà ami(e) avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Vous źtes déją ami avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Vous źtes déją ami avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Vous źtes déją ami avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Vous êtes déjà ami(e) avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Vous êtes déjà ami(e) avec cet utilisateur.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Vous êtes déjà ami(e) avec cet utilisateur.',
                },
                'de': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Sie sind mit dieser Benutzerin bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Sie sind mit diesem Benutzer bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Sie sind mit diesem Benutzer bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Sie sind mit diesem Benutzer bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Sie sind mit diesem Benutzer bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Sie sind mit dieser Benutzerin bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Sie sind mit diesem Benutzer bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Sie sind mit diesem Benutzer bereits befreundet.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Sie sind mit diesem Benutzer bereits befreundet.',
                },
                'es': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Ya eres amiga de esta usuaria.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Ya eres amiga de este usuario.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Ya eres amiga de este usuario.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Ya eres amigo de esta usuaria.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Ya eres amigo de este usuario.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Ya eres amigo de este usuario.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Ya eres amigo de esta usuaria.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Ya eres amigo de este usuario.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Ya eres amigo de este usuario.',
                },
                'pt': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Tu já és amiga desta utilizadora.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Tu já és amiga deste utilizador.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Tu já és amiga deste utilizador.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Tu já és amigo desta utilizadora.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Tu já és amigo deste utilizador.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Tu já és amigo deste utilizador.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Tu já és amigo desta utilizadora.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Tu já és amigo deste utilizador.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Tu já és amigo deste utilizador.',
                },
                'it': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Sei già amica di questa utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Sei già amica di questo utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Sei già amica di questo/a utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Sei già amico di questa utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Sei già amico di questo utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Sei già amico di questo/a utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'Sei già amico/a di questa utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): 'Sei già amico/a di questo utente.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'Sei già amico/a di questo/a utente.',
                },
                'nl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Je bent al vrienden met deze gebruiker.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'あなたはすでにこのユーザーと友達です。' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Вы уже дружите с этим пользователем.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): '您已經是該使用者的朋友。' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Jesteś już znajomym tego użytkownika.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'شما قبلاً با این کاربر دوست هستید.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'he': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'את כבר חברה של המשתמשת הזאת.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'את כבר חברה של המשתמש הזה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'את כבר חברה של המשתמש/ת הזאת.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'אתה כבר חבר של המשתמשת הזאת.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'אתה כבר חבר של המשתמש הזה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'אתה כבר חבר של המשתמש/ת הזאת.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'את/ה כבר חבר/ה של המשתמשת הזאת.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): 'את/ה כבר חבר/ה של המשתמש הזה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'את/ה כבר חבר/ה של המשתמש/ת הזאת.',
                },
                'ko': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): '이미 이 사용자와 친구입니다.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'أنت بالفعل صديق لهذا المستخدم.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'id': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Anda sudah berteman dengan pengguna ini.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Ви вже є друзями цього користувача.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Bu kullanıcıyla zaten arkadaşsınız.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Bạn đã là bạn bè với người dùng này.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'S tímto uživatelem jste již přáteli.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Du är redan vän med den här användaren.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Olet jo ystävä tämän käyttäjän kanssa.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Ön már barátja ezzel a felhasználóval.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'th': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'คุณเป็นเพื่อนกับผู้ใช้รายนี้แล้ว' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'el': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Είστε ήδη φίλοι με αυτόν τον χρήστη.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Anda sudah berkawan dengan pengguna ini.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Већ сте пријатељи са овим корисником.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Sunteți deja prieten cu acest utilizator.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'আপনি ইতিমধ্যেই এই ব্যবহারকারীর বন্ধু।' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): "Ja sou amic d'aquest usuari." for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'no': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Du er allerede venner med denne brukeren.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Вие вече сте приятели с този потребител.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'da': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Du er allerede venner med denne bruger.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'S týmto používateľom ste už priatelia.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'आप पहले से ही इस उपयोगकर्ता के मित्र हैं.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'et': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Olete selle kasutajaga juba sõbrad.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Već ste prijatelji s ovim korisnikom.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
                'az': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=other_user_gender): 'Siz artıq bu istifadəçi ilə dostsunuz.' for other_user_gender in User.ALL_GENDERS for user_gender in User.ALL_GENDERS},
                },
            }

            _you_cannot_be_friends_with_yourself_error_message_dict_by_gender = {
                'en': {
                    **{gender: 'You cannot be friends with yourself.' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'On ne peut pas être ami avec soi-même.' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sie können nicht mit sich selbst befreundet sein.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    User.GENDER_FEMALE_STRING: 'No puedes ser amiga de ti misma.',
                    User.GENDER_MALE_STRING: 'No puedes ser amigo de ti mismo.',
                    User.GENDER_OTHER_STRING: 'No puedes ser amigo de ti mismo.',
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: 'Tu não podes ser amiga de ti mesma.',
                    User.GENDER_MALE_STRING: 'Tu não podes ser amigo de ti mesmo.',
                    User.GENDER_OTHER_STRING: 'Tu não podes ser amigo de ti mesmo.',
                },
                'it': {
                    User.GENDER_FEMALE_STRING: 'Non puoi essere amica di te stessa.',
                    User.GENDER_MALE_STRING: 'Non puoi essere amica di te stessa.',
                    User.GENDER_OTHER_STRING: 'Non puoi essere amico/a di te stesso/a.',
                },
                'nl': {
                    **{gender: 'Je kan geen vrienden zijn met jezelf.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: '自分自身と友達になることはできません。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Вы не можете дружить сами с собой.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '你無法與自己成為朋友。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Nie możesz być przyjacielem samego siebie.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شما نمی توانید با خودتان دوست باشید.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'את לא יכולה להיות חברה של עצמך.',
                    User.GENDER_MALE_STRING: 'אתה לא יכול להיות חבר של עצמך.',
                    User.GENDER_OTHER_STRING: 'את/ה לא יכול/ה להיות חבר/ה של עצמך.',
                },
                'ko': {
                    **{gender: '나 자신과 친구가 될 수 없습니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'لا يمكنك أن تكون صديقًا لنفسك.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Anda tidak bisa berteman dengan diri sendiri.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Ти не можеш дружити сам із собою.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Kendinizle arkadaş olamazsınız.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn không thể làm bạn với chính mình.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Nemůžete být sami se sebou přáteli.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Du kan inte vara vän med dig själv.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Et voi olla ystävä itsesi kanssa.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Nem lehetsz barátod magaddal.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณไม่สามารถเป็นเพื่อนกับตัวเองได้' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Δεν μπορείς να είσαι φίλος με τον εαυτό σου.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Anda tidak boleh berkawan dengan diri sendiri.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Не можете бити пријатељи сами са собом.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Nu poți fi prieten cu tine însuți.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনি নিজের সাথে বন্ধু হতে পারবেন না।' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'No pots ser amic de tu mateix.' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Du kan ikke være venn med deg selv.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Не можете да бъдете приятели със себе си.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Du kan ikke være venner med dig selv.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Nemôžete byť sami so sebou priateľmi.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'आप स्वयं से मित्र नहीं बन सकते.' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Sa ei saa iseendaga sõber olla.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Ne možete sami sebi biti prijatelji.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Özünüzlə dost ola bilməzsiniz.' for gender in User.ALL_GENDERS},
                },
            }

            _you_already_have_friends_error_message_to_format_dict_by_gender = {
                'en': {
                    **{gender: "You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed." for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Vous avez déjà des amis sur {0}. Vous ne pouvez pas avoir plus de {1} ami(e)s sur Speedy Net. Veuillez supprimer des amis avant de continuer.' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Sie haben bereits {0} Freunde. Auf Speedy Net können Sie nicht mehr als {1} Freunde haben. Bitte entfernen Sie Freunde, bevor Sie weitermachen.' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Ya tienes {0} amigos. No puedes tener más de {1} amigos en Speedy Net. Elimina amigos antes de continuar.' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Tu já tens {0} amigos. Não podes ter mais que {1} amigos no Speedy Net. Remova amigos antes de continuar.' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Hai già {0} amici. Non puoi avere più di {1} amici su Speedy Net. Cortesemente, rimuovi gli amici prima di procedere.' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Je hebt al {0} vrienden. Je kunt niet meer dan {1} vrienden hebben op Speedy Net. Verwijder vrienden voordat je doorgaat.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'あなたにはすでに{0}人の友達がいます。 では、{1} 人以上の友達を持つことはできません Speedy Net 。続行する前に友達を削除してください。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'У вас уже есть {0} друзей. В у вас не может быть более {1} друзей. Speedy Net Пожалуйста, удалите друзей, прежде чем продолжить.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '您已經有 {0} 個朋友。您在 上的好友不能超過 Speedy Net {1} 個。請先刪除好友，然後再繼續。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Masz już {0} znajomych. W nie możesz mieć więcej niż {1} znajomych Speedy Net. Zanim będziesz kontynuować, usuń znajomych.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شما قبلاً {0} دوست دارید. شما نمی توانید بیش از {1} دوست در Speedy Net داشته باشید. لطفا قبل از ادامه دوستان را حذف کنید.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסירי חברים/ות לפני שאת ממשיכה.',
                    User.GENDER_MALE_STRING: 'כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר חברים/ות לפני שאתה ממשיך.',
                    User.GENDER_OTHER_STRING: 'כבר יש לך {0} חברות וחברים. לא יכולים להיות לך יותר מ-{1} חברות וחברים בספידי נט. אנא הסר/י חברים/ות לפני שאת/ה ממשיך/ה.',
                },
                'ko': {
                    **{gender: '이미 {0}명의 친구가 있습니다. Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우시기 바랍니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'لديك بالفعل {0} أصدقاء. لا يمكن أن يكون لديك أكثر من {1} من الأصدقاء Speedy Net على سبيدي نت. الرجاء إزالة الأصدقاء قبل المتابعة.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Anda sudah memiliki {0} teman. Anda tidak boleh memiliki lebih dari {1} teman di Speedy Net. Harap hapus teman sebelum Anda melanjutkan.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'У вас уже є {0} друзів. Ви не можете мати більше ніж {1} друзів у Speedy Net. Перш ніж продовжити, видаліть друзів.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: "Zaten {0} arkadaşınız var. 'te {1}'den fazla arkadaşınız olamaz. Devam Speedy Net etmeden önce lütfen arkadaşlarınızı kaldırın." for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn đã có {0} bạn bè. Bạn không thể có nhiều hơn {1} bạn bè trên Speedy Net. Vui lòng xóa bạn bè trước khi bạn tiếp tục.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Již máte {0} přátel. Na nemůžete mít více než {1} přátel Speedy Net. Než budete pokračovat, odeberte přátele.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Du har redan {0} vänner. Du kan inte ha fler än {1} vänner på Speedy Net. Ta bort vänner innan du fortsätter.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Sinulla on jo {0} ystävää. Sinulla voi olla enintään {1} ystävää Speedy Netissä. Poista ystävät ennen kuin jatkat.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Már van {0} barátod. Legfeljebb {1} barátod lehet a Speedy Neten. Kérjük, távolítsa el az ismerőseit, mielőtt folytatná.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณมีเพื่อน {0} แล้ว คุณไม่สามารถมีเพื่อนได้มากกว่า {1} คนบน Speedy Net กรุณาลบเพื่อนก่อนที่จะดำเนินการต่อ' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Έχετε ήδη {0} φίλους. Δεν μπορείτε να έχετε περισσότερους από {1} φίλους στο Speedy Net. Καταργήστε φίλους πριν προχωρήσετε.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Anda sudah mempunyai {0} rakan. Anda tidak boleh mempunyai lebih daripada {1} rakan di Speedy Net. Sila alih keluar rakan sebelum anda meneruskan.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: "You already have {0} friends. You can't have more than {1} friends on Speedy Net. Please remove friends before you proceed." for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Ai deja {0} prieteni. Nu puteți avea mai mult de {1} prieteni pe Speedy Net. Vă rugăm să eliminați prietenii înainte de a continua.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনার ইতিমধ্যেই {0} বন্ধু আছে৷ স্পিডি নেটে আপনার {1} এর বেশি বন্ধু থ Speedy Net াকতে পারে না। আপনি এগিয়ে যাওয়ার আগে বন্ধুদের সরান.' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Ja tens {0} amics. No pots tenir més de {1} amics a Speedy Net. Si us plau, elimineu els amics abans de continuar.' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Du har allerede {0} venner. Du kan ikke ha mer enn {1} venner på Speedy Net. Fjern venner før du fortsetter.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Вече имате {0} приятели. Не можете да имате повече от {1} приятели в Speedy Net. Моля, премахнете приятели, преди да продължите.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Du har allerede {0} venner. Du kan ikke have mere end {1} venner på Speedy Net. Fjern venligst venner, før du fortsætter.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Už máte {0} priateľov. V službe nemôžete mať viac ako {1} priateľov Speedy Net. Pred pokračovaním odstráňte priateľov.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'आपके पास पहले से ही {0} मित्र हैं। स्पीडी नेट पर आपके {1} से अधिक मित्र नह Speedy Net ीं हो सकते। कृपया आगे बढ़ने से पहले मित्रों को हटा दें।' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Teil on juba {0} sõpra. Teil võib Speedy Netis olla kuni {1} sõpra. Enne jätkamist eemaldage sõbrad.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Već imaš {0} prijatelja. Ne možete imati više od {1} prijatelja na Speedy Netu. Prije nastavka uklonite prijatelje.' for gender in User.ALL_GENDERS},
                },
                'az': {
                    **{gender: 'Sizin artıq {0} dostunuz var. Speedy Net-də {1}-dən çox dostunuz ola bilməz. Davam etməzdən əvvəl dostlarınızı silin.' for gender in User.ALL_GENDERS},
                },
            }

            _this_user_already_has_friends_error_message_to_format_dict_by_both_genders = {
                'en': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): "This user already has {0} friends. She can't have more than {1} friends on Speedy Net. Please ask her to remove friends before you proceed." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): "This user already has {0} friends. He can't have more than {1} friends on Speedy Net. Please ask him to remove friends before you proceed." for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed." for user_gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Cet utilisateur a déjà {0} amis. Elle ne peut pas avoir plus de {1} amis sur Speedy Net. Demandez-lui de retirer ses amis avant de continuer.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Cet utilisateur a déjà {0} amis. Il ne peut pas avoir plus de {1} amis sur Speedy Net. Demandez-lui de retirer ses amis avant de continuer.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Cet utilisateur a déjà {0} amis. Ils/Elles ne peuvent pas avoir plus de {1} ami(e)s sur Speedy Net. Demandez-leur de retirer leurs amis avant de continuer.' for user_gender in User.ALL_GENDERS},
                },
                'de': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Dieser Benutzer hat bereits {0} Freunde. Sie können auf Speedy Net nicht mehr als {1} Freunde haben. Bitte bitten Sie sie, Freunde zu entfernen, bevor Sie weitermachen.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Dieser Benutzer hat bereits {0} Freunde. Sie können auf Speedy Net nicht mehr als {1} Freunde haben. Bitte bitten Sie sie, Freunde zu entfernen, bevor Sie weitermachen.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Dieser Benutzer hat bereits {0} Freunde. Sie können auf Speedy Net nicht mehr als {1} Freunde haben. Bitte bitten Sie sie, Freunde zu entfernen, bevor Sie weitermachen.' for user_gender in User.ALL_GENDERS},
                },
                'es': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Esta usuaria ya tiene {0} amigos. No puede tener más de {1} amigos en Speedy Net. Pídele que elimine a sus amigos antes de continuar.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Este usuario ya tiene {0} amigos. No puede tener más de {1} amigos en Speedy Net. Pídele que elimine a sus amigos antes de continuar.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Este usuario ya tiene {0} amigos. No pueden tener más de {1} amigos en Speedy Net. Pídeles que eliminen a tus amigos antes de continuar.' for user_gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Esse utilizadora já tem {0} amigos. Ela não pode ter mais de {1} amigos na Speedy Net. Peça que ela remova amigos antes de continuar.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Esse utilizador já tem {0} amigos. Ele não pode ter mais de {1} amigos na Speedy Net. Peça que ele remova amigos antes de continuar.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Esse utilizador já tem {0} amigos. Eles não podem ter mais de {1} amigos na Speedy Net. Peça que eles removam amigos antes de continuar.' for user_gender in User.ALL_GENDERS},
                },
                'it': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Questo utente ha già {0} amici. Non può avere più di {1} amici su Speedy Net. Chiedile di rimuovere gli amici prima di procedere.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Questo utente ha già {0} amici. Non può avere più di {1} amici su Speedy Net. Chiedigli di rimuovere gli amici prima di procedere.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Questo utente ha già {0} amici. Non possono avere più di {1} amici su Speedy Net. Chiedi loro di rimuovere gli amici prima di procedere.' for user_gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Deze gebruiker heeft al {0} vrienden. Ze mag niet meer dan {1} vrienden hebben op Speedy Net. Vraag haar om vrienden te verwijderen voordat je verder gaat.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Deze gebruiker heeft al {0} vrienden. Hij mag niet meer dan {1} vrienden hebben op Speedy Net. Vraag hem om vrienden te verwijderen voordat je verder gaat.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Deze gebruiker heeft al {0} vrienden. Ze kunnen niet meer dan {1} vrienden hebben op Speedy Net. Vraag ze alsjeblieft om vrienden te verwijderen voordat je verder gaat.' for user_gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'このユーザーにはすでに友だちが {0} 人います。Speedy Net では友だちは {1} 人を超えて追加できません。続行する前に、友だちを削除するよう依頼してください。' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'このユーザーにはすでに友だちが {0} 人います。Speedy Net では友だちは {1} 人を超えて追加できません。続行する前に、友だちを削除するよう依頼してください。' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'このユーザーにはすでに {0} 人の友達がいます。 では、{1} 人以上の友達を持つことはできません Speedy Net 。続行する前に、友達を削除するように依頼してください。' for user_gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'У этой пользовательницы уже {0} друзей. Она не может иметь более {1} друзей в Speedy Net. Попросите её удалить друзей, прежде чем продолжить.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'У этого пользователя уже {0} друзей. Он не может иметь более {1} друзей в Speedy Net. Попросите его удалить друзей, прежде чем продолжить.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'У этого пользователя уже есть {0} друзей. У них не может быть более {1} друзей в Speedy Net. Прежде чем продолжить, попросите их удалить друзей.' for user_gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): '该用户已有 {0} 位好友。在 Speedy Net 上，好友数量不能超过 {1} 位。请先让她删除一些好友，然后再继续。' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): '该用户已有 {0} 位好友。在 Speedy Net 上，好友数量不能超过 {1} 位。请先让他删除一些好友，然后再继续。' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): '该用户已经有 {0} 位好友了。在 Speedy Net 上不能拥有超过 {1} 位好友。请让对方先移除一些好友，然后再继续。' for user_gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Ta użytkowniczka ma już {0} znajomych. Nie może mieć więcej niż {1} znajomych w Speedy Net. Poproś ją o usunięcie znajomych, zanim przejdziesz dalej.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Ten użytkownik ma już {0} znajomych. Nie może mieć więcej niż {1} znajomych w Speedy Net. Poproś go o usunięcie znajomych, zanim przejdziesz dalej.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Ten użytkownik ma już {0} znajomych. Nie mogą mieć więcej niż {1} znajomych w Speedy Net. Zanim przejdziesz dalej, poproś ich o usunięcie znajomych.' for user_gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'این کاربر هم\u200cاکنون {0} دوست دارد. او نمی\u200cتواند بیش از {1} دوست در Speedy Net داشته باشد. لطفاً از او بخواهید پیش از ادامه، دوستانی را حذف کند.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'این کاربر هم\u200cاکنون {0} دوست دارد. او نمی\u200cتواند بیش از {1} دوست در Speedy Net داشته باشد. لطفاً از او بخواهید پیش از ادامه، دوستانی را حذف کند.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'این کاربر قبلاً {0} دوست دارد. آنها نمی توانند بیش از {1} دوست در Speedy Net داشته باشند. لطفاً قبل از ادامه، از آنها بخواهید دوستان خود را حذف کنند.' for user_gender in User.ALL_GENDERS},
                },
                'he': {
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנה להסיר חברים/ות לפני שאת ממשיכה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנו להסיר חברים/ות לפני שאת ממשיכה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_FEMALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקשי ממנו/ה להסיר חברים/ות לפני שאת ממשיכה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנה להסיר חברים/ות לפני שאתה ממשיך.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_MALE_STRING): 'למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנו להסיר חברים/ות לפני שאתה ממשיך.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_MALE_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש ממנו/ה להסיר חברים/ות לפני שאתה ממשיך.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_FEMALE_STRING): 'למשתמשת זאת כבר יש {0} חברות וחברים. לא יכולים להיות לה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנה להסיר חברים/ות לפני שאת/ה ממשיך/ה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_MALE_STRING): 'למשתמש זה כבר יש {0} חברות וחברים. לא יכולים להיות לו יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנו להסיר חברים/ות לפני שאת/ה ממשיך/ה.',
                    get_both_genders_context_from_genders(user_gender=User.GENDER_OTHER_STRING, other_user_gender=User.GENDER_OTHER_STRING): 'למשתמש/ת זה כבר יש {0} חברות וחברים. לא יכולים להיות לו/ה יותר מ-{1} חברות וחברים בספידי נט. אנא בקש/י ממנו/ה להסיר חברים/ות לפני שאת/ה ממשיך/ה.',
                },
                'ko': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): '이 사용자에게는 이미 {0}명의 친구가 있습니다. 해당 사용자는 Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우도록 요청하세요.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): '이 사용자에게는 이미 {0}명의 친구가 있습니다. 해당 사용자는 Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우도록 요청하세요.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): '이 사용자에게는 이미 {0}명의 친구가 있습니다. 해당 사용자는 Speedy Net에서 {1}명 이상의 친구를 둘 수 없습니다. 계속하기 전에 친구를 지우도록 요청하세요.' for user_gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'لدى هذه المستخدمة بالفعل {0} من الأصدقاء. لا يمكنها امتلاك أكثر من {1} صديق على Speedy Net. يُرجى أن تطلب منها إزالة أصدقاء قبل المتابعة.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'لدى هذا المستخدم بالفعل {0} من الأصدقاء. لا يمكنه امتلاك أكثر من {1} صديق على Speedy Net. يُرجى أن تطلب منه إزالة أصدقاء قبل المتابعة.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'هذا المستخدم لديه بالفعل {0} أصدقاء. لا يمكن أن يكون لديهم أكثر من {1} من الأصدقاء Speedy Net على سبيدي نت. من فضلك اطلب منهم إزالة الأصدقاء قبل المتابعة.' for user_gender in User.ALL_GENDERS},
                },
                'id': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Pengguna ini sudah memiliki {0} teman. Dia tidak boleh memiliki lebih dari {1} teman di Speedy Net. Harap minta dia menghapus beberapa teman sebelum Anda melanjutkan.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Pengguna ini sudah memiliki {0} teman. Dia tidak boleh memiliki lebih dari {1} teman di Speedy Net. Harap minta dia menghapus beberapa teman sebelum Anda melanjutkan.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Pengguna ini sudah memiliki {0} teman. Mereka tidak boleh memiliki lebih dari {1} teman di Speedy Net. Silakan minta mereka untuk menghapus teman sebelum Anda melanjutkan.' for user_gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Ця користувачка вже має {0} друзів. Вона не може мати більше ніж {1} друзів у Speedy Net. Попросіть її видалити друзів, перш ніж продовжити.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Цей користувач уже має {0} друзів. Він не може мати більше ніж {1} друзів у Speedy Net. Попросіть його видалити друзів, перш ніж продовжити.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'У цього користувача вже є {0} друзів. Вони не можуть мати більше ніж {1} друзів у Speedy Net. Перш ніж продовжити, попросіть їх видалити друзів.' for user_gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Bu kullanıcının zaten {0} arkadaşı var. Speedy Net üzerinde {1} arkadaştan fazlasına sahip olamaz. Lütfen devam etmeden önce arkadaşlarını kaldırmasını isteyin.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Bu kullanıcının zaten {0} arkadaşı var. Speedy Net üzerinde {1} arkadaştan fazlasına sahip olamaz. Lütfen devam etmeden önce arkadaşlarını kaldırmasını isteyin.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "Bu kullanıcının zaten {0} arkadaşı var. 'te {1}'den fazla arkadaşı olamaz Speedy Net. Lütfen devam etmeden önce arkadaşlarını çıkarmalarını isteyin." for user_gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Người dùng này đã có {0} bạn bè. Cô ấy không thể có quá {1} bạn bè trên Speedy Net. Vui lòng yêu cầu cô ấy xóa bớt bạn bè trước khi tiếp tục.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Người dùng này đã có {0} bạn bè. Anh ấy không thể có quá {1} bạn bè trên Speedy Net. Vui lòng yêu cầu anh ấy xóa bớt bạn bè trước khi tiếp tục.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Người dùng này đã có {0} bạn bè. Họ không thể có nhiều hơn {1} bạn bè trên Speedy Net. Hãy yêu cầu họ xóa bạn bè trước khi bạn tiếp tục.' for user_gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Tato uživatelka už má {0} přátel. Na Speedy Net nemůže mít více než {1} přátel. Požádejte ji, aby před pokračováním některé přátele odstranila.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Tento uživatel už má {0} přátel. Na Speedy Net nemůže mít více než {1} přátel. Požádejte ho, aby před pokračováním některé přátele odstranil.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Tento uživatel již má {0} přátel. Na nemohou mít více než {1} přátel. Speedy Net Než budete pokračovat, požádejte je, aby odstranili přátele.' for user_gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Den här användaren har redan {0} vänner. Hon kan inte ha mer än {1} vänner på Speedy Net. Be henne att ta bort vänner innan du fortsätter.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Den här användaren har redan {0} vänner. Han kan inte ha mer än {1} vänner på Speedy Net. Be honom att ta bort vänner innan du fortsätter.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Den här användaren har redan {0} vänner. De kan inte ha mer än {1} vänner på Speedy Net. Be dem att ta bort vänner innan du fortsätter.' for user_gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Tällä käyttäjällä on jo {0} ystävää. Hänellä ei voi olla yli {1} ystävää Speedy Netissä. Pyydä häntä poistamaan ystävät ennen kuin jatkat.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Tällä käyttäjällä on jo {0} ystävää. Hänellä ei voi olla yli {1} ystävää Speedy Netissä. Pyydä häntä poistamaan ystävät ennen kuin jatkat.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Tällä käyttäjällä on jo {0} ystävää. Heillä ei voi olla enempää kuin {1} ystävää Speedy Netissä. Pyydä heitä poistamaan ystävät ennen kuin jatkat.' for user_gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Ennek a felhasználónak már {0} barátja van. A Speedy Net oldalon nem lehet több mint {1} barátja. A folytatás előtt kérje meg, hogy távolítson el barátokat.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Ennek a felhasználónak már {0} barátja van. A Speedy Net oldalon nem lehet több mint {1} barátja. A folytatás előtt kérje meg, hogy távolítson el barátokat.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Ennek a felhasználónak már {0} ismerőse van. Legfeljebb {1} barátjuk lehet a Speedy Neten. Kérje meg őket, hogy távolítsák el az ismerőseiket, mielőtt folytatná.' for user_gender in User.ALL_GENDERS},
                },
                'th': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'ผู้ใช้นี้มีเพื่อนอยู่แล้ว {0} คน เธอไม่สามารถมีเพื่อนได้มากกว่า {1} คนบน Speedy Net กรุณาขอให้เธอลบเพื่อนก่อนดำเนินการต่อ' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'ผู้ใช้นี้มีเพื่อนอยู่แล้ว {0} คน เขาไม่สามารถมีเพื่อนได้มากกว่า {1} คนบน Speedy Net กรุณาขอให้เขาลบเพื่อนก่อนดำเนินการต่อ' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'ผู้ใช้รายนี้มีเพื่อนแล้ว {0} คน พวกเขามีเพื่อนได้ไม่เกิน {1} คนบน Speedy Net โปรดขอให้พวกเขาลบเพื่อนก่อนที่จะดำเนินการต่อ' for user_gender in User.ALL_GENDERS},
                },
                'el': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Αυτή η χρήστρια έχει ήδη {0} φίλους. Δεν μπορεί να έχει περισσότερους από {1} φίλους στο Speedy Net. Παρακαλώ ζητήστε της να αφαιρέσει φίλους πριν συνεχίσετε.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Αυτός ο χρήστης έχει ήδη {0} φίλους. Δεν μπορεί να έχει περισσότερους από {1} φίλους στο Speedy Net. Παρακαλώ ζητήστε του να αφαιρέσει φίλους πριν συνεχίσετε.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Αυτός ο χρήστης έχει ήδη {0} φίλους. Δεν μπορούν να έχουν περισσότερους από {1} φίλους στο Speedy Net. Ζητήστε τους να αφαιρέσουν φίλους πριν προχωρήσετε.' for user_gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Pengguna ini sudah mempunyai {0} rakan. Dia tidak boleh mempunyai lebih daripada {1} rakan di Speedy Net. Sila minta dia membuang beberapa rakan sebelum anda meneruskan.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Pengguna ini sudah mempunyai {0} rakan. Dia tidak boleh mempunyai lebih daripada {1} rakan di Speedy Net. Sila minta dia membuang beberapa rakan sebelum anda meneruskan.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Pengguna ini sudah mempunyai {0} rakan. Mereka tidak boleh mempunyai lebih daripada {1} rakan di Speedy Net. Sila minta mereka mengalih keluar rakan sebelum anda meneruskan.' for user_gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Ова корисница већ има {0} пријатеља. Не може да има више од {1} пријатеља на Speedy Net. Замолите је да уклони пријатеље пре него што наставите.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Овај корисник већ има {0} пријатеља. Не може да има више од {1} пријатеља на Speedy Net. Замолите га да уклони пријатеље пре него што наставите.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): "This user already has {0} friends. They can't have more than {1} friends on Speedy Net. Please ask them to remove friends before you proceed." for user_gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Această utilizatoare are deja {0} prieteni. Ea nu poate avea mai mult de {1} prieteni pe Speedy Net. Vă rugăm să-i cereți să elimine prieteni înainte de a continua.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Acest utilizator are deja {0} prieteni. El nu poate avea mai mult de {1} prieteni pe Speedy Net. Vă rugăm să-i cereți să elimine prieteni înainte de a continua.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Acest utilizator are deja {0} prieteni. Nu pot avea mai mult de {1} prieteni pe Speedy Net. Vă rugăm să le cereți să elimine prietenii înainte de a continua.' for user_gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'এই ব্যবহারকারীর ইতিমধ্যে {0} জন বন্ধু আছে। তিনি Speedy Net-এ {1} জনের বেশি বন্ধু রাখতে পারবেন না। অনুগ্রহ করে এগিয়ে যাওয়ার আগে তাকে কিছু বন্ধু সরাতে বলুন।' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'এই ব্যবহারকারীর ইতিমধ্যে {0} জন বন্ধু আছে। তিনি Speedy Net-এ {1} জনের বেশি বন্ধু রাখতে পারবেন না। অনুগ্রহ করে এগিয়ে যাওয়ার আগে তাকে কিছু বন্ধু সরাতে বলুন।' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'এই ব্যবহারকারীর ইতিমধ্যেই {0} বন্ধু রয়েছে৷ স্পিডি নেটে তাদের {1} এর বেশি বন্ধু থাকত Speedy Net ে পারে না। আপনি এগিয়ে যাওয়ার আগে দয়া করে তাদের বন্ধুদের সরাতে বলুন।' for user_gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Aquesta usuària ja té {0} amics. No pot tenir més de {1} amics a Speedy Net. Si us plau, demana-li que elimini amics abans de continuar.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Aquest usuari ja té {0} amics. No pot tenir més de {1} amics a Speedy Net. Si us plau, demana-li que elimini amics abans de continuar.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Aquest usuari ja té {0} amics. No poden tenir més de {1} amics a Speedy Net. Si us plau, demaneu-los que eliminen els amics abans de continuar.' for user_gender in User.ALL_GENDERS},
                },
                'no': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Denne brukeren har allerede {0} venner. Hun kan ikke ha mer enn {1} venner på Speedy Net. Be henne fjerne venner før du fortsetter.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Denne brukeren har allerede {0} venner. Han kan ikke ha mer enn {1} venner på Speedy Net. Be ham fjerne venner før du fortsetter.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Denne brukeren har allerede {0} venner. Vedkommende kan ikke ha mer enn {1} venner på Speedy Net. Be dem fjerne venner før du fortsetter.' for user_gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Тази потребителка вече има {0} приятели. Тя не може да има повече от {1} приятели в Speedy Net. Моля, помолете я да премахне приятели, преди да продължите.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Този потребител вече има {0} приятели. Той не може да има повече от {1} приятели в Speedy Net. Моля, помолете го да премахне приятели, преди да продължите.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Този потребител вече има {0} приятели. Те не могат да имат повече от {1} приятели в Speedy Net. Моля, помолете ги да премахнат приятели, преди да продължите.' for user_gender in User.ALL_GENDERS},
                },
                'da': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Denne bruger har allerede {0} venner. Hun kan ikke have mere end {1} venner på Speedy Net. Bed hende om at fjerne venner, før du fortsætter.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Denne bruger har allerede {0} venner. Han kan ikke have mere end {1} venner på Speedy Net. Bed ham om at fjerne venner, før du fortsætter.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Denne bruger har allerede {0} venner. De kan ikke have mere end {1} venner på Speedy Net. Bed dem venligst om at fjerne venner, før du fortsætter.' for user_gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Táto používateľka už má {0} priateľov. Na Speedy Net nemôže mať viac ako {1} priateľov. Požiadajte ju, aby pred pokračovaním odstránila priateľov.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Tento používateľ už má {0} priateľov. Na Speedy Net nemôže mať viac ako {1} priateľov. Požiadajte ho, aby pred pokračovaním odstránil priateľov.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Tento používateľ už má {0} priateľov. V službe nemôžu mať viac ako {1} priateľov. Speedy Net Skôr ako budete pokračovať, požiadajte ich, aby odstránili priateľov.' for user_gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'इस उपयोगकर्ता के पास पहले से {0} मित्र हैं। वह Speedy Net पर {1} से अधिक मित्र नहीं रख सकती। कृपया आगे बढ़ने से पहले उसे मित्र हटाने के लिए कहें।' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'इस उपयोगकर्ता के पास पहले से {0} मित्र हैं। वह Speedy Net पर {1} से अधिक मित्र नहीं रख सकता। कृपया आगे बढ़ने से पहले उसे मित्र हटाने के लिए कहें।' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'इस उपयोगकर्ता के पास पहले से ही {0} मित्र हैं। स्पीडी नेट पर उनके {1} से अधिक मित्र Speedy Net नहीं हो सकते। कृपया आगे बढ़ने से पहले उनसे मित्रों को हटाने के लिए कहें।' for user_gender in User.ALL_GENDERS},
                },
                'et': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Sellel kasutajal on juba {0} sõpra. Tal ei tohi Speedy Net platvormil olla rohkem kui {1} sõpra. Palun paluge tal enne jätkamist sõpru eemaldada.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Sellel kasutajal on juba {0} sõpra. Tal ei tohi Speedy Net platvormil olla rohkem kui {1} sõpra. Palun paluge tal enne jätkamist sõpru eemaldada.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Sellel kasutajal on juba {0} sõpra. Neil ei saa Speedy Netis olla rohkem kui {1} sõpra. Enne jätkamist paluge neil sõbrad eemaldada.' for user_gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Ova korisnica već ima {0} prijatelja. Ne može imati više od {1} prijatelja na platformi Speedy Net. Molimo zamolite je da ukloni prijatelje prije nego što nastavite.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Ovaj korisnik već ima {0} prijatelja. Ne može imati više od {1} prijatelja na platformi Speedy Net. Molimo zamolite ga da ukloni prijatelje prije nego što nastavite.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Ovaj korisnik već ima {0} prijatelja. Ne mogu imati više od {1} prijatelja na Speedy Netu. Zamolite ih da uklone prijatelje prije nego nastavite.' for user_gender in User.ALL_GENDERS},
                },
                'az': {
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_FEMALE_STRING): 'Bu istifadəçinin artıq {0} dostu var. Onun Speedy Net-də {1}-dən çox dostu ola bilməz. Davam etməzdən əvvəl ondan dostlarını silməsini xahiş edin.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_MALE_STRING): 'Bu istifadəçinin artıq {0} dostu var. Onun Speedy Net-də {1}-dən çox dostu ola bilməz. Davam etməzdən əvvəl ondan dostlarını silməsini xahiş edin.' for user_gender in User.ALL_GENDERS},
                    **{get_both_genders_context_from_genders(user_gender=user_gender, other_user_gender=User.GENDER_OTHER_STRING): 'Bu istifadəçinin artıq {0} dostu var. Onların Speedy Net-də {1}-dən çox dostu ola bilməz. Davam etməzdən əvvəl onlardan dostlarını silmələrini xahiş edin.' for user_gender in User.ALL_GENDERS},
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


