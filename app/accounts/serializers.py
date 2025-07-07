from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    username = None


class CustomLoginSerializer(LoginSerializer):
    username = None


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name')
