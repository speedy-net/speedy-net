from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, redirect
from django.views.generic import View
from django.contrib.auth.decorators import login_required

from base.models import UserProfile

# Create your views here.
class ProfileView(View):
    """ Simple class based view for the profile page. """
    def get(self, request):
        if not request.user.is_authenticated() or not request.user.is_active:
            return redirect("/accounts/login/?next=/accounts/profile/")
        profile = UserProfile.objects.get(user=request.user)
        return render_to_response("base/user_profile.html", {
            'profile': profile
        })

    def post(self, request):
        if not request.user.is_authenticated() or not request.user.is_active:
            return redirect("/accounts/login/?next=/accounts/profile/")
        return redirect("user_profile")
