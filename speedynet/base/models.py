import json
import re
from datetime import timedelta, datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from friendship.models import Friend, FriendshipRequest
from registration.signals import user_registered


# User profile fields privacy settings
USER_PRIVATE_FIELD = 1
DEFAULT_USER_FIELD_PRIVACY = json.dumps({
    'first_name': USER_PRIVATE_FIELD,
    'last_name': USER_PRIVATE_FIELD,
    'gender': USER_PRIVATE_FIELD,
    'diet': USER_PRIVATE_FIELD,
    'email': USER_PRIVATE_FIELD,
    'date_of_birth': USER_PRIVATE_FIELD
})

USER_MODEL_FIELDS = ['first_name', 'last_name']


# Friendships are handled by `django-friendship` library
# https://github.com/revsys/django-friendship/

class UserProfile(models.Model):
    """ User extension model """
    PRIVATE = 1
    PUBLIC = 2
    FRIENDS_ONLY = 3
    FIELD_PRIVACY = (
        (PRIVATE, 'Private'),
        (PUBLIC, 'Public'),
        (FRIENDS_ONLY, 'Friends Only')
    )

    FEMALE = 1
    MALE = 2
    OTHER = 3
    GENDER_CHOICES = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
        (OTHER, 'Other'),
    )

    # user diet choices
    VEGAN = 1
    VEGETERIAN = 2
    CARNIST = 3
    DIET_CHOICES = (
        (VEGAN, 'Vegan'),
        (VEGETERIAN, 'Vegeterian'),
        (CARNIST, 'Carnist'),
    )

    FIRST = 1
    SECOND = 2
    THIRD = 3
    SECURITY_QUESTIONS = (
        (FIRST, 'School name'),
        (SECOND, 'Maiden name'),
        (THIRD, 'Dog name'),
    )


    user = models.OneToOneField(User)
    date_of_birth = models.DateTimeField(default=None)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=None)
    diet = models.SmallIntegerField(choices=DIET_CHOICES, default=None)
    profile_picture = models.ImageField(upload_to='user_pictures/', blank=True, default='default_profile_pic.png')
    security_question = models.SmallIntegerField(choices=SECURITY_QUESTIONS, default=FIRST)
    security_answer = models.CharField(max_length=128, blank=True, default='')

    # json with the field privacy attributes
    field_privacy = models.TextField(max_length=500, default=DEFAULT_USER_FIELD_PRIVACY)

    def get_age_as_delta(self):
        """ helper to get age. """
        return timezone.now() - self.date_of_birth

    def get_slug(self):
        """ helper to get user url slug """
        return re.sub(r'[\.\-_]', '', self.user.username).lower()

    def send_friend_request(self, user):
        """ request friendhip helper """
        new_friendship = Friend.objects.add_friend(self.user, user.user)

    def __unicode__(self):
        """ default representation of an object """
        return '%s - %s %s' % (self.user.username, self.user.first_name, self.user.last_name)

    def get_fields_for_user(self, user):
        """ get user fields with privacy filter """
        ret = {}
        acl = json.loads(self.field_privacy)
        if user in Friend.objects.friends(self.user):
            # show friend allowed fields
            for field in acl.keys():
                if acl[field] == UserProfile.FRIENDS_ONLY or acl[field] == UserProfile.PUBLIC:
                    if field in USER_MODEL_FIELDS:
                        ret[field] = getattr(self.user, field)
                    else:
                        ret[field] = getattr(self, field)
        else:
            # show public fields
            for field in acl.keys():
                if acl[field] == UserProfile.PUBLIC:
                    if field in USER_MODEL_FIELDS:
                        ret[field] = getattr(self.user, field)
                    else:
                        ret[field] = getattr(self, field)
        return ret



class UserMessage(models.Model):
    """ User to user messages. """
    sent_to = models.ForeignKey(User, related_name='received_messages')
    sent_from = models.ForeignKey(User, related_name='sent_messages')
    content = models.TextField(max_length=500)
    created = models.DateTimeField(auto_now_add=timezone.now())
    opened = models.DateTimeField(blank=True, null=True)
    hidden = models.BooleanField(default=False) # for deletion

    def __unicode__(self):
        return 'message to %s from %s' % (self.sent_to.username, self.sent_from.username)
