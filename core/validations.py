from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator,\
    MaxLengthValidator, MinValueValidator, MaxValueValidator
from rest_framework import serializers

import django.contrib.auth.password_validation as validators
from django.core import exceptions


def phone_regx_validator(regx='^09(1[0-9]|3[1-9]|2[1-9])[0-9]{3}[0-9]{4}$',
                         message='phone must be numeric with exact 11 digits',
                         code='invalid_phone'):
    return RegexValidator(
        regex=regx,
        message=message,
        code=code)


def username_regx_validator(regx='^(?=.{8,30}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$',
                            message='username must be between 8 and 30 characters.'
                                    ' It should be start with _ or contain _. or ._',
                            code='invalid_username'):
    return RegexValidator(
        regex=regx,
        message=message,
        code=code)


def email_validator():
    return [EmailValidator]


def phone_validator():
    return [phone_regx_validator(), MinLengthValidator(11), MaxLengthValidator(11)]


def username_validator():
    return [username_regx_validator(), MinLengthValidator(8), MaxLengthValidator(30)]


def password_validator():
    return [MinLengthValidator(8)]


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
