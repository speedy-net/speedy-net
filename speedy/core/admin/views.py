from django.views import generic

from speedy.core.admin.mixins import OnlyAdminMixin
from speedy.core.accounts.models import User
from speedy.match.accounts.models import SiteProfile as SpeedyMatchSiteProfile


class AdminUsersListView(OnlyAdminMixin, generic.ListView):
    template_name = 'admin/users_list.html'
    page_size = 24
    paginate_by = page_size

    def get_queryset(self):
        qs = User.objects.active().prefetch_related(SpeedyMatchSiteProfile.RELATED_NAME).distinct().order_by('-speedy_net_site_profile__last_visit')
        return qs

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'users_list': cd['object_list'],
        })
        return cd


