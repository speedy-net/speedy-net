from speedy.core.profiles.widgets import UserPhotoWidget, UserInfoWidget


class AdminUserPhotoWidget(UserPhotoWidget):
    """
    Widget that renders a user's profile photo for the Django admin.
    """
    template_name = 'admin/profiles/user_photo_widget.html'


class AdminUserInfoWidget(UserInfoWidget):
    """
    Widget that renders a user's profile info for the Django admin.
    """
    template_name = 'admin/profiles/user_info_widget.html'


