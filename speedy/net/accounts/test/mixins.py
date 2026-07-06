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

            _yes_delete_my_account_text_dict = {'en': 'Yes. Delete my account.', 'fr': 'Oui. Supprimer mon compte.', 'de': 'Ja. Lösche mein Konto.', 'es': 'Sí. Elimina mi cuenta.', 'pt': 'Sim. Eliminar a minha conta.', 'it': 'Sì. Elimina il mio account.', 'nl': 'Ja. Verwijder mijn account.', 'ja': 'はい。アカウントを削除してください。', 'ru': 'Да. Удалить мою учетную запись.', 'zh': '是的。刪除我的帳戶。', 'pl': 'Tak. Usuń moje konto.', 'fa': 'بله. اکانت من رو پاک کن', 'he': 'כן. מחקו את החשבון שלי.', 'ko': '네. 내 계정을 삭제하세요.', 'ar': 'نعم. حذف حسابي.', 'id': 'Ya. Hapus akun saya.', 'uk': 'так Видалити мій обліковий запис.', 'tr': 'Evet. Hesabımı sil.', 'vi': 'Đúng. Xóa tài khoản của tôi.', 'cs': 'Ano. Smazat můj účet.', 'sv': 'Ja. Ta bort mitt konto.', 'fi': 'Kyllä. Poista tilini.', 'hu': 'Igen. Fiókom törlése.', 'th': 'ใช่. ลบบัญชีของฉัน', 'el': 'Ναί. Διαγραφή του λογαριασμού μου.', 'ms': 'ya. Padam akaun saya.', 'sr': 'Да. Избриши мој налог.', 'ro': 'Da. Ștergeți contul meu.', 'bn': 'হ্যাঁ। আমার অ্যাকাউন্ট মুছে দিন।', 'ca': 'Sí. Esborra el meu compte.', 'no': 'Ja. Slett kontoen min.', 'bg': 'да Изтрий акаунта ми.', 'da': 'Ja. Slet min konto.', 'sk': 'áno. Odstrániť môj účet.', 'hi': 'हाँ। मेरा एकाउंट हटा दो।', 'et': 'Jah. Kustuta minu konto.', 'hr': 'Da. Izbriši moj račun.'}

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
                    **{gender: 'Eliminar conta' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Elimina account' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Account verwijderen' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'アカウントの削除' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Удалить аккаунт' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '刪除帳戶' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Usuń konto' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'حذف اکانت' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "מחקי את החשבון",
                    User.GENDER_MALE_STRING: "מחק את החשבון",
                    User.GENDER_OTHER_STRING: "מחק/י את החשבון",
                },
                'ko': {
                    **{gender: '계정 삭제' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'حذف الحساب' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Hapus Akun' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Видалити акаунт' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Hesabı Sil' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Xóa tài khoản' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Smazat účet' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Radera konto' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Poista tili' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Fiók törlése lehetőségre' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'ลบบัญชี' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Διαγραφή λογαριασμού' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Padam Akaun' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Избриши налог' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Șterge contul' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'অ্যাকাউন্ট মুছুন' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Suprimeix el compte' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Slett konto' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Изтриване на акаунт' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Slet konto' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Odstrániť účet' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'खाता हटा दो' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Kustuta konto' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Izbriši račun' for gender in User.ALL_GENDERS},
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
                    **{gender: 'Tens a certeza de que pretendes eliminar a tua conta Speedy Net? Isso é permanente e irreversível. Eliminar a tua conta Speedy Net também eliminará a tua conta Speedy Match. Se tiveres a certeza, escreve “Sim. Eliminar a minha conta.” neste campo, com exatidão e distinção entre maiúsculas e minúsculas.' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: "Sei sicuro di voler eliminare il tuo account Speedy Net? Questo è permanente e irreversibile. L'eliminazione del tuo account Speedy Net eliminerà anche il tuo account Speedy Match. Se sei sicuro, digita «Sì. Elimina il mio account.» in questo campo, esattamente e con distinzione tra maiuscole e minuscole." for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Weet je zeker dat je je Speedy Net-account wilt verwijderen? Dit is permanent en onomkeerbaar. Als u uw Speedy Net-account verwijdert, wordt ook uw Speedy Match-account verwijderd. Als je het zeker weet, typ dan „Ja. Verwijder mijn account.” in dit veld, precies en hoofdlettergevoelig.' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'Speedy Net アカウントを削除してもよろしいですか?これは永続的であり、元に戻すことはできません。 アカウントを削除すると Speedy Net 、Speedy Match アカウントも削除されます。間違いがない場合は、「はい。アカウントを削除します。」と入力します。このフィールドでは正確に、大文字と小文字が区別されます。' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Вы уверены, что хотите удалить свою учетную запись Speedy Net? Это навсегда и необратимо. Удаление вашей учетной записи Speedy Net также приведет к удалению вашей учетной записи Speedy Match. Если вы уверены, введите «Да. Удалить мою учетную запись». в этом поле точно и с учетом регистра.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '您確定要刪除您的 Speedy Net 帳戶嗎？這是永久且不可逆轉的。刪除您的 Speedy Net 帳戶也會刪除您的 Speedy Match 帳戶。如果您確定，請輸入「是。刪除我的帳戶」。在此欄位中，完全區分大小寫。' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Czy na pewno chcesz usunąć swoje konto Speedy Net? Jest to trwałe i nieodwracalne. Usunięcie konta Speedy Net spowoduje również usunięcie konta Speedy Match. Jeśli jesteś pewien, wpisz „Tak. Usuń moje konto". w tym polu, dokładnie i rozróżniana jest wielkość liter.' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'آیا مطمئن هستید که می خواهید حساب Speedy Net خود را حذف کنید؟ این دائمی و غیر قابل برگشت است. با حذف حساب Speedy Net، حساب Speedy Match شما نیز حذف می شود. اگر مطمئن هستید، "Yes. Delete my account" را تایپ کنید. در این زمینه دقیقا و حساس به حروف کوچک و بزرگ است.' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "האם את בטוחה שברצונך למחוק את החשבון שלך בספידי נט? זה קבוע ובלתי הפיך. מחיקת החשבון שלך בספידי נט תמחק גם את החשבון שלך בספידי מץ'. אם את בטוחה, הקלידי \"כן. מחקו את החשבון שלי.\" בשדה זה, בדיוק.",
                    User.GENDER_MALE_STRING: "האם אתה בטוח שברצונך למחוק את החשבון שלך בספידי נט? זה קבוע ובלתי הפיך. מחיקת החשבון שלך בספידי נט תמחק גם את החשבון שלך בספידי מץ'. אם אתה בטוח, הקלד \"כן. מחקו את החשבון שלי.\" בשדה זה, בדיוק.",
                    User.GENDER_OTHER_STRING: "האם את/ה בטוח/ה שברצונך למחוק את החשבון שלך בספידי נט? זה קבוע ובלתי הפיך. מחיקת החשבון שלך בספידי נט תמחק גם את החשבון שלך בספידי מץ'. אם את/ה בטוח/ה, הקלד/י \"כן. מחקו את החשבון שלי.\" בשדה זה, בדיוק.",
                },
                'ko': {
                    **{gender: 'Speedy Net 계정을 삭제하시겠습니까? 이는 영구적이며 되돌릴 수 없습니다. Speedy Net 계정을 삭제하면 Speedy Match 계정도 삭제됩니다. 확실하다면 "네. 내 계정을 삭제하세요."라고 입력하세요. 이 필드에서는 정확하게 대소문자를 구분합니다.' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'هل أنت متأكد أنك تريد حذف حساب سبيدي Speedy Net نت الخاص بك؟ وهذا أمر دائم ولا رجعة فيه. سيؤدي حذف حساب سبيدي Speedy Net نت الخاص بك إلى حذف حساب سبيدي ماتش الخاص بك أيض Speedy Match ًا. إذا كنت متأكدًا، فاكتب "نعم. احذف حسابي". في هذا المجال، بدقة وحساسة لحالة الأحرف.' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Apakah Anda yakin ingin menghapus akun Speedy Net Anda? Ini bersifat permanen dan tidak dapat diubah. Menghapus akun Speedy Net Anda juga akan menghapus akun Speedy Match Anda. Jika Anda yakin, ketik "Yes. Hapus akun saya". di bidang ini, persis dan peka huruf besar-kecil.' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Ви впевнені, що хочете видалити свій обліковий запис Speedy Net? Це є постійним і незворотнім. Видалення облікового запису Speedy Net також призведе до видалення облікового запису Speedy Match. Якщо ви впевнені, введіть "Так. Видалити мій обліковий запис". у цьому полі точно та з урахуванням регістру.' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Speedy Net hesabınızı silmek istediğinizden emin misiniz? Bu kalıcıdır ve geri döndürülemez. Speedy Net hesabınızı sildiğinizde Speedy Match hesabınız da silinir. Eminseniz "Evet. Hesabımı sil" yazın. bu alanda tam olarak ve büyük/küçük harfe duyarlıdır.' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Bạn có chắc chắn muốn xóa tài khoản Speedy Net của mình không? Điều này là vĩnh viễn và không thể đảo ngược. Xóa tài khoản Speedy Net của bạn cũng sẽ xóa tài khoản Speedy Match của bạn. Nếu bạn chắc chắn, hãy nhập "Có. Xóa tài khoản của tôi." trong lĩnh vực này, chính xác và phân biệt chữ hoa chữ thường.' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Opravdu chcete smazat svůj účet Speedy Net? To je trvalé a nevratné. Smazáním svého účtu Speedy Net smažete také svůj účet Speedy Match. Pokud jste si jisti, napište "Ano. Smazat můj účet." v této oblasti, přesně a velká a malá písmena.' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Är du säker på att du vill ta bort ditt Speedy Net-konto? Detta är permanent och irreversibelt. Om du tar bort ditt Speedy Net-konto raderas också ditt Speedy Match-konto. Om du är säker, skriv "Ja. Ta bort mitt konto." i det här fältet, exakt och skiftlägeskänsligt.' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Haluatko varmasti poistaa Speedy Net -tilisi? Tämä on pysyvää ja peruuttamatonta. Speedy Net -tilisi poistaminen poistaa myös Speedy Match -tilisi. Jos olet varma, kirjoita "Kyllä. Poista tilini." tässä kentässä, täsmälleen ja isot kirjaimet huomioon.' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Biztos benne, hogy törölni szeretné Speedy Net fiókját? Ez állandó és visszafordíthatatlan. A fiók törlésével a Speedy Speedy Net Match fiók is törlődik. Ha biztos Speedy Match benne, írja be az "Igen. Fiókom törlése" kifejezést. ezen a területen pontosan és a kis- és nagybetűk megkülönböztetésével.' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'คุณแน่ใจหรือไม่ว่าต้องการลบบัญชี Speedy Net ของคุณ? นี่เป็นสิ่งที่ถาวรและไม่สามารถย้อนกลับได้ การลบบัญชี Speedy Net ของคุณจะเป็นการลบบัญชี Speedy Match ของคุณด้วย If you are sure, type "Yes. Delete my account." ในฟิลด์นี้ ทุกประการและคำนึงถึงตัวพิมพ์เล็กและตัวพิมพ์ใหญ่' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Είστε βέβαιοι ότι θέλετε να διαγράψετε τον λογαριασμό σας Speedy Net; Αυτό είναι μόνιμο και μη αναστρέψιμο. Η διαγραφή του λογαριασμού σας στο Speedy Net θα διαγράψει επίσης τον λογαριασμό σας στο Speedy Match. Εάν είστε σίγουροι, πληκτρολογήστε "Ναι. Διαγραφή του λογαριασμού μου". σε αυτόν τον τομέα, ακριβώς και με διάκριση πεζών-κεφαλαίων.' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Adakah anda pasti mahu memadamkan akaun Speedy Net anda? Ini kekal dan tidak boleh dipulihkan. Memadam akaun Speedy Net anda juga akan memadamkan akaun Speedy Match anda. Jika anda pasti, taip "Ya. Padam akaun saya." dalam bidang ini, tepat dan sensitif huruf besar.' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Да ли сте сигурни да желите да избришете свој Speedy Net Спееди Нет налог? Ово је трајно и неповратно. Брисање вашег Спееди Speedy Net Нет налога ће такође избрисати ваш Спееди Матцх налог. Speedy Match Ако сте сигурни, откуцајте „Да. Избриши мој налог". у овом пољу, тачно и осетљиво на велика и мала слова.' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Sigur doriți să vă ștergeți contul Speedy Net? Acest lucru este permanent și ireversibil. Ștergerea contului dvs. Speedy Net va șterge și contul dvs. Speedy Match. Dacă sunteți sigur, introduceți „Da. Ștergeți contul meu". în acest domeniu, exact și cu majuscule și minuscule.' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'আপনি কি আপনার স্পিডি নেট অ্যাকাউন্ট মুছে Speedy Net ফেলার বিষয়ে নিশ্চিত? এটি স্থায়ী এবং অপরিবর্তনীয়। আপনার স্পিডি নেট Speedy Net অ্যাকাউন্ট মুছে দিলে আপনার স্পিডি ম্যাচ অ্যাকাউন্টও মুছে Speedy Match যাবে। আপনি যদি নিশ্চিত হন, টাইপ করুন "হ্যাঁ। আমার অ্যাকাউন্ট মুছুন।" এই ক্ষেত্রে, ঠিক এবং কেস সংবেদনশীল.' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: "Esteu segur que voleu suprimir el vostre compte de Speedy Net? Això és permanent i irreversible. Si suprimiu el vostre compte de Speedy Net, també se suprimirà el vostre compte de Speedy Match. Si n'estàs segur, escriviu \"Sí. Suprimeix el meu compte\". en aquest camp, exactament i distingeix entre majúscules i minúscules." for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Er du sikker på at du vil slette Speedy Net-kontoen din? Dette er permanent og irreversibelt. Sletting av Speedy Net-kontoen din vil også slette Speedy Match-kontoen din. Hvis du er sikker, skriv "Ja. Slett kontoen min." i dette feltet, nøyaktig og skiller mellom store og små bokstaver.' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Сигурни ли сте, че искате да изтриете акаунта си в Speedy Net? Това е постоянно и необратимо. Изтриването на вашия акаунт в Speedy Net ще изтрие и вашия акаунт в Speedy Match. Ако сте сигурни, напишете "Да. Изтрий акаунта ми." в това поле, точно и малки и големи букви.' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Er du sikker på, at du vil slette din Speedy Net-konto? Dette er permanent og irreversibelt. Sletning af din Speedy Net-konto vil også slette din Speedy Match-konto. Hvis du er sikker, skriv "Ja. Slet min konto." i dette felt, nøjagtigt og der skelnes mellem store og små bogstaver.' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Naozaj chcete odstrániť svoj účet Speedy Net? Toto je trvalé a nezvratné. Odstránením účtu Speedy Net sa odstráni aj váš účet Speedy Match. Ak ste si istí, napíšte "Áno. Odstrániť môj účet." v tejto oblasti, presne a veľké a malé písmená.' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'क्या आप वाकई अपना स्पीडी नेट खाता हटाना Speedy Net चाहते हैं? यह स्थायी एवं अपरिवर्तनीय है। आपके स्पीडी नेट खाते Speedy Net को हटाने से आपका स्पीडी मैच खाता भी नष्ट हो जाएगा। यद Speedy Match ि आप निश्चित हैं, तो "हाँ। मेरा खाता हटाएँ" टाइप करें। इस क्षेत्र में, बिल्कुल और केस संवेदनशील।' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Kas olete kindel, et soovite oma Speedy Neti konto kustutada? See on püsiv ja pöördumatu. Speedy Neti konto kustutamisel kustutatakse ka teie Speedy Matchi konto. Kui olete kindel, tippige "Jah. Kustuta minu konto". selles valdkonnas täpselt ja tõstutundlikult.' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Jeste li sigurni da želite izbrisati svoj Speedy Net račun? Ovo je trajno i nepovratno. Brisanjem vašeg Speedy Net računa izbrisat ćete i svoj Speedy Match račun. Ako ste sigurni, upišite "Da. Izbriši moj račun." u ovom polju, točno i razlikuje velika i mala slova.' for gender in User.ALL_GENDERS},
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
                    **{gender: 'Eliminar permanentemente tua conta no Speedy Net' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Elimina definitivamente il tuo account Speedy Net' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Verwijder je Speedy Net-account permanent' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'Speedy Net アカウントを完全に削除します' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Удалите навсегда свою учетную запись Speedy Net.' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '永久刪除您的 Speedy Net 帳戶' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Usuń trwale swoje konto Speedy Net' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'حساب Speedy Net خود را برای همیشه حذف کنید' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "מחקי את החשבון שלך בספידי נט לצמיתות",
                    User.GENDER_MALE_STRING: "מחק את החשבון שלך בספידי נט לצמיתות",
                    User.GENDER_OTHER_STRING: "מחק/י את החשבון שלך בספידי נט לצמיתות",
                },
                'ko': {
                    **{gender: 'Speedy Net 계정을 영구적으로 삭제하세요' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'احذف حسابك Speedy Net نهائيًا' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Hapus akun Speedy Net Anda secara permanen' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Назавжди видалити свій обліковий запис Speedy Net' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Speedy Net hesabınızı kalıcı olarak silin' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Xóa vĩnh viễn tài khoản Speedy Net của bạn' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Trvale smažte svůj účet Speedy Net' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Radera ditt Speedy Net-konto permanent' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Poista Speedy Net-tilisi pysyvästi' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Véglegesen törölje Speedy Net fiókját' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'ลบบัญชี Speedy Net ของคุณอย่างถาวร' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Διαγράψτε οριστικά τον λογαριασμό Speedy Net σας' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Padamkan akaun Speedy Net anda secara kekal' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Трајно избришите свој Speedy Net налог' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Ștergeți definitiv contul dvs. Speedy Net' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'স্থায়ীভাবে আপনার Speedy Net অ্যাকাউন্ট মুছে দিন' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'Suprimeix permanentment el teu compte Speedy Net' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Slett Speedy Net-kontoen din permanent' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Изтрийте за постоянно вашия Speedy Net акаунт' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Slet din Speedy Net-konto permanent' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Natrvalo odstráňte svoj účet Speedy Net' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'अपना Speedy Net खाता स्थायी रूप से हटाएं' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Kustutage jäädavalt oma Speedy Net konto' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Trajno izbrišite svoj Speedy Net račun' for gender in User.ALL_GENDERS},
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
                    **{gender: 'As tuas contas Speedy Net e Speedy Match foram excluídas. Obrigado por usar o Speedy Net.' for gender in User.ALL_GENDERS},
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


