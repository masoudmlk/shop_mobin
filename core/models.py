from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from knox.auth import TokenAuthentication as BaseTokenAuthentication, AuthToken as BaseAuthToken
from core.utils import Client
from rest_framework import exceptions
from shop import settings
from uuid import uuid4
from django.core.validators import MinValueValidator
from core.validations import score_validator


class User(AbstractUser):
    phone = models.CharField(null=False, blank=False, unique=True, max_length=11)
    is_verify_phone = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/%Y/%m/%d/', blank=True, null=True)


class AuthToken(BaseAuthToken):
    user_agent = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.token_key


class TokenAuthentication(BaseTokenAuthentication):
    model = AuthToken

    def authenticate(self, request):
        if not Client.valid_user_agent(request):
            msg = _('Invalid user agent.')
            raise exceptions.PermissionDenied(msg)
        return super(TokenAuthentication, self).authenticate(request)


class Product(models.Model):
    TYPE_DEFAULT = "OTR"
    TYPE_CHOICES = [(TYPE_DEFAULT, "OTHER"), ("P", 'PHONE'), ("CAM", 'CAMERA'), ("PC", "PERSONAL COMPUTER"), ("DVD", "DVD"),
                    ("GME", "GAME"), ("PS4", "PS4")]

    name = models.CharField(max_length=255, null=False, blank=False)
    type = models.CharField(max_length=3, null=False, blank=False, choices=TYPE_CHOICES, default=TYPE_DEFAULT)
    brand = models.CharField(max_length=255, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductItem(models.Model):
    # todo it can be one to one relationship but I prefer to use one to many for future use
    STATUS_HIDDEN = "H"
    STATUS_SHOW = "S"
    STATUS_UNDER_REVIEW = "U"
    STATUS_SHOW_CHOICES = [(STATUS_SHOW, "SHOW"), (STATUS_HIDDEN, "HIDDEN"), (STATUS_UNDER_REVIEW, "UNDER REVIEW")]
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    quantity = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0)])
    status_show = models.CharField(max_length=1, default=STATUS_HIDDEN, choices=STATUS_SHOW_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name},  {self.quantity},"

    @classmethod
    def get_unique_key(cls, product_id):
        return f"product_item_{product_id}"
class Opinion(models.Model):
    STATUS_HIDDEN = "H"
    STATUS_SHOW = "S"
    STATUS_UNDER_REVIEW = "U"
    STATUS_SHOW_CHOICES = [(STATUS_SHOW, "SHOW"), (STATUS_HIDDEN, "HIDDEN"), (STATUS_UNDER_REVIEW, "UNDER REVIEW")]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    status_show = models.CharField(max_length=1, default=STATUS_HIDDEN, choices=STATUS_SHOW_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        len_char = 10
        return self.description[0:len_char] if len(self.description) > len_char else self.description


class Score(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(validators=score_validator())
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['product', 'user']]

    def __str__(self):
        return f"{self.product_id} {self.user_id} {self.score}"


class Cart(models.Model):
    CURRENT_STATUS = "C"
    FINISHED_STATUS = "F"
    STATUS_CHOICES = [(CURRENT_STATUS, 'current'), (FINISHED_STATUS, 'Finished')]
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    status = models.CharField(max_length=1, null=False, blank=False, choices=STATUS_CHOICES, default=CURRENT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])


    def __str__(self):
        return f"{self.product.name} {self.quantity}"


class Shop(models.Model):
    track = models.UUIDField(unique=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.track}"

