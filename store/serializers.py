from django.core.validators import MinValueValidator

from rest_framework import serializers

from store.models import Product, ProductItem, Opinion, Score, Cart, CartItem, Shop
from core.serializers import UserSerializer
from store.validations import score_validator


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
    score = serializers.IntegerField(validators=score_validator())

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

