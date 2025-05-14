from .models import User, Uni, Hub, Ride
from rest_framework import serializers

class StudentSerializer(serializers.ModelSerializer):
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

class UniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uni
        fields = "__all__"


class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = "__all__"


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = "__all__"