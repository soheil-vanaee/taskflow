from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    class Role(models.TextChoices):
        OWNER = 'owner', _('Owner')
        MEMBER = 'member', _('Member')

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_member(self):
        return self.role == self.Role.MEMBER
