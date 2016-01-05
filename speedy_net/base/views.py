import re
from datetime import timedelta
from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound)
from django.core.exceptions import (ValidationError, ObjectDoesNotExist)
from django.core.validators import validate_email
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import (authenticate, login, logout)
from django.conf import settings
from django.utils import timezone
from django.views.generic import View

from base.models import (Token, UserEmailAddress, UserProfile, Identity)
from base import util
from base import email_util


def check_token(token, message):
    if (token.created + timedelta(days=settings.EMAIL_TOKEN_EXPIRY) < timezone.now()):
        return HttpResponseBadRequest(message)

def redirect_user(request):
    if request.user.is_authenticated():
        return redirect('/home/')

def add_new_email(email_to_save, profile):
    """ create new mail address, save and send verification """
    token = Token(token=util.generate_token())
    token.save()

    email, created = UserEmailAddress.objects.get_or_create(email=email_to_save, token=token, profile=profile)
    if not created:
        # email exists
        return False
    email.save()
    return email, token

def get_email_url(view, token, host=None):
    if not host:
        host = settings.ALLOWED_HOSTS[0]
    return 'http://%s%s?token=%s' % (host, reverse('base:' + view), token.token)


SUCCESS_REG = 'successfully registered! please login and be sure to activate your account.'
PASS_RESET_SENT = 'password reset link sent to your email.'
EMAIL_ADDED = "new email added. verification link has been sent."
EXPIRED_SET_PASS = 'form expired, please reset your password again'
REG_EXPIRED = "Activation expired, please register again."
EMAIL_TOKEN_EXPIRED = "token expired, add email again."
REQ_MISSING = 'required fields are missing'
USER_OR_EMAIL_MISSING = 'username or email are missing.'
PASS_MISSING = 'password missing.'
USERNAME_TAKEN = "username is taken, please choose another one"
USERNAME_ERROR = 'username should be at least 3 characters long.'
EMAIL_NON_EXIST = "email does not exist."
USER_NON_EXIST = "user does not exist."
TOKEN_NOT_EXIST = "token does not exist."
REG_AGAIN = 'please register again.'
PASS_NOT_EQUAL = 'passwords not equal.'



class Login(View):
    def get(self, request):
        return render(request, 'base/login.html', {
            'reset_url': reverse('base:password_reset_confirm')
        })

    def post(self, request):
        data = request.POST
        validation_error = None
        if 'login' not in data:
            return HttpResponseBadRequest(USER_OR_EMAIL_MISSING)
        if 'password' not in data:
            return HttpResponseBadRequest(PASS_MISSING)


        password = data.get('password')
        if not password:
            messages.add_message(request, messages.ERROR, PASS_MISSING, extra_tags='error')
            validation_error = True
        username = data.get('login')
        if not username:
            messages.add_message(request, messages.ERROR, USERNAME_ERROR, extra_tags='error')
            validation_error = True

        if not re.match(r'^[a-zA-Z0-9\-_]{3,}$', username):
             # try to login with email
            try:
                 validate_email(username)
            except ValidationError as e:
                messages.add_message(request, messages.ERROR, str(e), extra_tags='error')
                validation_error = True
            user = authenticate(email=username, password=password)
        else:
            user = authenticate(username=username, password=password)

        if validation_error:
            return render(request, 'base/login.html', { 'error': True }, status=400)


        if user:
            if user.is_active:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return redirect('/')
            else:
                return render('activate_email_request.html')
        return render(request, 'base/login.html', { 'error': True })


