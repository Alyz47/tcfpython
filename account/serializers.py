from django.contrib.auth import authenticate
from django_countries.serializers import CountryFieldMixin
# from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions
# from drf_extra_fields.fields import Base64ImageField
from .exceptions import (
    AccountDisabledException,
    InvalidCredentialsException,
)

from .models import User, Profile, Address


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")

        user = None

        user = authenticate(email=email, password=password)

        if not user:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise AccountDisabledException()

        validated_data['user'] = user
        return validated_data

    def to_representation(self, instance):
        # Customize the response data here
        user = instance['user']
        print("user: ", user)
        return {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'token': user.auth_token.key,
            # Add more fields as needed
        }


class EditProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    profile_picture = serializers.ImageField(required=False)
    gender = serializers.ChoiceField(choices=Profile.GENDER_CHOICES)

    class Meta:
        model = Profile
        fields = ['username', 'profile_picture', 'gender']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        username = user_data.get('username')

        # Update Profile fields
        instance.gender = validated_data.get('gender', instance.gender)
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']

        # Update User fields
        if username:
            instance.user.username = username
            instance.user.save()

        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'gender', 'has_preference', 'profile_picture', 'about', 'birth_date']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()  # Include Profile Serializer here

    class Meta:
        model = User
        fields = "__all__"


class SellerSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile']


class ReadAddressSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.get_username", read_only=True)

    class Meta:
        model = Address
        fields = "__all__"


class WriteAddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Address
        fields = ['user', 'country', 'city', 'street_address', 'postal_code']

    def create(self, validated_data):
        address = Address.objects.create(**validated_data)
        return address

    def update(self, instance, validated_data):
        if Address.objects.filter(user=instance.user).exists():
            print("User already has an address!")
            instance.country = ''
            instance.city = ''
            instance.street_address = ''
            instance.postal_code = ''
            print("Current address data cleared!")
        return super().update(instance, validated_data)
