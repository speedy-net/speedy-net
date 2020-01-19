from datetime import timedelta, datetime, timezone

from django.conf import settings as django_settings
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.views import generic
from django.db.models import F

from speedy.core.base.utils import to_attribute
from speedy.core.admin.mixins import OnlyAdminMixin
from speedy.core.accounts.utils import get_site_profile_model
from speedy.core.accounts.models import User
from speedy.net.accounts.models import SiteProfile as SpeedyNetSiteProfile

if (django_settings.SITE_ID == django_settings.SPEEDY_MATCH_SITE_ID):
    from speedy.match.profiles.views import UserDetailView
else:
    from speedy.core.profiles.views import UserDetailView


class AdminUsersListView(OnlyAdminMixin, generic.ListView):
    template_name = 'admin/users_list.html'
    page_size = 96
    paginate_by = page_size
    show_details = False

    @staticmethod
    def get_total_number_of_members_text():
        total_number_of_members = User.objects.all().count()
        total_number_of_members_in_the_last_week = User.objects.filter(
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=7),
        ).count()
        total_number_of_members_in_the_last_month = User.objects.filter(
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=30),
        ).count()
        total_number_of_members_in_the_last_four_months = User.objects.filter(
            speedy_match_site_profile__last_visit__gte=now() - timedelta(days=120),
        ).count()
        total_number_of_members_text = _("Admin: The total number of members on the site is {total_number_of_members}, of which {total_number_of_members_in_the_last_week} members entered the site in the last week, {total_number_of_members_in_the_last_month} members entered the site in the last month, and {total_number_of_members_in_the_last_four_months} members entered the site in the last four months.").format(
            total_number_of_members='{:,}'.format(total_number_of_members),
            total_number_of_members_in_the_last_week='{:,}'.format(total_number_of_members_in_the_last_week),
            total_number_of_members_in_the_last_month='{:,}'.format(total_number_of_members_in_the_last_month),
            total_number_of_members_in_the_last_four_months='{:,}'.format(total_number_of_members_in_the_last_four_months),
        )
        return total_number_of_members_text

    @staticmethod
    def get_total_number_of_members_date_registered_text():
        total_number_of_members_registered_in_the_last_week = User.objects.filter(
            date_created__gte=now() - timedelta(days=7),
        ).count()
        total_number_of_members_registered_in_the_last_month = User.objects.filter(
            date_created__gte=now() - timedelta(days=30),
        ).count()
        total_number_of_members_registered_in_the_last_four_months = User.objects.filter(
            date_created__gte=now() - timedelta(days=120),
        ).count()
        total_number_of_members_registered_more_than_four_months_ago = User.objects.filter(
            date_created__lte=now() - timedelta(days=120),
        ).count()
        total_number_of_members_registered_before_2019_08_01 = User.objects.filter(
            date_created__lte=datetime.strptime('2019-08-01 00:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc),
        ).count()
        total_number_of_members_date_registered_text = _("Admin: {total_number_of_members_registered_in_the_last_week} members registered in the last week. {total_number_of_members_registered_in_the_last_month} members registered in the last month. {total_number_of_members_registered_in_the_last_four_months} members registered in the last four months. {total_number_of_members_registered_more_than_four_months_ago} members registered more than four months ago. {total_number_of_members_registered_before_2019_08_01} members registered before 1 August 2019.").format(
            total_number_of_members_registered_in_the_last_week='{:,}'.format(total_number_of_members_registered_in_the_last_week),
            total_number_of_members_registered_in_the_last_month='{:,}'.format(total_number_of_members_registered_in_the_last_month),
            total_number_of_members_registered_in_the_last_four_months='{:,}'.format(total_number_of_members_registered_in_the_last_four_months),
            total_number_of_members_registered_more_than_four_months_ago='{:,}'.format(total_number_of_members_registered_more_than_four_months_ago),
            total_number_of_members_registered_before_2019_08_01='{:,}'.format(total_number_of_members_registered_before_2019_08_01),
        )
        return total_number_of_members_date_registered_text

    def get_queryset(self):
        SiteProfile = get_site_profile_model()
        if (self.request.GET.get('order_by') == 'number_of_friends'):
            qs = User.objects.all().order_by(F('{}__{}'.format(SpeedyNetSiteProfile.RELATED_NAME, to_attribute(name='number_of_friends'))).desc(nulls_last=True), '-{}__last_visit'.format(SiteProfile.RELATED_NAME))
        else:
            qs = User.objects.all().order_by('-{}__last_visit'.format(SiteProfile.RELATED_NAME))
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'users_list': cd['object_list'],
            'show_details': self.show_details,
            'total_number_of_members_text': self.get_total_number_of_members_text(),
            'total_number_of_members_date_registered_text': self.get_total_number_of_members_date_registered_text(),
        })
        return cd


class AdminUsersWithDetailsListView(AdminUsersListView):
    show_details = True


class AdminUserDetailView(OnlyAdminMixin, UserDetailView):
    template_name = 'admin/profiles/user_detail.html'

    def get_widgets(self):
        widgets = []
        for widget_path in django_settings.ADMIN_USER_PROFILE_WIDGETS:
            widget_class = import_string(widget_path)
            widgets.append(widget_class(**self.get_widget_kwargs()))
        return widgets


