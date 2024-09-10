from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta




class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, telegram_username=None, telegram_profile_photo=None, password=None):
        if not phone_number:
            raise ValueError('The Phone Number field is required')
        user = self.model(
            phone_number=phone_number,
            telegram_username=telegram_username,
            telegram_profile_photo=telegram_profile_photo,
        )
        if password is None:
            password = str(uuid.uuid4())
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number=phone_number,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class RoleCodes:
    """ role codes for users """
    USER = 'user'
    ADMIN = 'admin'
    STAFF = 'xodim'
    DIRECTOR = 'direktor'

    CHOICES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
        (STAFF, 'Xodim'),
        (DIRECTOR, 'Direktor'),
    ]

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    telegram_username = models.CharField(max_length=150, blank=True, null=True)
    telegram_profile_photo = models.URLField(blank=True, null=True)
    telegram_id = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(choices=RoleCodes.CHOICES, max_length=100, default=RoleCodes.USER)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

    def save(self, *args, **kwargs):
        if self.role in [RoleCodes.ADMIN, RoleCodes.XODIM]:
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)

class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    def is_valid(self):
        now = timezone.now()
        print(now)
        return self.is_active and (now - self.created_at < timedelta(minutes=1))

    @classmethod
    def delete_inactive_codes(cls):
        cls.objects.filter(is_active=False).delete()