class Register(View):
    def get(self, request):
        redirect_user(request)
        context = {
            'genders': UserProfile.GENDER_CHOICES
        }
        return render(request, 'base/register.html', context)

    def post(self, request):
        redirect_user(request)
        data = request.POST
        email, token, profile, error = (None, None, None, False)
        user, profile, identity, email = (None, None, None, None)
        if 'username' not in data or 'email1' not in data or \
            'email2' not in data or 'password' not in data or \
            'slug' not in data:
            messages.add_message(request, messages.ERROR, REQ_MISSING, extra_tags='error')
        if data.get('email1') != data.get('email2'):
            messages.add_message(request, messages.ERROR, REQ_MISSING, extra_tags='error')
            error = True

        try:
            validate_email(data.get('email1'))
        except ValidationError as e:
            messages.add_message(request, messages.ERROR, str(e), extra_tags='error')
            error = True

        if not re.match(r'[a-zA-Z0-9\-_\.]{3,}', data.get('username', None)):
            messages.add_message(request, messages.ERROR, USERNAME_ERROR, extra_tags='error')
            error = True

        if error:
            return render(request, 'base/register.html', status=400)

        if Identity.objects.filter(username=data.get('username')):
            # check identity does not exist
            messages.add_message(request, messages.ERROR, USERNAME_TAKEN, extra_tags='error')
            return render(request, 'base/register.html', status=400)
        user, created = User.objects.get_or_create(username=data.get('username'), is_active=False)
        if not created:
            messages.add_message(request, messages.ERROR, USERNAME_TAKEN, extra_tags='error')
            return render(request, 'base/register.html', status=400)


        # user and identity created, complete profile
        user.set_password(data.get('password'))
        user.is_active = False
        user.save()

        try:
            # create new identity and profile
            identity = Identity(
                username=data.get('username'),
                slug=data.get('slug'),
                model_type=Identity.USER_MODEL
            )
            identity.save()

            # TODO: fix this
            gender = data.get('gender') if data.get('gender', None) else UserProfile.OTHER
            diet = data.get('diet') if data.get('diet', None) else UserProfile.CARNIST
            date_of_birth = data.get('date_of_birth') if data.get('date_of_birth', None) else UserProfile.DEFAULT_REG_DOB

            profile = UserProfile(
                user=user,
                identity=identity,
                gender=gender,
                diet=diet,
                date_of_birth=date_of_birth
            )
            profile.save()

            # create new email for the profile, send activation mail
            email, token = add_new_email(data.get('email1'), profile)
            email_util.send_email_verification(email.email, get_email_url('activate_email', token, host=request.get_host()))
        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e), extra_tags='error')

            if user and user.id:
                user.delete()
            if identity and identity.id:
                identity.delete()
            if email and email.id:
                email.delete()
            if profile and profile.id:
                profile.delete()
            return render(request, 'base/register.html', status=400)

        if profile:
            messages.add_message(request, messages.INFO, SUCCESS_REG, extra_tags='success')
            return render(request, 'base/register_success.html')
        else:
            return render(request, 'base/register.html', status=400)


class AddEmail(View):
    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request):
        return render(request, 'base/add_email_address.html')

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request):
        data = request.POST
        email, token = (None, None)
        if 'email' not in data or data.get('email') in ['', None]:
            messages.add_message(request, messages.ERROR, REQ_MISSING, extra_tags='error')
            return render(request, 'base/add_email_address.html', status=400)

        try:
            validate_email(data.get('email'))
        except ValidationError as e:
            messages.add_message(request, messages.ERROR, str(e), extra_tags='error')
            return render(request, 'base/add_email_address.html', status=400)

        try:
            email, token = add_new_email(data.get('email'), request.user.userprofile)
            email_util.send_email_verification(email.email, get_email_url('activate_email', token, host=request.get_host()))
        except Exception as e:
            messages.add_message(request, messages.ERROR, str(e), extra_tags='error')
            return render(request, 'base/add_email_address.html', status=400)

        messages.add_message(request, messages.INFO, EMAIL_ADDED, extra_tags='success')
        return render(request, 'base/add_email_address.html')



class PasswordResetConfirm(View):
    def get(self, request):
        return render(request, 'base/password_reset_confirm.html')

    def post(self, request):
        data = request.POST
        if 'email' not in data:
            return HttpResponseBadRequest('email is missing.')

        try:
            validate_email(data.get('email'))
        except ValidationError as e:
            return HttpResponseBadRequest(str(e))
        try:
            email = UserEmailAddress.objects.get(email=data.get('email'))
        except ObjectDoesNotExist as e:
            return HttpResponseBadRequest(str(e))
        profile = email.profile
        token = Token(token=util.generate_token())
        token.save()
        profile.password_reset_token = token
        profile.save()

        url = 'http://%s%s?token=%s' % (request.get_host(), reverse('base:password_reset'), token.token)
        email_util.send_password_reset(email.email, url)
        messages.add_message(request, messages.INFO, PASS_RESET_SENT, extra_tags='success')
        return render(request, 'base/password_reset_confirm.html')


