import re

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (UserProfile, Club, ClubUser, UserMessage)


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'access', 'refresh']

    @classmethod
    def get_access(cls, obj):
        token = RefreshToken.for_user(obj)
        token['username'] = obj.username
        token['avatar'] = obj.userprofile.avatar
        token['about'] = obj.userprofile.about
        token['is_staff'] = obj.is_staff
        token['id'] = obj.id
        return str(token.access_token)

    @classmethod
    def get_refresh(cls, obj):
        token = RefreshToken.for_user(obj)
        return str(token)

    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be longer than 8 characters.")
        elif re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)", password) is None:
            raise serializers.ValidationError(
                "Password should at least contain a number, capital and small letter.")
        return password

    @classmethod
    def validate_email(cls, email):
        check_email = User.objects.filter(email=email)
        if check_email.exists():
            raise serializers.ValidationError("Email already exists.")
        return email

    @classmethod
    def validate_username(cls, username):
        check_username = User.objects.filter(username=username)
        if check_username.exists():
            raise serializers.ValidationError("Username already exists.")
        elif re.match(r"^([a-zA-Z\d]+[-_])*[a-zA-Z\d*]+$", username) is None:
            raise serializers.ValidationError(
                "username can't be of integers, have white spaces or symbols.")
        return username

    @classmethod
    def create(cls, validated_data):
        return User.objects.create_user(**validated_data)


class ContentObjectRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, Club):
            serializer = ClubSerializer(value)
        elif isinstance(value, UserProfile):
            serializer = UserProfileSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')
        return serializer.data


class UserProfileSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    @classmethod
    def get_messages(cls, obj):
        return MessageSerializer(obj.messages, many=True).data


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ("password",)

    @classmethod
    def get_profile(cls, obj):
        profile = obj.userprofile
        serializer = UserProfileSerializer(profile, many=False)
        return serializer.data


class LoginSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['avatar'] = user.userprofile.avatar
        token['is_staff'] = user.is_staff
        token['id'] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializer(self.user).data
        for k, v in serializer.items():
            data[k] = v
        return data


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8,
                                     required=True, write_only=True,
                                     style={'input_type': 'password'})
    verify_password = serializers.CharField(max_length=128, min_length=8,
                                            required=True, write_only=True,
                                            style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['password', 'verify_password']

    @classmethod
    def update(cls, instance, data):
        password = data.pop('password', None)
        verify_password = data.pop('verify_password', None)
        for (key, value) in data.items():
            setattr(instance, key, value)

        if password != verify_password:
            response = {'error': 'Password do not match, try again'}
            return Response(response, content_type='text/json', status=status.HTTP_400_BAD_REQUEST)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ClubSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    club_users = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = '__all__'
        read_only_fields = ('messages', 'owner', 'club_users',)
        # depth = 1

    @classmethod
    def get_messages(cls, obj):
        return MessageSerializer(obj.messages, many=True).data

    @classmethod
    def get_club_users(cls, obj):
        return UserProfileSerializer(obj.clubusers, many=True).data

    def create(self, validated_data):
        user = self.context['user']
        validated_data['owner'] = user
        club = Club.objects.create(**validated_data)
        ClubUser.objects.create(user=user.userprofile, club=club)
        return club


class ClubUserSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    club = ClubSerializer(read_only=True)

    class Meta:
        model = ClubUser
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        validated_data['club'] = self.context['club']
        club_user = ClubUser.objects.create(**validated_data)
        return club_user


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = UserMessage
        fields = '__all__'
        read_only_fields = ('content_type', 'object_id',)
