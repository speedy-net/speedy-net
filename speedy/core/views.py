from django.http import HttpResponseRedirect
from django.views import generic


class MultiUpdateView(generic.TemplateView):
    initial = {}
    form_classes = None
    success_url = None

    def get_success_url(self):
        return self.success_url

    def get_form_classes(self):
        return self.form_classes

    def get_initial(self, prefix):
        handler = 'get_initial_%s' % prefix
        if hasattr(self, handler):
            return getattr(self, handler)()
        return self.initial.get(prefix, {})

    def get_object(self, prefix):
        handler = 'get_object_%s' % prefix
        if hasattr(self, handler):
            return getattr(self, handler)()
        return None

    def get_form_kwargs(self, prefix):
        kwargs = {
            'initial': self.get_initial(prefix),
            'prefix': prefix,
        }
        instance = self.get_object(prefix)
        if instance is not None:
            kwargs['instance'] = instance
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        handler = 'get_form_kwargs_%s' % prefix
        if hasattr(self, handler):
            kwargs.update(getattr(self, handler)())
        return kwargs

    def get_forms(self):
        form_classes = self.get_form_classes()
        forms = {}
        for prefix, form_class in form_classes.items():
            forms[prefix] = form_class(**self.get_form_kwargs(prefix))
        return forms

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        for prefix, form in self.get_forms().items():
            cd[prefix + '_form'] = form
        return cd

    def form_valid(self, form, prefix):
        handler = 'form_valid_%s' % prefix
        if hasattr(self, handler):
            getattr(self, handler)(form)
        elif hasattr(form, 'save'):
            form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, prefix):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        prefix = self.request.POST['_form']
        form = forms[prefix]
        if form.is_valid():
            return self.form_valid(form, prefix)
        else:
            return self.form_invalid(form, prefix)
