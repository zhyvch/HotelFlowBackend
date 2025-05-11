import uuid

from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from src.apps.common.models import PhoneNumberField
from src.apps.users.models import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name=_('Email'),
        unique=True,
    )
    phone_number = PhoneNumberField(
        verbose_name=_('Phone number'),
    )
    first_name = models.CharField(
        verbose_name=_('First name'),
        max_length=254,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name=_('Last name'),
        max_length=254,
        blank=True,
    )
    middle_name = models.CharField(
        verbose_name=_('Middle name or patronymic'),
        max_length=254,
        blank=True,
    )
    photo = models.ImageField(
        verbose_name=_('Photo'),
        upload_to='users/',
        null=True,
        blank=True,
    )
    bonus_balance = models.DecimalField(
        verbose_name=_('Bonus balance'),
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    is_employee = models.BooleanField(
        verbose_name=_('Is employee'),
        default=False,
    )
    date_joined = models.DateTimeField(
        verbose_name=_('Date joined'),
        auto_now=True,
    )
    is_active = models.BooleanField(
        verbose_name=_('Is active'),
        default=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_('Is staff'),
        default=False,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def email_username(self):
        return self.email[:self.email.index('@')]

