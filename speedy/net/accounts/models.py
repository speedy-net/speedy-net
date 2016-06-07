from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from speedy.core.models import TimeStampedModel
from speedy.net.accounts.utils import generate_id
from speedy.net.accounts.validators import identity_id_validator

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


class Entity(TimeStampedModel):

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entity')

    id = models.CharField(max_length=15, validators=[identity_id_validator], primary_key=True, db_index=True,
                          unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_id()
            while Entity.objects.filter(id=self.id).exists():
                self.id = generate_id()
        if not self.slug:
            self.slug = self.id
        return super().save(*args, **kwargs)

    def __str__(self):
        return '<Entity {}>'.format(self.id)


class User(Entity, AbstractBaseUser):
    GENDER_FEMALE = 1
    GENDER_MALE = 2
    GENDER_OTHER = 3
    GENDER_CHOICES = (
        (GENDER_MALE, _('Male')),
        (GENDER_FEMALE, _('Female')),
        (GENDER_OTHER, _('Other')),
    )
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    email = models.EmailField(verbose_name=_('email'), unique=True)
    first_name = models.CharField(verbose_name=_('first name'), max_length=75)
    last_name = models.CharField(verbose_name=_('last name'), max_length=75)
    date_of_birth = models.DateField(verbose_name=_('date of birth'), blank=True, null=True)
    gender = models.SmallIntegerField(verbose_name=_('gender'), choices=GENDER_CHOICES)
    profile_picture = models.ImageField(verbose_name=_('profile picture'), upload_to='accounts/user/profile_picture/', blank=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


    def __str__(self):
        return self.slug

