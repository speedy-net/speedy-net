from speedy.core.profiles.widgets import UserPhotoWidget, UserInfoWidget


class AdminUserPhotoWidget(UserPhotoWidget):
    template_name = 'admin/profiles/user_photo_widget.html'


class AdminUserInfoWidget(UserInfoWidget):
    template_name = 'admin/profiles/user_info_widget.html'


