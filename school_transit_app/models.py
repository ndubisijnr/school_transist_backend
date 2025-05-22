from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
       
        if not email:
            raise ValueError('email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    # def get_by_natural_key(self, email):
    #     return self.get(email=email)
    

## student at a university
class User(AbstractBaseUser, PermissionsMixin):
    email = models.CharField(max_length=255, unique=True, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
    state = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return self.name

## student at a university
class Student(models.Model):
    uni_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    school_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255,blank=True, null=True)

    
    def __str__(self):
        return self.full_name

## student at a university
class Location(models.Model):
    uni = models.ForeignKey('Uni', on_delete=models.CASCADE,blank=True, null=True)
    area_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.area_name


## vehicle at the university
class Hub(models.Model):
    class SeaterChoices(models.TextChoices):
        ONE = 'one', 'one seater'
        TWO = 'two', 'two seater'

    class VehicleTypeChoices(models.TextChoices):
        motorcycle = 'motorcycle', 'motorcycle'
        tricylce = 'tricylce', 'tricylce'
        car = 'car', 'car'

       
    uni_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_availiable = models.BooleanField(default=True)
    driver_fullname = models.CharField(max_length=255,blank=True, null=True)
    driver_vehicle_type = models.CharField(max_length=255,choices=VehicleTypeChoices.choices,default=VehicleTypeChoices.motorcyle)
    driver_vehicle_name = models.CharField(max_length=255,blank=True, null=True)
    driver_vehicle_color = models.CharField(max_length=255,blank=True, null=True)
    driver_vehicle_capacity = models.CharField(max_length=255, choices=SeaterChoices.choices,default=SeaterChoices.ONE)
    driver_gender = models.CharField(max_length=255,blank=True, null=True)
    driver_photo = models.CharField(max_length=255,blank=True, null=True)
    driver_is_verified = models.BooleanField(default=False)
    location = models.CharField(max_length=255,blank=True, null=True)

    def __str__(self):
        return self.driver_fullname


## rides made by the student using the hub at the university
class Ride(models.Model):
    class StatusChoices(models.TextChoices):
        MADY = 'mady', 'ride requested'
        NUKE = 'nuke', 'ride is on the way'
        SPEEDY = 'speedy', 'ride in transit'
        ZEUS = 'zeus', 'ride complete'

    class SeaterChoices(models.TextChoices):
        ONE = 'one', 'one seater'
        TWO = 'two', 'two seater'
       

    where_from = models.CharField(max_length=255)
    where_to = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student = models.ManyToManyField('Student', blank=True)
    hub = models.ForeignKey('Hub', on_delete=models.CASCADE, blank=True, null=True)
    uni = models.ForeignKey('Uni', on_delete=models.CASCADE, blank=True, null=True)
    transit_fee = models.CharField(max_length=255,blank=True, null=True)
    transit_status = models.CharField(max_length=225,choices=StatusChoices.choices,default="NA")
    wait_time = models.CharField(max_length=255,blank=True, null=True)
    seater =  models.CharField(max_length=225,choices=SeaterChoices.choices,default=SeaterChoices.ONE)
    review_comment = models.CharField(max_length=255)


    def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
        return super().save(force_insert, force_update, using, update_fields)