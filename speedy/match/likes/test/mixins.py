from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.core.base.test.mixins import TestCaseMixin
    from speedy.core.accounts.models import User


    class SpeedyMatchLikesLanguageMixin(TestCaseMixin):
        def set_up(self):
            super().set_up()

            _list_mutual_title_dict = {'en': 'Mutual Likes', 'fr': 'J’aimes mutuels', 'de': 'Gegenseitige Likes', 'es': 'Me gusta mutuos', 'pt': 'Curtidas recíproca', 'it': 'Mi Piace reciproci', 'nl': 'Wederzijdse likes', 'ja': '相互いいね', 'ru': 'Взаимные лайки', 'zh': '互相喜歡', 'pl': 'Wzajemne polubienia', 'fa': 'لایک های متقابل', 'he': 'לייקים הדדיים', 'ko': '상호 좋아요', 'ar': 'الإعجابات المتبادلة', 'id': 'Saling Suka', 'uk': 'Взаємні лайки', 'tr': 'Karşılıklı Beğeniler', 'vi': 'Lượt thích lẫn nhau', 'cs': 'Vzájemné lajky', 'sv': 'Ömsesidiga gillanden', 'fi': 'Yhteiset tykkäämiset', 'hu': 'Kölcsönös kedvelések', 'th': 'ความชอบร่วมกัน', 'el': 'Αμοιβαία Likes', 'ms': 'Saling Suka', 'sr': 'Мутуал Ликес', 'ro': 'Like-uri reciproce', 'bn': 'পারস্পরিক পছন্দ', 'ca': "M'agrada mutu", 'no': 'Gjensidige liker', 'bg': 'Взаимни харесвания', 'da': 'Gensidige likes', 'sk': 'Vzájomné lajky', 'hi': 'आपसी पसंद', 'et': 'Vastastikused meeldimised', 'hr': 'Međusobni lajkovi'}

            _list_to_title_dict_by_gender = {
                'en': {
                    User.GENDER_FEMALE_STRING: 'Girls You Like',
                    User.GENDER_MALE_STRING: 'Boys You Like',
                    User.GENDER_OTHER_STRING: 'People You Like',
                },
                'fr': {
                    User.GENDER_FEMALE_STRING: 'Les filles que vous aimez',
                    User.GENDER_MALE_STRING: 'Les garçons que vous aimez',
                    User.GENDER_OTHER_STRING: 'Les personnes que vous aimez',
                },
                'de': {
                    User.GENDER_FEMALE_STRING: 'Mädchen, die Sie selbst mögen',
                    User.GENDER_MALE_STRING: 'Jungs die Sie selbst mögen',
                    User.GENDER_OTHER_STRING: 'Leute, die Sie selbst mögen',
                },
                'es': {
                    User.GENDER_FEMALE_STRING: 'Chicas que te gustan',
                    User.GENDER_MALE_STRING: 'Chicos que te gustan',
                    User.GENDER_OTHER_STRING: 'Gente que te gusta',
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: 'Garotas que tu curtes',
                    User.GENDER_MALE_STRING: 'Garotos que tu curtes',
                    User.GENDER_OTHER_STRING: 'Pessoas que tu curtes',
                },
                'it': {
                    User.GENDER_FEMALE_STRING: 'Le ragazze a cui hai messo Mi Piace',
                    User.GENDER_MALE_STRING: 'I ragazzi a cui hai messo Mi Piace',
                    User.GENDER_OTHER_STRING: 'Persone a cui hai messo Mi Piace',
                },
                'nl': {
                    User.GENDER_FEMALE_STRING: 'Meisjes die je leuk vindt',
                    User.GENDER_MALE_STRING: 'Jongens die je leuk vindt',
                    User.GENDER_OTHER_STRING: 'Mensen die je leuk vindt',
                },
                'ja': {
                    User.GENDER_FEMALE_STRING: '好きな女の子',
                    User.GENDER_MALE_STRING: '好きな男の子たち',
                    User.GENDER_OTHER_STRING: '好きな人',
                },
                'ru': {
                    User.GENDER_FEMALE_STRING: 'Девушки, которые тебе нравятся',
                    User.GENDER_MALE_STRING: 'Мальчики, которые тебе нравятся',
                    User.GENDER_OTHER_STRING: 'Люди, которые вам нравятся',
                },
                'zh': {
                    User.GENDER_FEMALE_STRING: '你喜歡的女孩',
                    User.GENDER_MALE_STRING: '你喜歡的男孩',
                    User.GENDER_OTHER_STRING: '你喜歡的人',
                },
                'pl': {
                    User.GENDER_FEMALE_STRING: 'Dziewczyny, które lubisz',
                    User.GENDER_MALE_STRING: 'Chłopcy, których lubisz',
                    User.GENDER_OTHER_STRING: 'Ludzie, których lubisz',
                },
                'fa': {
                    User.GENDER_FEMALE_STRING: 'دخترانی که دوست دارید',
                    User.GENDER_MALE_STRING: 'پسرهایی که دوست دارید',
                    User.GENDER_OTHER_STRING: 'افرادی که دوست دارید',
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'בנות שעשית להן לייק',
                    User.GENDER_MALE_STRING: 'בנים שעשית להם לייק',
                    User.GENDER_OTHER_STRING: 'אנשים שעשית להם לייק',
                },
                'ko': {
                    User.GENDER_FEMALE_STRING: '귀하가 좋아하는 여성',
                    User.GENDER_MALE_STRING: '귀하가 좋아하는 남성',
                    User.GENDER_OTHER_STRING: '귀하가 좋아하는 사람',
                },
                'ar': {
                    User.GENDER_FEMALE_STRING: 'الفتيات التي تحبها',
                    User.GENDER_MALE_STRING: 'الأولاد الذين تحبهم',
                    User.GENDER_OTHER_STRING: 'الأشخاص الذين تحبهم',
                },
                'id': {
                    User.GENDER_FEMALE_STRING: 'Gadis yang Kamu Suka',
                    User.GENDER_MALE_STRING: 'Cowok yang Kamu Suka',
                    User.GENDER_OTHER_STRING: 'Orang yang Anda Suka',
                },
                'uk': {
                    User.GENDER_FEMALE_STRING: 'Дівчата, які вам подобаються',
                    User.GENDER_MALE_STRING: 'Хлопці, які тобі подобаються',
                    User.GENDER_OTHER_STRING: 'Люди, які вам подобаються',
                },
                'tr': {
                    User.GENDER_FEMALE_STRING: 'Beğendiğiniz Kızlar',
                    User.GENDER_MALE_STRING: 'Beğendiğiniz Erkekler',
                    User.GENDER_OTHER_STRING: 'Beğendiğiniz kişiler',
                },
                'vi': {
                    User.GENDER_FEMALE_STRING: 'Cô gái bạn thích',
                    User.GENDER_MALE_STRING: 'chàng trai bạn thích',
                    User.GENDER_OTHER_STRING: 'Những người bạn thích',
                },
                'cs': {
                    User.GENDER_FEMALE_STRING: 'Dívky, které se vám líbí',
                    User.GENDER_MALE_STRING: 'Kluci, které se vám líbí',
                    User.GENDER_OTHER_STRING: 'Lidé, které máte rádi',
                },
                'sv': {
                    User.GENDER_FEMALE_STRING: 'Tjejer du gillar',
                    User.GENDER_MALE_STRING: 'Killar du gillar',
                    User.GENDER_OTHER_STRING: 'Folk du gillar',
                },
                'fi': {
                    User.GENDER_FEMALE_STRING: 'Tytöt, joista tykkäät',
                    User.GENDER_MALE_STRING: 'Pojat, joista tykkäät',
                    User.GENDER_OTHER_STRING: 'Ihmiset, joista tykkäät',
                },
                'hu': {
                    User.GENDER_FEMALE_STRING: 'Lányok, akiket kedvelsz',
                    User.GENDER_MALE_STRING: 'Fiúk, akiket kedvelsz',
                    User.GENDER_OTHER_STRING: 'Olyan emberek, akiket kedvelsz',
                },
                'th': {
                    User.GENDER_FEMALE_STRING: 'ผู้หญิงที่คุณชอบ',
                    User.GENDER_MALE_STRING: 'ผู้ชายที่คุณชอบ',
                    User.GENDER_OTHER_STRING: 'คนที่คุณชอบ',
                },
                'el': {
                    User.GENDER_FEMALE_STRING: 'Κορίτσια που σου αρέσουν',
                    User.GENDER_MALE_STRING: 'Αγόρια που σου αρέσουν',
                    User.GENDER_OTHER_STRING: 'Άτομα που σου αρέσουν',
                },
                'ms': {
                    User.GENDER_FEMALE_STRING: 'Gadis yang Anda Suka',
                    User.GENDER_MALE_STRING: 'Lelaki yang Anda Suka',
                    User.GENDER_OTHER_STRING: 'Orang yang Anda Suka',
                },
                'sr': {
                    User.GENDER_FEMALE_STRING: 'Гирлс Иоу Лике',
                    User.GENDER_MALE_STRING: 'Боис Иоу Лике',
                    User.GENDER_OTHER_STRING: 'Људи које волите',
                },
                'ro': {
                    User.GENDER_FEMALE_STRING: 'Fete care vă plac',
                    User.GENDER_MALE_STRING: 'Băieți care vă plac',
                    User.GENDER_OTHER_STRING: 'Oameni care vă plac',
                },
                'bn': {
                    User.GENDER_FEMALE_STRING: 'আপনার পছন্দের মেয়েরা',
                    User.GENDER_MALE_STRING: 'বয়েজ ইউ লাইক',
                    User.GENDER_OTHER_STRING: 'আপনি পছন্দ মানুষ',
                },
                'ca': {
                    User.GENDER_FEMALE_STRING: "Noies que t'agraden",
                    User.GENDER_MALE_STRING: "Nois que t'agraden",
                    User.GENDER_OTHER_STRING: "Gent que t'agrada",
                },
                'no': {
                    User.GENDER_FEMALE_STRING: 'Jenter du liker',
                    User.GENDER_MALE_STRING: 'Gutter du liker',
                    User.GENDER_OTHER_STRING: 'Folk du liker',
                },
                'bg': {
                    User.GENDER_FEMALE_STRING: 'Момичета, които харесвате',
                    User.GENDER_MALE_STRING: 'Момчета, които харесвате',
                    User.GENDER_OTHER_STRING: 'Хора, които харесвате',
                },
                'da': {
                    User.GENDER_FEMALE_STRING: 'Piger du kan lide',
                    User.GENDER_MALE_STRING: 'Drenge du kan lide',
                    User.GENDER_OTHER_STRING: 'Folk du kan lide',
                },
                'sk': {
                    User.GENDER_FEMALE_STRING: 'Dievčatá, ktoré sa vám páčia',
                    User.GENDER_MALE_STRING: 'Chlapci, ktorých máte radi',
                    User.GENDER_OTHER_STRING: 'Ľudia, ktorých máte radi',
                },
                'hi': {
                    User.GENDER_FEMALE_STRING: 'जिन लड़कियों को आप पसंद करते हैं',
                    User.GENDER_MALE_STRING: 'लड़के तुम्हें पसंद हैं',
                    User.GENDER_OTHER_STRING: 'वे लोग जिन्हें आप पसंद करते हैं',
                },
                'et': {
                    User.GENDER_FEMALE_STRING: 'Tüdrukud, kes teile meeldivad',
                    User.GENDER_MALE_STRING: 'Poisid, kes teile meeldivad',
                    User.GENDER_OTHER_STRING: 'Inimesed, kes sulle meeldivad',
                },
                'hr': {
                    User.GENDER_FEMALE_STRING: 'Djevojke koje vam se sviđaju',
                    User.GENDER_MALE_STRING: 'Dečki koji vam se sviđaju',
                    User.GENDER_OTHER_STRING: 'Ljudi koji vam se sviđaju',
                },
            }

            _list_from_title_dict_by_gender = {
                'en': {
                    User.GENDER_FEMALE_STRING: 'Girls Who Like You',
                    User.GENDER_MALE_STRING: 'Boys Who Like You',
                    User.GENDER_OTHER_STRING: 'People Who Like You',
                },
                'fr': {
                    User.GENDER_FEMALE_STRING: 'Les filles qui vous aiment',
                    User.GENDER_MALE_STRING: 'Les garçons qui vous aiment',
                    User.GENDER_OTHER_STRING: 'Les personnes qui vous aiment',
                },
                'de': {
                    User.GENDER_FEMALE_STRING: 'Mädchen, die Sie mögen',
                    User.GENDER_MALE_STRING: 'Jungs, die Sie mögen',
                    User.GENDER_OTHER_STRING: 'Leute, die Sie mögen',
                },
                'es': {
                    User.GENDER_FEMALE_STRING: 'Chicas a las que les gustas',
                    User.GENDER_MALE_STRING: 'Chicos a los que les gustas',
                    User.GENDER_OTHER_STRING: 'Gente a la que le gustas',
                },
                'pt': {
                    User.GENDER_FEMALE_STRING: 'Garotas que curtem a ti',
                    User.GENDER_MALE_STRING: 'Garotos que curtem a ti',
                    User.GENDER_OTHER_STRING: 'Pessoas que curtem a ti',
                },
                'it': {
                    User.GENDER_FEMALE_STRING: 'Le ragazze che ti hanno messo Mi Piace',
                    User.GENDER_MALE_STRING: 'I ragazzi che ti hanno messo Mi Piace',
                    User.GENDER_OTHER_STRING: 'Le persone che ti hanno messo Mi Piace',
                },
                'nl': {
                    User.GENDER_FEMALE_STRING: 'Meisjes die je leuk vinden',
                    User.GENDER_MALE_STRING: 'Jongens die je leuk vinden',
                    User.GENDER_OTHER_STRING: 'Mensen die je leuk vinden',
                },
                'ja': {
                    User.GENDER_FEMALE_STRING: 'あなたが好きな女の子',
                    User.GENDER_MALE_STRING: 'あなたが好きなボーイズ',
                    User.GENDER_OTHER_STRING: 'あなたを好きな人',
                },
                'ru': {
                    User.GENDER_FEMALE_STRING: 'Девушки, которым ты нравишься',
                    User.GENDER_MALE_STRING: 'Мальчики, которым ты нравишься',
                    User.GENDER_OTHER_STRING: 'Люди, которым ты нравишься',
                },
                'zh': {
                    User.GENDER_FEMALE_STRING: '喜歡你的女孩',
                    User.GENDER_MALE_STRING: '喜歡你的男孩',
                    User.GENDER_OTHER_STRING: '喜歡你的人',
                },
                'pl': {
                    User.GENDER_FEMALE_STRING: 'Dziewczyny, które cię lubią',
                    User.GENDER_MALE_STRING: 'Chłopcy, którzy cię lubią',
                    User.GENDER_OTHER_STRING: 'Ludzie, którzy Cię lubią',
                },
                'fa': {
                    User.GENDER_FEMALE_STRING: 'دخترانی که شما را دوست دارند',
                    User.GENDER_MALE_STRING: 'پسرانی که شما را دوست دارند',
                    User.GENDER_OTHER_STRING: 'افرادی که شما را دوست دارند',
                },
                'he': {
                    User.GENDER_FEMALE_STRING: 'בנות שעשו לך לייק',
                    User.GENDER_MALE_STRING: 'בנים שעשו לך לייק',
                    User.GENDER_OTHER_STRING: 'אנשים שעשו לך לייק',
                },
                'ko': {
                    User.GENDER_FEMALE_STRING: '귀하를 좋아하는 여성',
                    User.GENDER_MALE_STRING: '귀하를 좋아하는 남성',
                    User.GENDER_OTHER_STRING: '귀하를 좋아하는 사람',
                },
                'ar': {
                    User.GENDER_FEMALE_STRING: 'الفتيات الذين يحبونك',
                    User.GENDER_MALE_STRING: 'الأولاد الذين يحبونك',
                    User.GENDER_OTHER_STRING: 'الأشخاص الذين يحبونك',
                },
                'id': {
                    User.GENDER_FEMALE_STRING: 'Gadis yang Menyukaimu',
                    User.GENDER_MALE_STRING: 'Laki-Laki yang Menyukaimu',
                    User.GENDER_OTHER_STRING: 'Orang yang Menyukaimu',
                },
                'uk': {
                    User.GENDER_FEMALE_STRING: 'Дівчата, яким ти подобаєшся',
                    User.GENDER_MALE_STRING: 'Хлопці, яким ти подобаєшся',
                    User.GENDER_OTHER_STRING: 'Люди, яким ти подобаєшся',
                },
                'tr': {
                    User.GENDER_FEMALE_STRING: 'Senden Hoşlanan Kızlar',
                    User.GENDER_MALE_STRING: 'Senden Hoşlanan Erkekler',
                    User.GENDER_OTHER_STRING: 'Seni Beğenenler',
                },
                'vi': {
                    User.GENDER_FEMALE_STRING: 'Những cô gái thích bạn',
                    User.GENDER_MALE_STRING: 'Chàng trai thích bạn',
                    User.GENDER_OTHER_STRING: 'Những người thích bạn',
                },
                'cs': {
                    User.GENDER_FEMALE_STRING: 'Dívky, které tě mají rády',
                    User.GENDER_MALE_STRING: 'Kluci, kteří tě mají rádi',
                    User.GENDER_OTHER_STRING: 'Lidé, kteří vás mají rádi',
                },
                'sv': {
                    User.GENDER_FEMALE_STRING: 'Tjejer som gillar dig',
                    User.GENDER_MALE_STRING: 'Killar som gillar dig',
                    User.GENDER_OTHER_STRING: 'Folk som gillar dig',
                },
                'fi': {
                    User.GENDER_FEMALE_STRING: 'Tytöt, jotka tykkäävät sinusta',
                    User.GENDER_MALE_STRING: 'Pojat, jotka tykkäävät sinusta',
                    User.GENDER_OTHER_STRING: 'Ihmiset, jotka tykkäävät sinusta',
                },
                'hu': {
                    User.GENDER_FEMALE_STRING: 'Lányok, akik kedvelnek téged',
                    User.GENDER_MALE_STRING: 'Fiúk, akik kedvelnek téged',
                    User.GENDER_OTHER_STRING: 'Emberek, akik kedvelnek téged',
                },
                'th': {
                    User.GENDER_FEMALE_STRING: 'ผู้หญิงที่ชอบคุณ',
                    User.GENDER_MALE_STRING: 'เด็กผู้ชายที่ชอบคุณ',
                    User.GENDER_OTHER_STRING: 'คนที่ชอบคุณ',
                },
                'el': {
                    User.GENDER_FEMALE_STRING: 'Κορίτσια που σου αρέσουν',
                    User.GENDER_MALE_STRING: 'Αγόρια που σας αρέσουν',
                    User.GENDER_OTHER_STRING: 'Άτομα που σε συμπαθούν',
                },
                'ms': {
                    User.GENDER_FEMALE_STRING: 'Perempuan Yang Suka Awak',
                    User.GENDER_MALE_STRING: 'Lelaki Yang Suka Awak',
                    User.GENDER_OTHER_STRING: 'Orang Yang Suka Anda',
                },
                'sr': {
                    User.GENDER_FEMALE_STRING: 'Гирлс Вхо Лике Иоу',
                    User.GENDER_MALE_STRING: 'Боис Вхо Лике Иоу',
                    User.GENDER_OTHER_STRING: 'Људи који вас воле',
                },
                'ro': {
                    User.GENDER_FEMALE_STRING: 'Fete care te plac',
                    User.GENDER_MALE_STRING: 'Băieți care vă plac',
                    User.GENDER_OTHER_STRING: 'Oameni care te plac',
                },
                'bn': {
                    User.GENDER_FEMALE_STRING: 'মেয়েরা যারা তোমাকে পছন্দ করে',
                    User.GENDER_MALE_STRING: 'বয়েজ হু লাইক ইউ',
                    User.GENDER_OTHER_STRING: 'যারা আপনাকে পছন্দ করে',
                },
                'ca': {
                    User.GENDER_FEMALE_STRING: "Noies que t'agraden",
                    User.GENDER_MALE_STRING: "Nois que t'agraden",
                    User.GENDER_OTHER_STRING: "Gent que t'agrada",
                },
                'no': {
                    User.GENDER_FEMALE_STRING: 'Jenter som liker deg',
                    User.GENDER_MALE_STRING: 'Gutter som liker deg',
                    User.GENDER_OTHER_STRING: 'Folk som liker deg',
                },
                'bg': {
                    User.GENDER_FEMALE_STRING: 'Момичета, които те харесват',
                    User.GENDER_MALE_STRING: 'Момчета, които те харесват',
                    User.GENDER_OTHER_STRING: 'Хора, които те харесват',
                },
                'da': {
                    User.GENDER_FEMALE_STRING: 'Piger der kan lide dig',
                    User.GENDER_MALE_STRING: 'Drenge der kan lide dig',
                    User.GENDER_OTHER_STRING: 'Mennesker, der kan lide dig',
                },
                'sk': {
                    User.GENDER_FEMALE_STRING: 'Dievčatá, ktoré ťa majú radi',
                    User.GENDER_MALE_STRING: 'Chlapci, ktorí ťa majú radi',
                    User.GENDER_OTHER_STRING: 'Ľudia, ktorí ťa majú radi',
                },
                'hi': {
                    User.GENDER_FEMALE_STRING: 'जो लड़कियाँ तुम्हें पसंद करती हैं',
                    User.GENDER_MALE_STRING: 'लड़के जो तुम्हें पसंद करते हैं',
                    User.GENDER_OTHER_STRING: 'जो लोग आपको पसंद करते हैं',
                },
                'et': {
                    User.GENDER_FEMALE_STRING: 'Tüdrukud, kellele sa meeldid',
                    User.GENDER_MALE_STRING: 'Poisid, kellele sa meeldid',
                    User.GENDER_OTHER_STRING: 'Inimesed, kellele sa meeldid',
                },
                'hr': {
                    User.GENDER_FEMALE_STRING: 'Djevojke kojima se sviđaš',
                    User.GENDER_MALE_STRING: 'Dečki kojima se sviđaš',
                    User.GENDER_OTHER_STRING: 'Ljudi kojima se sviđaš',
                },
            }

            _someone_likes_you_on_speedy_match_subject_dict_by_gender = {
                'en': {
                    **{gender: 'Someone likes you on Speedy Match' for gender in User.ALL_GENDERS},
                },
                'fr': {
                    **{gender: 'Quelqu’un vous aime bien sur Speedy Match' for gender in User.ALL_GENDERS},
                },
                'de': {
                    **{gender: 'Jemand likt Sie am Speedy Match' for gender in User.ALL_GENDERS},
                },
                'es': {
                    **{gender: 'Le gustas a alguien Speedy Match' for gender in User.ALL_GENDERS},
                },
                'pt': {
                    **{gender: 'Alguém curte a ti no Speedy Match' for gender in User.ALL_GENDERS},
                },
                'it': {
                    **{gender: 'Qualcuno ti ha messo Mi Piace su Speedy Match' for gender in User.ALL_GENDERS},
                },
                'nl': {
                    **{gender: 'Iemand vindt je leuk op Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ja': {
                    **{gender: 'Speedy Match であなたに「いいね！」した人がいます' for gender in User.ALL_GENDERS},
                },
                'ru': {
                    **{gender: 'Кому-то вы понравились в Speedy Match' for gender in User.ALL_GENDERS},
                },
                'zh': {
                    **{gender: '在 Speedy Match 上有人喜欢你' for gender in User.ALL_GENDERS},
                },
                'pl': {
                    **{gender: 'Ktoś polubił Cię w Speedy Match' for gender in User.ALL_GENDERS},
                },
                'fa': {
                    **{gender: 'شخصی در Speedy Match شما را پسندیده است' for gender in User.ALL_GENDERS},
                },
                'he': {
                    User.GENDER_FEMALE_STRING: "מישהי עשתה לך לייק בספידי מץ'",
                    User.GENDER_MALE_STRING: "מישהו עשה לך לייק בספידי מץ'",
                    User.GENDER_OTHER_STRING: "מישהו עשה לך לייק בספידי מץ'",
                },
                'ko': {
                    **{gender: '누군가가 다음에서 귀하를 좋아합니다 Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ar': {
                    **{gender: 'هناك شخص معجب بك على Speedy Match' for gender in User.ALL_GENDERS},
                },
                'id': {
                    **{gender: 'Seseorang menyukai Anda di Speedy Match' for gender in User.ALL_GENDERS},
                },
                'uk': {
                    **{gender: 'Ви комусь сподобалися у Speedy Match' for gender in User.ALL_GENDERS},
                },
                'tr': {
                    **{gender: 'Birisi sizi Speedy Match üzerinde beğendi' for gender in User.ALL_GENDERS},
                },
                'vi': {
                    **{gender: 'Có người thích bạn trên Speedy Match' for gender in User.ALL_GENDERS},
                },
                'cs': {
                    **{gender: 'Někomu se líbíte na Speedy Match' for gender in User.ALL_GENDERS},
                },
                'sv': {
                    **{gender: 'Någon gillar dig på Speedy Match' for gender in User.ALL_GENDERS},
                },
                'fi': {
                    **{gender: 'Joku tykkää sinusta Speedy Match' for gender in User.ALL_GENDERS},
                },
                'hu': {
                    **{gender: 'Valaki kedvel téged a Speedy Match oldalon' for gender in User.ALL_GENDERS},
                },
                'th': {
                    **{gender: 'มีคนกดถูกใจคุณบน Speedy Match' for gender in User.ALL_GENDERS},
                },
                'el': {
                    **{gender: 'Κάποιος σας συμπαθεί στο Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ms': {
                    **{gender: 'Seseorang menyukai anda di Speedy Match' for gender in User.ALL_GENDERS},
                },
                'sr': {
                    **{gender: 'Неко вас је лајковао на Speedy Match' for gender in User.ALL_GENDERS},
                },
                'ro': {
                    **{gender: 'Cineva te place pe Speedy Match' for gender in User.ALL_GENDERS},
                },
                'bn': {
                    **{gender: 'Speedy Match-এ কেউ আপনাকে পছন্দ করেছে' for gender in User.ALL_GENDERS},
                },
                'ca': {
                    **{gender: 'A algú li agrades a Speedy Match' for gender in User.ALL_GENDERS},
                },
                'no': {
                    **{gender: 'Noen liker deg på Speedy Match' for gender in User.ALL_GENDERS},
                },
                'bg': {
                    **{gender: 'Някой ви харесва в Speedy Match' for gender in User.ALL_GENDERS},
                },
                'da': {
                    **{gender: 'Nogen kan lide dig på Speedy Match' for gender in User.ALL_GENDERS},
                },
                'sk': {
                    **{gender: 'Niekomu sa páčite na Speedy Match' for gender in User.ALL_GENDERS},
                },
                'hi': {
                    **{gender: 'Speedy Match पर कोई आपको पसंद करता है' for gender in User.ALL_GENDERS},
                },
                'et': {
                    **{gender: 'Kellelegi meeldid Speedy Match platvormil' for gender in User.ALL_GENDERS},
                },
                'hr': {
                    **{gender: 'Nekome se sviđate na platformi Speedy Match' for gender in User.ALL_GENDERS},
                },
            }

            self._list_mutual_title = _list_mutual_title_dict[self.language_code]

            self._list_to_title_dict_by_gender = _list_to_title_dict_by_gender[self.language_code]
            self._list_from_title_dict_by_gender = _list_from_title_dict_by_gender[self.language_code]
            self._someone_likes_you_on_speedy_match_subject_dict_by_gender = _someone_likes_you_on_speedy_match_subject_dict_by_gender[self.language_code]

            self.assertSetEqual(set1=set(self._list_to_title_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._list_from_title_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))
            self.assertSetEqual(set1=set(self._someone_likes_you_on_speedy_match_subject_dict_by_gender.keys()), set2=set(User.ALL_GENDERS))

            self.assertEqual(first=len(set(self._list_to_title_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._list_from_title_dict_by_gender.keys())), second=3)
            self.assertEqual(first=len(set(self._someone_likes_you_on_speedy_match_subject_dict_by_gender.keys())), second=3)


