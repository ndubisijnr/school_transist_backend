from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, uni_id, email, password=None, **extra_fields):
        if not uni_id:
            raise ValueError('Uni_id field must be set')
        if not email:
            raise ValueError('email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, uni_id=uni_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, uni_id):
        return self.get(uni_id=uni_id)
    

## student at a university
class User(AbstractBaseUser, PermissionsMixin):
    uni_id = models.CharField(max_length=255, unique=True, blank=None, null=False, default='0')
    email = models.CharField(max_length=255, unique=True, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255,blank=True, null=True)
    uni = models.CharField(max_length=255,blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Add required fields

    objects = UserManager()  # Attach the custom manager here
    
    def __str__(self):
        return self.email

## university
class Uni(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=None, null=False, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length=255,blank=True, null=True)


## vehicle at the university
class Hub(models.Model):
    school_name_id = models.CharField(max_length=255, unique=True, blank=None, null=False, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255,blank=True, null=True)
    where_to = models.CharField(max_length=255,blank=True, null=True)
    driver = models.CharField(max_length=255,blank=True, null=True)

## rides made by the student using the hub at the university
class Ride(models.Model):
    where_from = models.CharField(max_length=255)
    where_to = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student_id = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True)
    transit_fee = models.CharField(max_length=255,blank=True, null=True)
    transit_status = models.CharField(max_length=255,blank=True, null=True)