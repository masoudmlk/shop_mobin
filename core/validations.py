from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator,\
    MaxLengthValidator, MinValueValidator, MaxValueValidator


class CoreValidation:

    @staticmethod
    def phone_regx_validator(regx=None, message=None, code=None):
        if regx is None:
            regx = '^09(1[0-9]|3[1-9]|2[1-9])[0-9]{3}[0-9]{4}$'

        if message is None:
            message = 'phone must be numeric with exact 11 digits'

        if message is None:
            code = 'invalid_phone'

        return RegexValidator(
            regex=regx,
            message=message,
            code=code)

    @staticmethod
    def username_regx_validator(regx=None, message=None, code=None):
        if regx is None:
            regx = '^(?=.{8,30}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'

        if message is None:
            message = 'username must be between 8 and 30 characters. It should be start with _ or contain _. or ._'

        if message is None:
            code = 'invalid_username'

        return RegexValidator(
            regex=regx,
            message=message,
            code=code)

    @staticmethod
    def email_validator():
        return [EmailValidator]

    @staticmethod
    def phone_validator():
        return [CoreValidation.phone_regx_validator(), MinLengthValidator(11), MaxLengthValidator(11)]

    @staticmethod
    def username_validator():
        return [CoreValidation.username_regx_validator(), MinLengthValidator(8), MaxLengthValidator(30)]

    @staticmethod
    def password_validator():
        return [MinLengthValidator(8)]


    @staticmethod
    def score_validator():
        return [MinValueValidator(1), MaxValueValidator(5)]