from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext as _
from django.views import generic
from rules.contrib.views import LoginRequiredMixin

from speedy.core.accounts.views import ActivateSiteProfileView as CoreActivateSiteProfileView
from speedy.core.accounts.views import IndexView as CoreIndexView, \
    EditProfileNotificationsView as CoreEditProfileNotificationsView
from speedy.core.base.views import FormValidMessageMixin
from . import forms



class IndexView(CoreIndexView):
    registered_redirect_to = 'matches:list'


class ActivateSiteProfileView(CoreActivateSiteProfileView):
    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'steps_range': list(range(1, len(settings.SITE_PROFILE_FORM_FIELDS))),
            'current_step': self.step,
            'previous_step': self.step - 1,
        })
        return cd

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['step'] = self.step
        if 'gender_to_match' in self.request.POST:
            kwargs['data']['gender_to_match'] = ','.join(self.request.POST.getlist('gender_to_match'))
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        try:
            self.step = int(kwargs['step'])
        except (KeyError, ValueError):
            return redirect('accounts:activate', step=self.request.user.profile.activation_step)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        SPEEDY_NET_SITE_ID = settings.SITE_PROFILES['net']['site_id']
        if not request.user.is_active:
            return render(self.request, self.template_name,
                          {'speedy_net_url': Site.objects.get(id=SPEEDY_NET_SITE_ID).domain})
        if self.step == 1:
            return redirect('accounts:edit_profile')
        # else:
        #     step, errors = self.request.user.profile.validate_profile_and_activate()
        #     if (self.request.user.profile.activation_step == 0) and (
        #         step == len(settings.SITE_PROFILE_FORM_FIELDS)) and not self.request.user.has_confirmed_email():
        #         return redirect(reverse_lazy('accounts:edit_profile_credentials'))
        return super().get(self.request, *args, **kwargs)

    def get_account_activation_url(self):
        return reverse_lazy('accounts:activate', kwargs={'step': self.step})

    def get_success_url(self):
        if self.step >= len(settings.SITE_PROFILE_FORM_FIELDS) - 1:
            return '/'
        else:
            return reverse_lazy('accounts:activate', kwargs={'step': self.step + 1})

    def form_valid(self, form):
        super().form_valid(form=form)
        site = Site.objects.get_current()
        if self.object.is_active:
            messages.success(self.request,
                             pgettext_lazy(context=self.request.user.get_gender(), message='Welcome to {}!').format(
                                 _(site.name)))
        if self.request.user.profile.is_active:
            return redirect(to=reverse_lazy('matches:list'))
        else:
            return redirect(to=self.get_success_url())


class EditProfileNotificationsView(CoreEditProfileNotificationsView):
    form_class = forms.ProfileNotificationsForm
