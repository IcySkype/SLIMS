from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'teacher')

        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('teacher', 'Teacher'),
        ('lab_technician', 'Lab Technician'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='teacher')
    email = models.EmailField(unique=True)
    id_num = models.CharField(max_length=10, unique=True)

    USERNAME_FIELD = 'email'  # Use email as the login field
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"