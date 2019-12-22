from django.conf import settings as django_settings
from django.utils.module_loading import import_string
from django.views import generic

from speedy.core.admin.mixins import OnlyAdminMixin
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.accounts.models import User
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile

if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
    from speedy.match.profiles.views import UserDetailView
else:
    from speedy.core.profiles.views import UserDetailView


class AdminUsersListView(OnlyAdminMixin, generic.ListView):
    template_name = 'admin/users_list.html'
    page_size = 96
    paginate_by = page_size
    show_details = False

    def get_queryset(self):
        SiteProfile = get_site_profile_model()
        qs = User.objects.all().prefetch_related(SpeedyNetSiteProfile.RELATED_NAME, SpeedyMatchSiteProfile.RELATED_NAME).distinct().order_by('-{}__last_visit'.format(SiteProfile.RELATED_NAME))
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'users_list': cd['object_list'],
            'show_details': self.show_details,
        })
        return cd


class AdminUsersWithDetailsListView(AdminUsersListView):
    show_details = True


class AdminUserDetailView(OnlyAdminMixin, UserDetailView):
    template_name = 'admin/profiles/user_detail.html'
    admin_widgets = {
        'speedy.core.profiles.widgets.UserInfoWidget': 'speedy.core.profiles.admin.widgets.AdminUserInfoWidget',
    }

    def get_widgets(self):
        widgets = []
        for widget_path in django_settings.USER_PROFILE_WIDGETS:
            if (widget_path in self.admin_widgets):
                widget_path = self.admin_widgets[widget_path]
            widget_class = import_string(widget_path)
            widgets.append(widget_class(**self.get_widget_kwargs()))
        return widgets

