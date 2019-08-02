from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class StaticBaseView(generic.TemplateView):
    # canonical_full_path must be defined in classes inherited from this class.

    def get(self, request, *args, **kwargs):
        if (request.get_full_path() == self.canonical_full_path):
            return super().get(request=request, *args, **kwargs)
        else:
            return redirect(to=self.canonical_full_path, permanent=True)

    class Meta:
        abstract = True


class StaticMainPageBaseView(StaticBaseView):
    canonical_full_path = "/"

    class Meta:
        abstract = True


class StaticAboutBaseView(StaticBaseView):
    canonical_full_path = "/about/"

    class Meta:
        abstract = True


class StaticPrivacyPolicyBaseView(StaticBaseView):
    canonical_full_path = "/privacy/"

    class Meta:
        abstract = True


class StaticTermsOfServiceBaseView(StaticBaseView):
    canonical_full_path = "/terms/"

    class Meta:
        abstract = True


class StaticContactUsBaseView(StaticBaseView):
    canonical_full_path = "/contact/"

    class Meta:
        abstract = True


class FormValidMessageMixin(object):
    form_valid_message = _('Changes saved.')

    def get_form_valid_message(self, form):
        return self.form_valid_message

    def form_valid(self, form):
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=self.get_form_valid_message(form=form))
        return response


class PaginationMixin(object):
    def dispatch(self, request, *args, **kwargs):
        object_list = self.get_object_list()
        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(object_list, self.page_size)
        try:
            page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            return redirect(to='matches:list')
        self.paginator = paginator
        self.page = page
        return super().dispatch(request=request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'paginator': self.paginator,
            'page_obj': self.page,
            'is_paginated': self.page.has_other_pages(),
        })
        return cd


