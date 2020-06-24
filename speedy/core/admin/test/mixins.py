class SpeedyCoreAdminLanguageMixin(object):
    def set_up(self):
        super().set_up()

        _permission_denied_h1_dict = {'en': "Permission Denied", 'he': "ההרשאה נדחתה"}
        _speedy_is_sorry_but_this_page_is_private_alert_dict = {'en': "Speedy is sorry, but this page is private.", 'he': "ספידי מצטערת, אבל הדף הזה פרטי."}

        self._permission_denied_h1 = _permission_denied_h1_dict[self.language_code]
        self._speedy_is_sorry_but_this_page_is_private_alert = _speedy_is_sorry_but_this_page_is_private_alert_dict[self.language_code]


