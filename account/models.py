import re

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import TimeStampedModel


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        if not password:
            raise ValueError('User must have a password')

        if re.fullmatch('^[a-z0-9.]+@[a-z0-9]+.[a-z]{2,}$', email.lower()) is None:
            raise ValueError('Invalid Email Address')

        if re.fullmatch('^[a-z0-9.@#$%^&*-+~!]{8,}$', password.lower()) is None:
            raise ValueError('Password Must Be At Least 8 Characters')

        user_obj = self.model(
            username=username,
            # Standardize lower caps on input entered
            email=self.normalize_email(email),
        )
        user_obj.active = is_active
        user_obj.admin = is_staff
        user_obj.superuser = is_admin
        user_obj.set_password(password)
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, email, username, password=None):
        user = self.create_user(email=email, username=username, password=password, is_staff=True)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email=email, username=username, password=password, is_staff=True, is_admin=True)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=100, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.admin

    @property
    def is_admin(self):
        return self.superuser


class Profile(TimeStampedModel):
    GENDER_CHOICES = [
        ("m", "Male"),
        ("f", "Female"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=50, blank=True)
    profile_picture = models.ImageField(upload_to="images/", blank=True)
    about = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    has_preference = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.user.username

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, *args, **kwargs):
        if created:
            Profile.objects.create(user=instance)


class Address(TimeStampedModel):
    user = models.ForeignKey(User, related_name="address", on_delete=models.CASCADE)
    country = CountryField(blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    street_address = models.CharField(max_length=250, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    # has_card = models.BooleanField(default=False)  # Move this
    # primary = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.user.username
