"""
Base views and view mixins of Speedy Core, including static page views and pagination.
"""
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class StaticBaseView(generic.TemplateView):
    """
    A base view for static pages, redirecting to the canonical URL if the requested path doesn't match it exactly.

    Attributes:
        canonical_full_path (str): The canonical full path of the page. Must be defined in classes inherited from this class.

    Methods:
        get: Serves the page if the request matches the canonical path, otherwise redirects to it.
    """

    # canonical_full_path must be defined in classes inherited from this class.

    def get(self, request, *args, **kwargs):
        """
        Serves the page if the requested full path matches `self.canonical_full_path`, otherwise redirects (permanently) to the canonical full path.

        :param request: The current request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The rendered page, or a permanent redirect to the canonical full path.
        """
        if (request.get_full_path() == self.canonical_full_path):
            return super().get(request=request, *args, **kwargs)
        else:
            return redirect(to=self.canonical_full_path, permanent=True)

    class Meta:
        abstract = True


class StaticMainPageBaseView(StaticBaseView):
    """
    A base view for the main page, with canonical full path "/".
    """
    canonical_full_path = "/"

    class Meta:
        abstract = True


class StaticAboutBaseView(StaticBaseView):
    """
    A base view for the about page, with canonical full path "/about/".
    """
    canonical_full_path = "/about/"

    class Meta:
        abstract = True


class StaticPrivacyPolicyBaseView(StaticBaseView):
    """
    A base view for the privacy policy page, with canonical full path "/privacy/".
    """
    canonical_full_path = "/privacy/"

    class Meta:
        abstract = True


class StaticTermsOfServiceBaseView(StaticBaseView):
    """
    A base view for the terms of service page, with canonical full path "/terms/".
    """
    canonical_full_path = "/terms/"

    class Meta:
        abstract = True


class StaticContactUsBaseView(StaticBaseView):
    """
    A base view for the contact us page, with canonical full path "/contact/".
    """
    canonical_full_path = "/contact/"

    class Meta:
        abstract = True


class FormValidMessageMixin(object):
    """
    A mixin for form views which shows a success message after a valid form submission.

    Attributes:
        form_valid_message (str): The default success message to show.

    Methods:
        get_form_valid_message: Returns the success message to show for the given form.
        form_valid: Shows the success message and returns the parent's form_valid response.
    """
    form_valid_message = _('Changes saved.')

    def get_form_valid_message(self, form):
        """
        Returns the success message to show for the given form.

        :param form: The submitted, valid form.
        :return: The success message.
        :rtype: str
        """
        return self.form_valid_message

    def form_valid(self, form):
        """
        Shows the success message and returns the parent's form_valid response.

        :param form: The submitted, valid form.
        :return: The HTTP response from the parent's form_valid method.
        """
        response = super().form_valid(form=form)
        messages.success(request=self.request, message=self.get_form_valid_message(form=form))
        return response


class PaginationMixin(object):
    """
    A mixin for views which paginates a list of objects.

    Methods:
        redirect_on_exception: Returns the response to use when the requested page is invalid. Must be implemented in subclasses.
        dispatch: Paginates `self.get_object_list()` according to the requested page number before dispatching the request.
        get_context_data: Adds pagination data to the template context.
    """

    def redirect_on_exception(self):
        """
        Returns the response to use when the requested page number is invalid or out of range.

        :raises NotImplementedError: Always, unless overridden in a subclass.
        """
        raise NotImplementedError("This method is not implemented in this mixin.")

    def dispatch(self, request, *args, **kwargs):
        """
        Paginates `self.get_object_list()` according to the requested page number, storing the paginator and page on `self`, before dispatching the request.

        :param request: The current request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The response from the parent's dispatch method, or the result of `self.redirect_on_exception()` if the page number is invalid.
        """
        object_list = self.get_object_list()
        page_number = self.request.GET.get('page', 1)
        paginator = Paginator(object_list, self.page_size)
        try:
            page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            return self.redirect_on_exception()
        self.paginator = paginator
        self.page = page
        return super().dispatch(request=request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Adds pagination data (the paginator, the current page and whether there are other pages) to the template context.

        :param kwargs: Additional keyword arguments.
        :return: The context data, including pagination data.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'paginator': self.paginator,
            'page_obj': self.page,
            'is_paginated': self.page.has_other_pages(),
        })
        return cd


