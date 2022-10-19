from django.core.validators import RegexValidator, EmailValidator, MinValueValidator, MaxLengthValidator, \
    MinLengthValidator, MaxValueValidator
from django.core import exceptions
import django.contrib.auth.password_validation as validators

from rest_framework import serializers

from core.models import User
from core.validations import CoreValidation
from core.models import AuthToken, Product, ProductItem, Opinion, Score, Cart, CartItem, Shop


def validate_password_and_repeat_password(data):
    if data.get('password') != data.get('password_repeat'):
        raise serializers.ValidationError({"dismatch password": "password and password repeat are not match"})

    if data.get('old_password') is not None and data.get('old_password') == data.get('password'):
        raise serializers.ValidationError({"Error": "password password should not same as old password"})

    # get the password from the data
    password = data.get('password')
    errors = dict()
    try:
        # validate the password and catch the exception
        validators.validate_password(password=password)
    # the exception raised here is different than serializers.ValidationError
    except exceptions.ValidationError as e:
        errors['password'] = list(e.messages)
    if errors:
        raise serializers.ValidationError(errors)
    return data


class UserSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone', 'image']


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, required=True,
                                     validators=CoreValidation.username_validator())

    password = serializers.CharField(max_length=255, write_only=True, required=True,
                                     validators=CoreValidation.password_validator())
    password_repeat = serializers.CharField(max_length=255, write_only=True, required=True,
                                            validators=CoreValidation.password_validator())
    email = serializers.CharField(max_length=255, write_only=True, required=True,
                                  validators=CoreValidation.email_validator())
    phone = serializers.CharField(max_length=11)
    first_name = serializers.CharField(max_length=255, allow_blank=True, allow_null=True, required=False)
    last_name = serializers.CharField(max_length=255, allow_blank=True, allow_null=True, required=False)
    image = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_repeat', 'first_name', 'last_name', 'phone', 'image']

    def validate_phone(self, phone):
        existing = User.objects.filter(phone=phone).first()
        if existing:
            raise serializers.ValidationError(
                {'invalid phone': "Someone with that phone has already registered. Was it you?"})
        return phone

    def validate_username(self, username):
        # username = str(username)
        # if len(username) < 4:
        #     raise serializers.ValidationError(
        #         {'invalid username': "username is to small"})
        #
        # if username.isnumeric():
        #     raise serializers.ValidationError(
        #         {'invalid username': "username can not be a number"})

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


class OtpValidateSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=255, write_only=True, required=True)


class UserChangePassSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=255, required=True, )
    password = serializers.CharField(max_length=255, write_only=True, required=True, )
    password_repeat = serializers.CharField(max_length=255, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['old_password', 'password', 'password_repeat']

    def validate(self, data):
        return validate_password_and_repeat_password(data)


class ProductSerializer(serializers.ModelSerializer):
    display_type = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'type', 'display_type', 'brand']


class OpinionSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Opinion
        fields = ['id', 'product_id', 'user_id', 'description', 'created_at']


class ScoreSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    score = serializers.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    class Meta:
        model = Opinion
        fields = ['id', 'product_id', 'user_id', 'score', 'created_at']


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, validators=[MinValueValidator(1)])

class removeCartItemSerializer(serializers.Serializer):
    ids = serializers.ListField(allow_null=False, allow_empty=False, min_length=1)


class CartItemWithProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    display_status = serializers.CharField(source='get_status_display', read_only=True)
    items = CartItemWithProductSerializer(many=True)
    user = UserSerializer()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'status', 'display_status', 'created_at']


class cartSerializer(serializers.ModelSerializer):
    items = CartItemWithProductSerializer()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'status', 'items',  'created_at']


class TrackSerializer(serializers.ModelSerializer):
    cart = CartSerializer()
    class Meta:
        model = Shop
        fields = ['track', 'cart', 'user', 'created_at']

