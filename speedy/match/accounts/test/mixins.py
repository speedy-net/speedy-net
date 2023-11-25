from django.conf import settings as django_settings

if (django_settings.TESTS):
    from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


    class SpeedyMatchAccountsModelsMixin(object):
        def assert_step_and_error_messages_ok(self, step, error_messages):
            self.assertEqual(first=step, second=len(SpeedyMatchSiteProfile.settings.SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS))
            self.assertEqual(first=step, second=10)
            self.assertEqual(first=len(error_messages), second=0)
            self.assertListEqual(list1=error_messages, list2=[])


    class SpeedyMatchAccountsLanguageMixin(object):
        def _item_in_the_array_did_not_validate_error_message_by_index(self, index):
            return self._item_in_the_array_did_not_validate_error_message_to_format.format(index=index)

        def _item_in_the_array_did_not_validate_value_is_not_a_valid_choice_errors_dict_by_field_name_and_index_and_value(self, field_name, index, value):
            return {field_name: ["{}{}".format(self._item_in_the_array_did_not_validate_error_message_by_index(index=index), self._value_is_not_a_valid_choice_error_message_by_value(value=value))]}

        def set_up(self):
            super().set_up()

            _a_profile_picture_is_required_error_message_dict = {'en': "A profile picture is required.", 'fr': "Une photo de profil est requise.", 'de': "Ein Profilbild ist erforderlich.", 'es': "Se requiere una foto de perfil.", 'pt': "A foto do perfil é obrigatória.", 'it': "È un’immagine del profilo.", 'nl': "Een profielfoto is verplicht.", 'he': "נדרשת תמונת פרופיל."}
            _please_write_a_few_words_about_yourself_error_message_dict = {'en': "Please write a few words about yourself.", 'fr': "Veuillez vous présenter en quelques mots.", 'de': "Bitte schreiben Sie einige Worte über sich selbst.", 'es': "Escribe algunas palabras sobre ti.", 'pt': "Escreva algumas palavras sobre ti.", 'it': "Scrivi una breve descrizione di te stesso/a.", 'nl': "Schrijf een paar woorden over jezelf.", 'he': "אנא כתוב/י כמה מילים על עצמך."}
            _please_write_where_you_live_error_message_dict = {'en': "Please write where you live.", 'fr': "Veuillez indiquer votre ville de résidence.", 'de': "Bitte schreiben Sie, wo Sie wohnen.", 'es': "Escribe dónde vives.", 'pt': "Escreva o local da tua morada.", 'it': "Scrivi dove vivi.", 'nl': "Schrijf alstublieft waar je woont.", 'he': "אנא כתוב/י איפה את/ה גר/ה."}
            _do_you_have_children_how_many_error_message_dict = {'en': "Do you have children? How many?", 'fr': "Avez-vous des enfants\xa0? Combien\xa0?", 'de': "Haben Sie Kinder? Wie viele?", 'es': "¿Tienes hijos? ¿Cuántos?", 'pt': "Tens filhos? Quantos?", 'it': "Hai figli? Quanti?", 'nl': "Heb je kinderen? Hoeveel?", 'he': "יש לך ילדים? כמה?"}
            _do_you_want_more_children_error_message_dict = {'en': "Do you want (more) children?", 'fr': "Voulez-vous (plus) d’enfants\xa0?", 'de': "Möchten Sie (mehr) Kinder?", 'es': "¿Quieres (más) hijos?", 'pt': "Quer ter (mais) filhos?", 'it': "Vuoi (altri) figli?", 'nl': "Wil je (meer) kinderen?", 'he': "את/ה רוצה (עוד) ילדים?"}
            _who_is_your_ideal_partner_error_message_dict = {'en': "Who is your ideal partner?", 'fr': "Qui est votre partenaire idéal\xa0?", 'de': "Wer ist Ihr idealer Partner?", 'es': "¿Quién es tu pareja ideal?", 'pt': "Quem é a tua parceria ideal?", 'it': "Chi è il/la tuo/a partner ideale?", 'nl': "Wie is jouw ideale partner?", 'he': "מי בן או בת הזוג האידיאלי/ת שלך?"}
            _height_must_be_from_1_to_450_cm_error_message_dict = {'en': "Height must be from 1 to 450 cm.", 'fr': "La hauteur doit être comprise entre 1 et 450\xa0cm.", 'de': "Die Höhe muss 1 bis 450 cm betragen.", 'es': "La estatura debe ser de 1 a 450 cm.", 'pt': "Altura deve ser entre 1 e 450 cm.", 'it': "L’altezza deve essere compresa tra 1 e 450 cm.", 'nl': "Lengte moet tussen 1 en 450 cm liggen.", 'he': 'הגובה חייב להיות בין 1 ל-450 ס"מ.'}
            _your_diet_is_required_error_message_dict = {'en': "Your diet is required.", 'fr': "Veuillez renseigner votre régime alimentaire.", 'de': "Ihre Ernährungsweise ist erforderlich.", 'es': "Se requiere tu dieta.", 'pt': "Tua dieta é obrigatória.", 'it': "La tua dieta è richiesta.", 'nl': "Je dieet is verplicht.", 'he': "התזונה שלך נדרשת."}
            _your_smoking_status_is_required_error_message_dict = {'en': "Your smoking status is required.", 'fr': "Veuillez spécifier si vous êtes fumeur.", 'de': "Ihr Raucherstatus ist erforderlich.", 'es': "Se requiere tu condición de fumador.", 'pt': "Teu status como fumante é obrigatório.", 'it': "Sono richieste informazioni in merito al fumo.", 'nl': "Je rookstatus is verplicht.", 'he': "הרגלי העישון שלך נדרשים."}
            _your_relationship_status_is_required_error_message_dict = {'en': "Your relationship status is required.", 'fr': "Veuillez spécifier si vous êtes en couple.", 'de': "Ihr Beziehungsstatus ist erforderlich.", 'es': "Se requiere tu estado de relaciones.", 'pt': "Teu status de relacionamento é obrigatório.", 'it': "È richiesto lo stato della tua relazione.", 'nl': "Je relatiestatus is verplicht.", 'he': "סטטוס מערכת היחסים שלך נדרש."}
            _gender_to_match_is_required_error_message_dict = {'en': "Gender to match is required.", 'fr': "Veuillez renseigner le genre souhaité.", 'de': "Das Match-Geschlecht ist erforderlich.", 'es': "Se requiere que el género coincida.", 'pt': "O gênero para correspondência é obrigatório.", 'it': "Il genere della corrispondenza è richiesto.", 'nl': "Geslacht voor matchen is verplicht.", 'he': "מין בן/בת הזוג שלך נדרש."}
            _minimal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': "Minimal age to match must be from 0 to 180 years.", 'fr': "L’âge minimum concordant doit être compris entre 0 et 180\xa0ans.", 'de': "Das übereinstimmende Mindestalter muss zwischen 0 und 180 Jahren liegen.", 'es': "La edad mínima para coincidir debe ser de 0 a 180 años.", 'pt': "Idade mínima para correspondência deve ser entre 0 e 180 anos.", 'it': "L’età minima della corrispondenza deve essere compresa tra 0 e 180 anni.", 'nl': "De minimale leeftijd voor matchen moet tussen 0 en 180 jaar liggen.", 'he': "הגיל המינימלי לבן/בת הזוג חייב להיות בין 0 ל-180 שנה."}
            _maximal_age_to_match_must_be_from_0_to_180_years_error_message_dict = {'en': "Maximal age to match must be from 0 to 180 years.", 'fr': "L’âge maximum concordant doit être compris entre 0 et 180\xa0ans.", 'de': "Das übereinstimmende Höchstalter muss zwischen 0 und 180 Jahren liegen.", 'es': "La edad máxima para coincidir debe ser de 0 a 180 años.", 'pt': "Idade máxima para correspondência deve ser entre 0 e 180 anos.", 'it': "L’età massima della corrispondenza deve essere compresa tra 0 e 180 anni.", 'nl': "De maximale leeftijd voor matchen moet tussen 0 en 180 jaar liggen.", 'he': "הגיל המקסימלי לבן/בת הזוג חייב להיות בין 0 ל-180 שנה."}
            _maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message_dict = {'en': "Maximal age to match can't be less than minimal age to match.", 'fr': "L’âge maximal concordant ne peut être inférieur à l’âge minimal concordant.", 'de': "Das übereinstimmende Höchstalter kann nicht niedriger als das übereinstimmende Mindestalter sein.", 'es': "La edad máxima para igualar no puede ser menor que la edad mínima para igualar.", 'pt': "Idade máxima para correspondência não pode ser menor do que a idade mínima.", 'it': "L’età massima della corrispondenza non può essere inferiore all’età minima.", 'nl': "De maximale bijpassende leeftijd mag niet lager zijn dan de minimumleeftijd.", 'he': "הגיל המקסימלי לבן/בת הזוג לא יכול להיות פחות מהגיל המינימלי לבן/בת הזוג."}
            _diet_match_is_required_error_message_dict = {'en': "Diet match is required.", 'fr': "Concordance de régimes alimentaires requise.", 'de': "Ernährungs-Match ist erforderlich.", 'es': "Se requiere una dieta acorde.", 'pt': "A correspondência de dieta é obrigatória.", 'it': "È richiesta una corrispondenza con la dieta.", 'nl': "Dieetmatch is verplicht.", 'he': "התאמת התזונה נדרשת."}
            _smoking_status_match_is_required_error_message_dict = {'en': "Smoking status match is required.", 'fr': "Concordance de statut de fumeur requise.", 'de': "Raucherstatus-Match ist erforderlich.", 'es': "Se requiere coincidencia de condición de fumador.", 'pt': "A correspondência de status como fumante é obrigatória.", 'it': "È richiesta la corrispondenza con lo stato di fumatore.", 'nl': "Matchen van de rookstatus is vereist.", 'he': "התאמת הרגלי העישון נדרשת."}
            _relationship_status_match_is_required_error_message_dict = {'en': "Relationship status match is required.", 'fr': "Concordance du statut relationnel est requise.", 'de': "Beziehungsstatus-Match ist erforderlich.", 'es': "Se requiere coincidencia de estado de relaciones.", 'pt': "A correspondência de status de relacionamento é obrigatória.", 'it': "È richiesta una corrispondenza con lo stato della relazione.", 'nl': "Matchen van de relatiestatus is vereist.", 'he': "התאמת סטטוס מערכת היחסים נדרשת."}
            _at_least_one_diet_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one diet match option should be five hearts.", 'fr': "Au moins une option de concordance de régime alimentaire doit être de cinq cœurs.", 'de': "Mindestens eine Ernährungsoption sollte aus fünf Herzen bestehen.", 'es': "Al menos una opción de combinación de dieta debe ser cinco corazones.", 'pt': "No mínimo uma opção de correspondência de dieta deve ser de cinco corações.", 'it': "Almeno un’opzione di corrispondenza alla dieta deve essere a cinque cuori.", 'nl': "Ten minste één dieetmatchoptie moet vijf harten zijn.", 'he': "לפחות אפשרות אחת להתאמת תזונה צריכה להיות חמישה לבבות."}
            _at_least_one_smoking_status_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one smoking status match option should be five hearts.", 'fr': "Au moins une option de concordance de statut de fumeur doit être de cinq cœurs.", 'de': "Mindestens eine Raucher-Status-Option sollte aus fünf Herzen bestehen.", 'es': "Al menos una opción de coincidencia de condición de fumador debe ser cinco corazones.", 'pt': "No mínimo uma opção de correspondência de status como fumante deve ser de cinco corações.", 'it': "Almeno un’opzione di corrispondenza allo stato di fumatore deve essere di cinque cuori.", 'nl': "Ten minste één matchoptie voor de rookstatus moet vijf harten zijn.", 'he': "לפחות אפשרות אחת להתאמת הרגלי עישון צריכה להיות חמישה לבבות."}
            _at_least_one_relationship_status_match_option_should_be_5_hearts_error_message_dict = {'en': "At least one relationship status match option should be five hearts.", 'fr': "Au moins une option de concordance du statut relationnel doit être à cinq cœurs.", 'de': "Mindestens eine Beziehungsstatus-Option sollte aus fünf Herzen bestehen.", 'es': "Al menos una opción de coincidencia de estado de relación debe ser cinco corazones.", 'pt': "No mínimo uma opção de correspondência de status de relacionamento deve ser de cinco corações.", 'it': "Almeno un’opzione di corrispondenza dello stato relazionale deve essere di cinque cuori.", 'nl': "Ten minste één matchoptie voor de relatiestatus moet vijf harten zijn.", 'he': "לפחות אפשרות אחת להתאמת סטטוס מערכת יחסים צריכה להיות חמישה לבבות."}

            _item_in_the_array_did_not_validate_error_message_to_format_dict = {'en': "Item {index} in the array did not validate: ", 'fr': "Item {index} in the array did not validate: ", 'de': "Item {index} in the array did not validate: ", 'es': "Item {index} in the array did not validate: ", 'pt': "Item {index} in the array did not validate: ", 'it': "Item {index} in the array did not validate: ", 'nl': "Item {index} in the array did not validate: ", 'he': "Item {index} in the array did not validate: "}

            self._a_profile_picture_is_required_error_message = _a_profile_picture_is_required_error_message_dict[self.language_code]
            self._please_write_a_few_words_about_yourself_error_message = _please_write_a_few_words_about_yourself_error_message_dict[self.language_code]
            self._please_write_where_you_live_error_message = _please_write_where_you_live_error_message_dict[self.language_code]
            self._do_you_have_children_how_many_error_message = _do_you_have_children_how_many_error_message_dict[self.language_code]
            self._do_you_want_more_children_error_message = _do_you_want_more_children_error_message_dict[self.language_code]
            self._who_is_your_ideal_partner_error_message = _who_is_your_ideal_partner_error_message_dict[self.language_code]
            self._height_must_be_from_1_to_450_cm_error_message = _height_must_be_from_1_to_450_cm_error_message_dict[self.language_code]
            self._your_diet_is_required_error_message = _your_diet_is_required_error_message_dict[self.language_code]
            self._your_smoking_status_is_required_error_message = _your_smoking_status_is_required_error_message_dict[self.language_code]
            self._your_relationship_status_is_required_error_message = _your_relationship_status_is_required_error_message_dict[self.language_code]
            self._gender_to_match_is_required_error_message = _gender_to_match_is_required_error_message_dict[self.language_code]
            self._minimal_age_to_match_must_be_from_0_to_180_years_error_message = _minimal_age_to_match_must_be_from_0_to_180_years_error_message_dict[self.language_code]
            self._maximal_age_to_match_must_be_from_0_to_180_years_error_message = _maximal_age_to_match_must_be_from_0_to_180_years_error_message_dict[self.language_code]
            self._maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message = _maximal_age_to_match_cant_be_less_than_minimal_age_to_match_error_message_dict[self.language_code]
            self._diet_match_is_required_error_message = _diet_match_is_required_error_message_dict[self.language_code]
            self._smoking_status_match_is_required_error_message = _smoking_status_match_is_required_error_message_dict[self.language_code]
            self._relationship_status_match_is_required_error_message = _relationship_status_match_is_required_error_message_dict[self.language_code]
            self._at_least_one_diet_match_option_should_be_5_hearts_error_message = _at_least_one_diet_match_option_should_be_5_hearts_error_message_dict[self.language_code]
            self._at_least_one_smoking_status_match_option_should_be_5_hearts_error_message = _at_least_one_smoking_status_match_option_should_be_5_hearts_error_message_dict[self.language_code]
            self._at_least_one_relationship_status_match_option_should_be_5_hearts_error_message = _at_least_one_relationship_status_match_option_should_be_5_hearts_error_message_dict[self.language_code]

            self._item_in_the_array_did_not_validate_error_message_to_format = _item_in_the_array_did_not_validate_error_message_to_format_dict[self.language_code]


