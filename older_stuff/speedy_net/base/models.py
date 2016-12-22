# import json
import re
from datetime import (timedelta, date)
from django.db import models
# from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
# from django.dispatch import receiver
# from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from friendship.models import (Friend, FriendshipRequest)
from base import util
# from base import email_util


# User fields privacy settings
USER_PRIVATE_FIELD = 1
USER_FRIENDS_FIELD = 2
USER_PUBLIC_FIELD = 3
DEFAULT_USER_FIELD_PRIVACY = {
    'first_name': USER_PRIVATE_FIELD,
    'last_name': USER_PRIVATE_FIELD,
    'gender': USER_PRIVATE_FIELD,
    'diet': USER_PRIVATE_FIELD,
    'email': USER_PRIVATE_FIELD,
    'date_of_birth': USER_PRIVATE_FIELD
}

USER_MODEL_FIELDS = ['first_name', 'last_name']


SLUG_404 = '404'
USERNAME_NONE = 'none'


identity_id_validator = validators.RegexValidator(regex=r'[0-9]', message="id contains illegal characters")
username_validator = validators.RegexValidator(regex=r'[a-z0-9]', message="username contains illegal characters")


class Token(models.Model):
    class Meta:
        verbose_name_plural = "Tokens"

    token = models.CharField(max_length=128, unique=True)
    created = models.DateTimeField(auto_now_add=timezone.now())


class Identity(models.Model):
    """ Identity table to mash up all model IDs, usernames and slugs  """

    USER_MODEL         = 1
    PAGE_MODEL         = 2
    GROUP_MODEL        = 3
    CAUSE_MODEL        = 4
    EVENT_MODEL        = 5
    MODEL_TYPES = (
        (USER_MODEL, 'User'),
        (PAGE_MODEL, 'Page'),
        (GROUP_MODEL, 'Group'),
        (CAUSE_MODEL, 'Cause'),
        (EVENT_MODEL, 'Event'),
    )

    class Meta:
        verbose_name_plural = "Identities"

    id = models.CharField(max_length=15, validators=[identity_id_validator], primary_key=True, db_index=True)
    username = models.CharField(max_length=20, validators=[username_validator], unique=True)
    slug = models.SlugField(unique=True)
    model_type = models.SmallIntegerField(choices=MODEL_TYPES, null=True)

    def save(self, *args, **kwargs):
        # strip the slug from tail/head and 2+ dashes
        # TODO: fix
        self.slug = re.sub('[-]{1,}', '-', self.slug)
        self.slug = re.sub('^-', '', self.slug)
        self.slug = re.sub('-$', '', self.slug)
        if re.sub('[-]', '', self.slug) != self.username:
            raise ValidationError('slug does not parse to username.')
        self.id = Identity.get_id()
        super(Identity, self).save(*args, **kwargs)


    @classmethod
    def get_id(cls):
        """ generate new id until unique found """
        newid = util.generate_id()
        while (cls.objects.filter(id=newid).count() > 0):
            newid = util.generate_id()
        return newid

    def __str__(self):
        return '<Identity %s - %s (%s)>' % (self.username, self.id, self.slug)


class ManagedEntity(models.Model):
    """ abstract model for managed objects """
    class Meta:
        abstract = True

    # create custom manager for the managed models
    objects = models.Manager()

    identity = models.OneToOneField(Identity, null=True, blank=True)


class UserManager(BaseUserManager):
    def create_user(self, username, slug, date_of_birth, gender, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        # ~~~~ TODO: check that the username is valid; slug is valid etc.

        user = self.model(
            username=username,
            slug=slug,
            date_of_birth=date_of_birth,
            gender=gender,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, slug, date_of_birth, gender, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            slug=slug,
            date_of_birth=date_of_birth,
            gender=gender,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, ManagedEntity):
    """ User """

    class Meta:
        pass

    DEFAULT_REG_DOB = date.today() - timedelta(365 * 100)
    DEFAULT_PIC = 'default_profile_pic.png'

    FEMALE = 1
    MALE   = 2
    OTHER  = 3
    GENDER_CHOICES = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
        (OTHER, 'Other'),
    )

    # user diet choices
    UNKNOWN   = 0
    VEGAN      = 1
    VEGETARIAN = 2
    CARNIST    = 3
    DIET_CHOICES = (
        (UNKNOWN, 'Please select...'),
        (VEGAN, 'Vegan'),
        (VEGETARIAN, 'Vegeterian'),
        (CARNIST, 'Carnist')
    )

    date_of_birth = models.DateField()
    gender = models.SmallIntegerField(choices=GENDER_CHOICES)
    email = models.EmailField(
            verbose_name='email address',
            max_length=255,
            unique=True,
    )
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    diet = models.SmallIntegerField(choices=DIET_CHOICES, default=UNKNOWN)
    profile_picture = models.ImageField(upload_to='user_pictures/', blank=True, default=DEFAULT_PIC)
    password_reset_token = models.ForeignKey(Token, null=True, blank=True, related_name='password_reset_user', on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["date_of_birth", "gender", "email"]

    # json with the field privacy attributes
    field_privacy = JSONField(default=DEFAULT_USER_FIELD_PRIVACY)

    def get_age_as_delta(self):
        """ helper to get age. """
        return timezone.now() - self.date_of_birth

    def send_friend_request(self, user):
        """ request friendship helper """
        new_friendship = Friend.objects.add_friend(self.user, user.user)

    def get_allowed_fields_for_user(self, user):
        """ get user fields with privacy filter """
        acl = self.field_privacy
        is_friend = user in Friend.objects.friends(self.user)

        def access_filter(key):
            """ return fields allowed to see """
            permissions = [USER_PUBLIC_FIELD]
            if is_friend:
                permissions.append(USER_FRIENDS_FIELD)
            return acl[key] in permissions

        return filter(access_filter, acl.keys())

    def __str__(self):
        if self.identity:
            return "<User {}>".format(self.identity.username)
        else:
            return "<User - not active"


class UserEmailAddress(models.Model):
    """ user email address that sends verification email
        and may be used to login
    """
    class Meta:
        verbose_name_plural = "Email addresses"

    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)
    token = models.ForeignKey(Token, null=True, blank=True)
    user = models.ForeignKey(User)

    def __str__(self):
        return "<Email {}>".format(self.email)


class Page(ManagedEntity):
    name = models.CharField(max_length=128)

    def __str__(self):
        return "<Page {}>".format(self.name)


class Group(ManagedEntity):
    name = models.CharField(max_length=128)

    def __str__(self):
        return "<Group {}>".format(self.name)


class Cause(ManagedEntity):
    name = models.CharField(max_length=128)

    def __str__(self):
        return "<Cause {}>".format(self.name)


@python_2_unicode_compatible
class UserMessage(models.Model):
    """ User to user messages. """

    sent_to = models.ForeignKey(User, related_name='received_messages')
    sent_from = models.ForeignKey(User, related_name='sent_messages')
    content = models.TextField(max_length=500)
    created = models.DateTimeField(auto_now_add=timezone.now())
    opened = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False) # for deletion

    def __str__(self):
        return 'message to %s from %s' % (self.sent_to.identity.username, self.sent_from.identity.username)


