from rules.contrib.views import LoginRequiredMixin


class OnlyAdminMixin(LoginRequiredMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if (not (request.user.is_authenticated)):
            return self.handle_no_permission()
        if (not ((request.user.is_superuser) and (request.user.is_staff))):
            return self.handle_no_permission()
        return super().dispatch(request=request, *args, **kwargs)


