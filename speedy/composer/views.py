# from django.conf import settings
# from django.db.models import Q
# from django.http import Http404
# from django.shortcuts import redirect
# from django.utils import translation
# from django.utils.module_loading import import_string
from django.views import generic
# from rules.contrib.views import LoginRequiredMixin
#
# from speedy.net.accounts.models import User, normalize_username
# from speedy.net.friends.rules import friend_request_sent, is_friend


class MainPageView(generic.TemplateView):
    template_name = 'main_page.html'

