from django.core.validators import MinValueValidator

from rest_framework import serializers

from core.models import User, AuthToken
from core.validations import username_validator, password_validator, email_validator,\
    validate_password_and_repeat_password


class UserSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'image']


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, required=True,
                                     validators=username_validator())

    password = serializers.CharField(max_length=255, write_only=True, required=True,
                                     validators=password_validator())
    password_repeat = serializers.CharField(max_length=255, write_only=True, required=True,
                                            validators=password_validator())
    email = serializers.CharField(max_length=255, write_only=True, required=True,
                                  validators=email_validator())
    phone = serializers.CharField(max_length=11)
    first_name = serializers.CharField(max_length=255, allow_blank=True, allow_null=True, required=False)
    last_name = serializers.CharField(max_length=255, allow_blank=True, allow_null=True, required=False)
    image = serializers.ImageField(allow_null=True, required=False)

    def validate_phone(self, phone):
        existing = User.objects.filter(phone=phone).first()
        if existing:
            raise serializers.ValidationError(
                {'invalid phone': "Someone with that phone has already registered. Was it you?"})
        return phone

    def validate_username(self, username):
        existing = User.objects.filter(username=username).first()
        if existing:
            raise serializers.ValidationError(
                {'invalid username': "Someone with that username has already registered. Was it you?"})
        return username

    def validate(self, data):
        return validate_password_and_repeat_password(data)

    def save(self, **kwargs):
        key = "password_repeat"
        if self.validated_data.get(key):
            del self.validated_data[key]

        return super().save(**kwargs)


class TokenGeneralSerializer(serializers.Serializer):
    token_key = serializers.CharField(max_length=255, read_only=True)
    user_agent = serializers.CharField(max_length=255, read_only=True)
    created = serializers.DateTimeField(read_only=True)


class TokenSerializer(serializers.ModelSerializer):
    token_key = serializers.CharField(read_only=True)

    class Meta:
        model = AuthToken
        fields = ['token_key']


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['username', 'password']


class UserChangePassSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=255, required=True, )
    password = serializers.CharField(max_length=255, write_only=True, required=True, )
    password_repeat = serializers.CharField(max_length=255, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['old_password', 'password', 'password_repeat']

    def validate(self, data):
        return validate_password_and_repeat_password(data)

