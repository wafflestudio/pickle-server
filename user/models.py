from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.upload import convert_filename


def upload_to_func(instance, filename):
    prefix = "uploads/user_images/"
    return prefix + convert_filename(filename)


class User(AbstractUser):
    first_name = None
    last_name = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    email = models.EmailField(_("email address"), unique=True)
    image = models.ImageField(upload_to=upload_to_func, blank=True, null=True)
