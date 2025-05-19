from .models import User, Uni, Hub, Ride, Student, Location
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        # exclude = ('PUBLIC_Key', 'SECRET_Key')  # specify the field to exclude
        extra_kwargs = {
            'password': {'write_only': True,'required': False},
            'is_staff': {'write_only': True},
            'is_admin': {'write_only': True},
            'is_superuser': {'write_only': True},
            'groups': {'write_only': True},
            'user_permissions': {'write_only': True},
        }

# Create a proper login serializer
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    # This serializer is only for validation, not for creating users
    class Meta:
        fields = ('email', 'password')

class UniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uni
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

        depth = 1     

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

        depth = 1  

class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = "__all__"

        depth = 1


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = "__all__"



class UserRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

class UserLoginRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

class StudentRequestSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=255)
    uni = serializers.CharField(max_length=255)
    school_id = serializers.CharField(max_length=255)
    full_name = serializers.CharField(max_length=255)


class HubRequestSerializer(serializers.Serializer):
    uni = serializers.CharField(max_length=255)
    driver_fullname = serializers.CharField(max_length=255)
    driver_gender = serializers.CharField(max_length=255)

class LocationRequestSerializer(serializers.Serializer):
    uni = serializers.CharField(max_length=255)
    area_name = serializers.CharField(max_length=255)

class UniversityRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=225)
    addresss = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)


class RequestRideRequestSerializer(serializers.Serializer):
    where_from = serializers.CharField(max_length=255)
    where_to = serializers.CharField(max_length=255)