class PasswordReset(View):
    def get(self, request):
        data = request.GET
        if 'token' not in data:
            return HttpResponseBadRequest('token is missing.')
        try:
            token = Token.objects.get(token=data.get('token', None))
        except ObjectDoesNotExist as e:
            return HttpResponseBadRequest('token error.')
        if token.created + timedelta(days=settings.EMAIL_TOKEN_EXPIRY) < timezone.now():
            return HttpResponseBadRequest('token expired.')
        return render(request, 'base/password_reset.html', {
            'token': token.token
        })

    def post(self, request):
        data = request.POST
        user, profile, token = (None, None, None)

        # validate all fields are there and token is OK
        if 'password1' not in data or 'password2' not in data:
            messages.add_message(request, messages.ERROR, REQ_MISSING, extra_tags='error')
            return render(request, 'base/register.html', status=400)
        if 'token' not in data:
            return HttpResponseBadRequest('malformed request')
        if data.get('password1', None) != data.get('password2', None):
            messages.add_message(request, messages.ERROR, PASS_NOT_EQUAL, extra_tags='error')
            return render(request, 'base/register.html', status=400)


        # TODO: add password validation
        # try get profile and user from the token
        try:
            token = Token.objects.get(token=data.get('token', None))
            profile = UserProfile.objects.get(password_reset_token=token)
        except ObjectDoesNotExist as e:
            messages.add_message(request, messages.ERROR, EXPIRED_SET_PASS, extra_tags='error')
        if token:
            check_token(token, EXPIRED_SET_PASS)

        if not token or not profile:
            # show errors, redirect to login
            return redirect('base:login')

        user = profile.user
        user.set_password(data.get('password1'))
        user.save()
        # delete reset token, save
        profile.password_reset_token = None
        profile.save()
        token.delete()
        return redirect('base:login')


class BaseProfile(View):
    @method_decorator(login_required(login_url='/account/login/'))
    def get(self, request):
        # TODO: get user profile, display it, etc..
        profile = request.user.userprofile
        return render(request, 'base/user_profile.html', { 'profile': profile })

    @method_decorator(login_required(login_url='/account/login/'))
    def post(self, request):
        data = request.POST
        # TODO: profile change form
        return redirect(reverse('base:user_profile'))


@login_required(login_url='/account/login/')
def logout_view(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed('GET')
    if request.user:
        logout(request)
    return redirect('/')


def home(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed('GET')
    context = {
        'logged_in': request.user.is_authenticated(),
        'username': request.user.username
    }
    return render(request, 'base/home.html', context)


def activate_email(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed('GET')

    token, email = (None, None)
    if 'token' not in request.GET:
        return HttpResponseBadRequest(TOKEN_NOT_EXIST)

    # check token
    try:
        token = Token.objects.get(token=request.GET.get('token'))
    except ObjectDoesNotExist as e:
        return HttpResponseBadRequest(TOKEN_NOT_EXIST)
    check_token(token, EMAIL_TOKEN_EXPIRED)

    # check email
    try:
        email = UserEmailAddress.objects.get(token=token)
    except ObjectDoesNotExist as e:
        return HttpResponseBadRequest(EMAIL_NON_EXIST)

    profile = email.profile
    if not profile.user:
        return HttpResponseBadRequest(USER_NON_EXIST)

    # activate the email
    email.verified = True
    email.token = None
    email.save()
    token.delete()

    # first activation, login after activation
    if not profile.user.is_active:
        # get identity
        profile.user.is_active = True
        profile.user.save()
        # set backend app specifically here, so django would know which backend auth'ed the user.
        profile.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, profile.user)
        return redirect('/')

    return redirect('/')


@login_required(login_url='/account/login/')
def resolve_slug(request, slug):
    if request.method != 'GET':
        return HttpResponseNotAllowed('GET')
    try:
        identity = Identity.objects.get(username=re.sub(r'[\-_\.]', '', slug))
    except ObjectDoesNotExist as e:
        return HttpResponseNotFound()

    if slug != identity.slug:
        redirect(reverse('resolve_slug', kwargs={ 'slug': identity.slug }))

    profile = identity.userprofile
    context = { 'profile': profile }
    return render(request, 'base/user_profile.html', context)
