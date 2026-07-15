function init_datepicker() {
    var dobDpElem = this.$("#id_date_of_birth").clone();
    dobDpElem.attr('id', 'id_date_of_birth_dp');
    dobDpElem.attr('name', 'date_of_birth_dp');
    this.$("#id_date_of_birth").after(dobDpElem);
    this.$("#id_date_of_birth").attr('type', 'hidden');
    this.$("#id_date_of_birth").removeAttr('class');
    this.$("#id_date_of_birth").removeAttr('required');
    this.$("#id_date_of_birth_dp").datepicker(datepicker_options);
    var dob = $.datepicker.parseDate('yy-mm-dd', this.$("#id_date_of_birth").val());
    this.$("#id_date_of_birth_dp").datepicker('setDate', dob);
}

var datepicker_options = {
    altField: "#id_date_of_birth",
    altFormat: 'yy-mm-dd',
    changeMonth: true,
    changeYear: true,
    minDate: '-185y+1d',
    maxDate: '+3y+0d',
    yearRange: '-185:+3',
    defaultDate: '+2y+0d'
};

$.datepicker.regional.en = {
    closeText: "Done",
    prevText: "Prev",
    nextText: "Next",
    currentText: "Today",
    monthNames: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    monthNamesShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    dayNames: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    dayNamesShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    dayNamesMin: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
    weekHeader: "Wk",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.fr = {
    closeText: "Fermer",
    prevText: "Précédent",
    nextText: "Suivant",
    currentText: "Aujourd'hui",
    monthNames: ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
    monthNamesShort: ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
    dayNames: ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"],
    dayNamesShort: ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."],
    dayNamesMin: ["D", "L", "M", "M", "J", "V", "S"],
    weekHeader: "Sem.",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.de = {
    closeText: "Schließen",
    prevText: "Zurück",
    nextText: "Vor",
    currentText: "Heute",
    monthNames: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    monthNamesShort: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    dayNames: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"],
    dayNamesShort: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
    dayNamesMin: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
    weekHeader: "KW",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.es = {
    closeText: "Cerrar",
    prevText: "Ant",
    nextText: "Sig",
    currentText: "Hoy",
    monthNames: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    monthNamesShort: ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    dayNames: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
    dayNamesShort: ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
    dayNamesMin: ["D", "L", "M", "X", "J", "V", "S"],
    weekHeader: "Sm",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.pt = {
    closeText: "Fechar",
    prevText: "Anterior",
    nextText: "Seguinte",
    currentText: "Hoje",
    monthNames: ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
    monthNamesShort: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
    dayNames: ["Domingo", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"],
    dayNamesShort: ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
    dayNamesMin: ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
    weekHeader: "Sem",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.it = {
    closeText: "Chiudi",
    prevText: "Prec",
    nextText: "Succ",
    currentText: "Oggi",
    monthNames: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
    monthNamesShort: ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    dayNames: ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"],
    dayNamesShort: ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"],
    dayNamesMin: ["Do", "Lu", "Ma", "Me", "Gi", "Ve", "Sa"],
    weekHeader: "Sm",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.nl = {
    closeText: "Sluiten",
    prevText: "Vorig",
    nextText: "Volgende",
    currentText: "Vandaag",
    monthNames: ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober", "november", "december"],
    monthNamesShort: ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"],
    dayNames: ["zondag", "maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag"],
    dayNamesShort: ["zon", "maa", "din", "woe", "don", "vri", "zat"],
    dayNamesMin: ["zo", "ma", "di", "wo", "do", "vr", "za"],
    weekHeader: "Wk",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.ja = {
    closeText: "閉じる",
    prevText: "前",
    nextText: "次",
    currentText: "今日",
    monthNames: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
    monthNamesShort: ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
    dayNames: ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"],
    dayNamesShort: ["日", "月", "火", "水", "木", "金", "土"],
    dayNamesMin: ["日", "月", "火", "水", "木", "金", "土"],
    weekHeader: "週",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: true,
    yearSuffix: "年"
};

$.datepicker.regional.ru = {
    closeText: "Закрыть",
    prevText: "Пред",
    nextText: "След",
    currentText: "Сегодня",
    monthNames: ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
    monthNamesShort: ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
    dayNames: ["воскресенье", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота"],
    dayNamesShort: ["вск", "пнд", "втр", "срд", "чтв", "птн", "сбт"],
    dayNamesMin: ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
    weekHeader: "Нед",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.zh = {
    closeText: "關閉",
    prevText: "上個月",
    nextText: "下個月",
    currentText: "今天",
    monthNames: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
    monthNamesShort: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
    dayNames: ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"],
    dayNamesShort: ["週日", "週一", "週二", "週三", "週四", "週五", "週六"],
    dayNamesMin: ["日", "一", "二", "三", "四", "五", "六"],
    weekHeader: "週",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: true,
    yearSuffix: "年"
};

$.datepicker.regional.pl = {
    closeText: "Zamknij",
    prevText: "Poprzedni",
    nextText: "Następny",
    currentText: "Dziś",
    monthNames: ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"],
    monthNamesShort: ["Sty", "Lu", "Mar", "Kw", "Maj", "Cze", "Lip", "Sie", "Wrz", "Pa", "Lis", "Gru"],
    dayNames: ["Niedziela", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota"],
    dayNamesShort: ["Nie", "Pn", "Wt", "Śr", "Czw", "Pt", "So"],
    dayNamesMin: ["N", "Pn", "Wt", "Śr", "Cz", "Pt", "So"],
    weekHeader: "Tydz",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.fa = {
    closeText: "بستن",
    prevText: "قبلی",
    nextText: "بعدی",
    currentText: "امروز",
    monthNames: ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن", "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"],
    monthNamesShort: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    dayNames: ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"],
    dayNamesShort: ["ی", "د", "س", "چ", "پ", "ج", "ش"],
    dayNamesMin: ["ی", "د", "س", "چ", "پ", "ج", "ش"],
    weekHeader: "هف",
    dateFormat: "d MM yy",
    firstDay: 6,
    isRTL: true,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.he = {
    closeText: "סגור",
    prevText: "הקודם",
    nextText: "הבא",
    currentText: "היום",
    monthNames: ["ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"],
    monthNamesShort: ["ינו", "פבר", "מרץ", "אפר", "מאי", "יוני", "יולי", "אוג", "ספט", "אוק", "נוב", "דצמ"],
    dayNames: ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"],
    dayNamesShort: ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "שבת"],
    dayNamesMin: ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "שבת"],
    weekHeader: "שב׳",
    dateFormat: "d בMM yy",
    firstDay: 0,
    isRTL: true,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.ko = {
    closeText: "닫기",
    prevText: "이전달",
    nextText: "다음달",
    currentText: "오늘",
    monthNames: ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
    monthNamesShort: ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
    dayNames: ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"],
    dayNamesShort: ["일", "월", "화", "수", "목", "금", "토"],
    dayNamesMin: ["일", "월", "화", "수", "목", "금", "토"],
    weekHeader: "주",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: true,
    yearSuffix: "년"
};

$.datepicker.regional.ar = {
    closeText: "إغلاق",
    prevText: "السابق",
    nextText: "التالي",
    currentText: "اليوم",
    monthNames: ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
    monthNamesShort: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    dayNames: ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"],
    dayNamesShort: ["أحد", "اثنين", "ثلاثاء", "أربعاء", "خميس", "جمعة", "سبت"],
    dayNamesMin: ["ح", "ن", "ث", "ر", "خ", "ج", "س"],
    weekHeader: "أسبوع",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: true,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.id = {
    closeText: "Tutup",
    prevText: "Mundur",
    nextText: "Maju",
    currentText: "Hari ini",
    monthNames: ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"],
    monthNamesShort: ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"],
    dayNames: ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"],
    dayNamesShort: ["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"],
    dayNamesMin: ["Mg", "Sn", "Sl", "Rb", "Km", "Jm", "Sb"],
    weekHeader: "Mg",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.uk = {
    closeText: "Закрити",
    prevText: "Попередній",
    nextText: "Наступний",
    currentText: "Сьогодні",
    monthNames: ["Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"],
    monthNamesShort: ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"],
    dayNames: ["неділя", "понеділок", "вівторок", "середа", "четвер", "п’ятниця", "субота"],
    dayNamesShort: ["нед", "пнд", "вів", "срд", "чтв", "птн", "сбт"],
    dayNamesMin: ["Нд", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
    weekHeader: "Тиж",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.tr = {
    closeText: "Kapat",
    prevText: "Geri",
    nextText: "İleri",
    currentText: "Bugün",
    monthNames: ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
    monthNamesShort: ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"],
    dayNames: ["Pazar", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"],
    dayNamesShort: ["Pz", "Pt", "Sa", "Ça", "Pe", "Cu", "Ct"],
    dayNamesMin: ["Pz", "Pt", "Sa", "Ça", "Pe", "Cu", "Ct"],
    weekHeader: "Hf",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.vi = {
    closeText: "Đóng",
    prevText: "Trước",
    nextText: "Tiếp",
    currentText: "Hôm nay",
    monthNames: ["Tháng Một", "Tháng Hai", "Tháng Ba", "Tháng Tư", "Tháng Năm", "Tháng Sáu", "Tháng Bảy", "Tháng Tám", "Tháng Chín", "Tháng Mười", "Tháng Mười Một", "Tháng Mười Hai"],
    monthNamesShort: ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6", "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"],
    dayNames: ["Chủ Nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"],
    dayNamesShort: ["CN", "T2", "T3", "T4", "T5", "T6", "T7"],
    dayNamesMin: ["CN", "T2", "T3", "T4", "T5", "T6", "T7"],
    weekHeader: "Tu",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.cs = {
    closeText: "Zavřít",
    prevText: "Dříve",
    nextText: "Později",
    currentText: "Nyní",
    monthNames: ["leden", "únor", "březen", "duben", "květen", "červen", "červenec", "srpen", "září", "říjen", "listopad", "prosinec"],
    monthNamesShort: ["led", "úno", "bře", "dub", "kvě", "čer", "čvc", "srp", "zář", "říj", "lis", "pro"],
    dayNames: ["neděle", "pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota"],
    dayNamesShort: ["ne", "po", "út", "st", "čt", "pá", "so"],
    dayNamesMin: ["ne", "po", "út", "st", "čt", "pá", "so"],
    weekHeader: "Týd",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.sv = {
    closeText: "Stäng",
    prevText: "Förra",
    nextText: "Nästa",
    currentText: "Idag",
    monthNames: ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"],
    monthNamesShort: ["jan.", "feb.", "mars", "apr.", "maj", "juni", "juli", "aug.", "sep.", "okt.", "nov.", "dec."],
    dayNames: ["söndag", "måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag"],
    dayNamesShort: ["sön", "mån", "tis", "ons", "tor", "fre", "lör"],
    dayNamesMin: ["sö", "må", "ti", "on", "to", "fr", "lö"],
    weekHeader: "Ve",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.fi = {
    closeText: "Sulje",
    prevText: "Edellinen",
    nextText: "Seuraava",
    currentText: "Tänään",
    monthNames: ["Tammikuu", "Helmikuu", "Maaliskuu", "Huhtikuu", "Toukokuu", "Kesäkuu", "Heinäkuu", "Elokuu", "Syyskuu", "Lokakuu", "Marraskuu", "Joulukuu"],
    monthNamesShort: ["Tammi", "Helmi", "Maalis", "Huhti", "Touko", "Kesä", "Heinä", "Elo", "Syys", "Loka", "Marras", "Joulu"],
    dayNames: ["Sunnuntai", "Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai", "Lauantai"],
    dayNamesShort: ["Su", "Ma", "Ti", "Ke", "To", "Pe", "La"],
    dayNamesMin: ["Su", "Ma", "Ti", "Ke", "To", "Pe", "La"],
    weekHeader: "Vk",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.hu = {
    closeText: "Bezár",
    prevText: "Vissza",
    nextText: "Előre",
    currentText: "Ma",
    monthNames: ["Január", "Február", "Március", "Április", "Május", "Június", "Július", "Augusztus", "Szeptember", "Október", "November", "December"],
    monthNamesShort: ["Jan", "Feb", "Már", "Ápr", "Máj", "Jún", "Júl", "Aug", "Szep", "Okt", "Nov", "Dec"],
    dayNames: ["Vasárnap", "Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat"],
    dayNamesShort: ["Vas", "Hét", "Ked", "Sze", "Csü", "Pén", "Szo"],
    dayNamesMin: ["V", "H", "K", "Sze", "Cs", "P", "Szo"],
    weekHeader: "Hét",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: true,
    yearSuffix: ""
};

$.datepicker.regional.th = {
    closeText: "ปิด",
    prevText: "ย้อน",
    nextText: "ถัดไป",
    currentText: "วันนี้",
    monthNames: ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"],
    monthNamesShort: ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."],
    dayNames: ["อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"],
    dayNamesShort: ["อา.", "จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส."],
    dayNamesMin: ["อา.", "จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส."],
    weekHeader: "สัปดาห์",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.el = {
    closeText: "Κλείσιμο",
    prevText: "Προηγούμενος",
    nextText: "Επόμενος",
    currentText: "Σήμερα",
    monthNames: ["Ιανουάριος", "Φεβρουάριος", "Μάρτιος", "Απρίλιος", "Μάιος", "Ιούνιος", "Ιούλιος", "Αύγουστος", "Σεπτέμβριος", "Οκτώβριος", "Νοέμβριος", "Δεκέμβριος"],
    monthNamesShort: ["Ιαν", "Φεβ", "Μαρ", "Απρ", "Μαι", "Ιουν", "Ιουλ", "Αυγ", "Σεπ", "Οκτ", "Νοε", "Δεκ"],
    dayNames: ["Κυριακή", "Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο"],
    dayNamesShort: ["Κυρ", "Δευ", "Τρι", "Τετ", "Πεμ", "Παρ", "Σαβ"],
    dayNamesMin: ["Κυ", "Δε", "Τρ", "Τε", "Πε", "Πα", "Σα"],
    weekHeader: "Εβδ",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.ms = {
    closeText: "Tutup",
    prevText: "Sebelum",
    nextText: "Selepas",
    currentText: "Hari ini",
    monthNames: ["Januari", "Februari", "Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November", "Disember"],
    monthNamesShort: ["Jan", "Feb", "Mac", "Apr", "Mei", "Jun", "Jul", "Ogo", "Sep", "Okt", "Nov", "Dis"],
    dayNames: ["Ahad", "Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu"],
    dayNamesShort: ["Aha", "Isn", "Sel", "Rab", "Kha", "Jum", "Sab"],
    dayNamesMin: ["Ah", "Is", "Se", "Ra", "Kh", "Ju", "Sa"],
    weekHeader: "Mg",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.sr = {
    closeText: "Затвори",
    prevText: "Претходна",
    nextText: "Следећи",
    currentText: "Данас",
    monthNames: ["Јануар", "Фебруар", "Март", "Април", "Мај", "Јун", "Јул", "Август", "Септембар", "Октобар", "Новембар", "Децембар"],
    monthNamesShort: ["Јан", "Феб", "Мар", "Апр", "Мај", "Јун", "Јул", "Авг", "Сеп", "Окт", "Нов", "Дец"],
    dayNames: ["Недеља", "Понедељак", "Уторак", "Среда", "Четвртак", "Петак", "Субота"],
    dayNamesShort: ["Нед", "Пон", "Уто", "Сре", "Чет", "Пет", "Суб"],
    dayNamesMin: ["Не", "По", "Ут", "Ср", "Че", "Пе", "Су"],
    weekHeader: "Сед",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.ro = {
    closeText: "Închide",
    prevText: "Luna precedentă",
    nextText: "Luna următoare",
    currentText: "Azi",
    monthNames: ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"],
    monthNamesShort: ["Ian", "Feb", "Mar", "Apr", "Mai", "Iun", "Iul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    dayNames: ["Duminică", "Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă"],
    dayNamesShort: ["Dum", "Lun", "Mar", "Mie", "Joi", "Vin", "Sâm"],
    dayNamesMin: ["Du", "Lu", "Ma", "Mi", "Jo", "Vi", "Sâ"],
    weekHeader: "Săpt",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.bn = {
    closeText: "বন্ধ",
    prevText: "পূর্ববর্তী",
    nextText: "পরবর্তী",
    currentText: "আজ",
    monthNames: ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"],
    monthNamesShort: ["জানু", "ফেব", "মার্চ", "এপ্রি", "মে", "জুন", "জুল", "আগ", "সেপ্টে", "অক্টো", "নভে", "ডিসে"],
    dayNames: ["রবিবার", "সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার"],
    dayNamesShort: ["রবি", "সোম", "মঙ্গল", "বুধ", "বৃহ", "শুক্র", "শনি"],
    dayNamesMin: ["রবি", "সোম", "মঙ্গল", "বুধ", "বৃহ", "শুক্র", "শনি"],
    weekHeader: "সপ্তাহ",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.ca = {
    closeText: "Tanca",
    prevText: "Anterior",
    nextText: "Següent",
    currentText: "Avui",
    monthNames: ["gener", "febrer", "març", "abril", "maig", "juny", "juliol", "agost", "setembre", "octubre", "novembre", "desembre"],
    monthNamesShort: ["gen", "feb", "març", "abr", "maig", "juny", "jul", "ag", "set", "oct", "nov", "des"],
    dayNames: ["diumenge", "dilluns", "dimarts", "dimecres", "dijous", "divendres", "dissabte"],
    dayNamesShort: ["dg", "dl", "dt", "dc", "dj", "dv", "ds"],
    dayNamesMin: ["dg", "dl", "dt", "dc", "dj", "dv", "ds"],
    weekHeader: "Set",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.no = {
    closeText: "Lukk",
    prevText: "Forrige",
    nextText: "Neste",
    currentText: "I dag",
    monthNames: ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"],
    monthNamesShort: ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"],
    dayNames: ["søndag", "mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag"],
    dayNamesShort: ["søn", "man", "tir", "ons", "tor", "fre", "lør"],
    dayNamesMin: ["sø", "ma", "ti", "on", "to", "fr", "lø"],
    weekHeader: "Uke",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.bg = {
    closeText: "затвори",
    prevText: "назад",
    nextText: "напред",
    currentText: "днес",
    monthNames: ["Януари", "Февруари", "Март", "Април", "Май", "Юни", "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"],
    monthNamesShort: ["Яну", "Фев", "Мар", "Апр", "Май", "Юни", "Юли", "Авг", "Сеп", "Окт", "Нов", "Дек"],
    dayNames: ["Неделя", "Понеделник", "Вторник", "Сряда", "Четвъртък", "Петък", "Събота"],
    dayNamesShort: ["Нед", "Пон", "Вто", "Сря", "Чет", "Пет", "Съб"],
    dayNamesMin: ["Не", "По", "Вт", "Ср", "Че", "Пе", "Съ"],
    weekHeader: "Сед",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.da = {
    closeText: "Luk",
    prevText: "Forrige",
    nextText: "Næste",
    currentText: "I dag",
    monthNames: ["Januar", "Februar", "Marts", "April", "Maj", "Juni", "Juli", "August", "September", "Oktober", "November", "December"],
    monthNamesShort: ["Jan", "Feb", "Mar", "Apr", "Maj", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"],
    dayNames: ["Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"],
    dayNamesShort: ["Søn", "Man", "Tir", "Ons", "Tor", "Fre", "Lør"],
    dayNamesMin: ["Sø", "Ma", "Ti", "On", "To", "Fr", "Lø"],
    weekHeader: "Uge",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.sk = {
    closeText: "Zavrieť",
    prevText: "Predchádzajúci",
    nextText: "Nasledujúci",
    currentText: "Dnes",
    monthNames: ["január", "február", "marec", "apríl", "máj", "jún", "júl", "august", "september", "október", "november", "december"],
    monthNamesShort: ["Jan", "Feb", "Mar", "Apr", "Máj", "Jún", "Júl", "Aug", "Sep", "Okt", "Nov", "Dec"],
    dayNames: ["nedeľa", "pondelok", "utorok", "streda", "štvrtok", "piatok", "sobota"],
    dayNamesShort: ["Ned", "Pon", "Uto", "Str", "Štv", "Pia", "Sob"],
    dayNamesMin: ["Ne", "Po", "Ut", "St", "Št", "Pia", "So"],
    weekHeader: "Ty",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.hi = {
    closeText: "बंद",
    prevText: "पिछला",
    nextText: "अगला",
    currentText: "आज",
    monthNames: ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"],
    monthNamesShort: ["जन", "फर", "मार्च", "अप्रै", "मई", "जून", "जुल", "अग", "सित", "अक्ट", "नव", "दिस"],
    dayNames: ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"],
    dayNamesShort: ["रवि", "सोम", "मंगल", "बुध", "गुरु", "शुक्र", "शनि"],
    dayNamesMin: ["रवि", "सोम", "मंगल", "बुध", "गुरु", "शुक्र", "शनि"],
    weekHeader: "हफ्ता",
    dateFormat: "d MM yy",
    firstDay: 0,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.et = {
    closeText: "Sulge",
    prevText: "Eelnev",
    nextText: "Järgnev",
    currentText: "Täna",
    monthNames: ["Jaanuar", "Veebruar", "Märts", "Aprill", "Mai", "Juuni", "Juuli", "August", "September", "Oktoober", "November", "Detsember"],
    monthNamesShort: ["Jaan", "Veebr", "Märts", "Apr", "Mai", "Juuni", "Juuli", "Aug", "Sept", "Okt", "Nov", "Dets"],
    dayNames: ["Pühapäev", "Esmaspäev", "Teisipäev", "Kolmapäev", "Neljapäev", "Reede", "Laupäev"],
    dayNamesShort: ["Pühap", "Esmasp", "Teisip", "Kolmap", "Neljap", "Reede", "Laup"],
    dayNamesMin: ["P", "E", "T", "K", "N", "R", "L"],
    weekHeader: "näd",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.regional.hr = {
    closeText: "Zatvori",
    prevText: "Prethodno",
    nextText: "Sljedeći",
    currentText: "Danas",
    monthNames: ["Siječanj", "Veljača", "Ožujak", "Travanj", "Svibanj", "Lipanj", "Srpanj", "Kolovoz", "Rujan", "Listopad", "Studeni", "Prosinac"],
    monthNamesShort: ["Sij", "Velj", "Ožu", "Tra", "Svi", "Lip", "Srp", "Kol", "Ruj", "Lis", "Stu", "Pro"],
    dayNames: ["Nedjelja", "Ponedjeljak", "Utorak", "Srijeda", "Četvrtak", "Petak", "Subota"],
    dayNamesShort: ["Ned", "Pon", "Uto", "Sri", "Čet", "Pet", "Sub"],
    dayNamesMin: ["Ne", "Po", "Ut", "Sr", "Če", "Pe", "Su"],
    weekHeader: "Tje",
    dateFormat: "d MM yy",
    firstDay: 1,
    isRTL: false,
    showMonthAfterYear: false,
    yearSuffix: ""
};

$.datepicker.setDefaults($.datepicker.regional[$('html').attr('lang')]);

evil.block('@@RegistrationForm', {

    _generateSlug: function () {
        var components = [this.firstNameField.val(), this.lastNameField.val()];
        components = components.filter(function (i) {
            return i
        });
        var slug = components.join('_');
        slug = slug.toLowerCase();
        slug = slug.replace(' ', '_');
        slug = slug.replace(/[^\x00-\x7F]/g, '');
        return slug;
    },

    init: function () {
        this.slugField = this.$('#id_slug');
        this.firstNameField = this.$('#id_first_name');
        this.lastNameField = this.$('#id_last_name');
        this.slugChanged = (this.slugField.val() != this._generateSlug());
        init_datepicker();
    },

    'change on #id_slug': function () {
        this.slugChanged = true;
    },

    'keyup on #id_first_name, #id_last_name': function () {
        if (!this.slugChanged) {
            this.slugField.val(
                this._generateSlug()
            );
        }
    }

});


evil.block('@@ProfileForm', {
    init: init_datepicker
});


evil.block('@@AutoForm', {
    'change on select': function () {
        this.$('form').submit();
    }
});


evil.block('@@MessageList', {
    init: function () {
        var _this = this;
        if (this.block.data('page-number') === 1) {
            window.setInterval(function () {
                _this.poll();
            }, 5000);
        }
    },

    poll: function () {
        var _this = this;
        if (this.block.data('page-number') === 1) {
            if (!((window.localStorage !== null) && (window.localStorage.getItem('logged-in') === 'false'))) {
                var url = this.block.data('poll-url');
                var since = this.$('@message').first().data('timestamp');
                url += '?since=' + since;
                $.ajax(url).done(function (data) {
                    $(data).prependTo(_this.block);
                }).fail(function (jqXHR) {
                    if ((jqXHR.status === 403) && (window.localStorage !== null)) {
                        window.localStorage.setItem('logged-in', 'false');
                    }
                });
            }
        }
    }
});


evil.block('@@Uploader', {

    blankState: function () {
        this.progress.hide();
        this.filename.hide();
        this.browseButton.show();
    },

    boundState: function () {
        this.blankState();
        this.filename.show();
    },

    progressState: function () {
        this.progress.show();
        this.progressBar.width(0);
        this.filename.hide();
        this.browseButton.hide();
    },

    startUpload: function (file) {
        var _this = this;
        this.progressState();
        var data = new FormData();
        data.append('file', file);
        $.ajax({
            url: this.block.data('action'),
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            xhr: function () {
                var xhr = $.ajaxSettings.xhr();
                if (xhr.upload) {
                    xhr.upload.addEventListener('progress', function (evt) {
                        var percent = Math.round(evt.loaded / evt.total * 100);
                        _this.progressBar.css('width', percent + '%');
                        if (percent == 100) {
                            _this.progressBar.addClass('active');
                            _this.progress.addClass('progress-striped');
                        } else {
                            _this.progressBar.removeClass('active');
                            _this.progress.removeClass('progress-striped');
                        }
                    }, false);
                }
                return xhr;
            }
        }).done(function (data, textStatus, jqXHR) {
            _this.boundState();
            _this.filename.text(data.files[0].name);
            _this.realInput.val(data.files[0].uuid);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            var data = jqXHR.responseJSON;
            for (var errorField in data) {
                if (data.hasOwnProperty(errorField)) {
                    alert(data[errorField]);
                    _this.blankState();
                    break;
                }
            }
        });
    },

    init: function () {
        if (this.realInput.val()) {
            this.boundState();
        } else {
            this.blankState();
        }
    },

    'click on @browseButton': function (event) {
        event.preventDefault();
        this.fileInput.trigger('click');
    },

    'change on @fileInput': function (event) {
        event.preventDefault();
        files = this.fileInput[0].files;
        if (files.length) {
            this.startUpload(files[0]);
        }
    }

});

window.speedy = {};

window.speedy.setSession = function (domain, key) {
    $.ajax({
        url: '//' + domain + '/set-session/',
        method: 'post',
        data: {
            key: key
        },
        xhrFields: {
            withCredentials: true
        }
    });
};

$(document).ready(function () {
    $(".form-control-danger").addClass("is-invalid"); // A hack to work with django-crispy-forms 1.6.1.

    $('form[method="post"]').submit(function () {
        $(this).find(':input[type="submit"]').prop('disabled', true);
    });
});

var isRTL = $("body").hasClass("bidi-rtl");
if (isRTL) {
    Popper.Defaults.modifiers.preventOverflowRTL = {
        enabled: true,
        order: 301, // preventOverflow order: 300
        fn: (data) => {
            var preventOverflow = data.instance.modifiers.find(modifier => modifier.name == 'preventOverflow');
            var isOverflowLeft = data.popper.width > data.offsets.reference.width + Math.abs(preventOverflow.boundaries.left);
            if (isOverflowLeft) {
                left = Math.floor(preventOverflow.boundaries.left);
                data.styles['left'] = left;
                data.styles['right'] = 'auto';
            } else {
                data.styles['left'] = '';
                data.styles['right'] = '';
            }
            return data;
        }
    };

    Popper.Defaults.modifiers.computeStyleRTL = {
        enabled: true,
        order: 851, // computeStyle order: 850
        fn: (data) => {
            var left = -Math.floor(data.popper.left); // RTL
            var top = Math.floor(data.popper.top);
            data.styles['transform'] = `translate3d(${left}px, ${top}px, 0)`;
            return data;
        }
    };
}

