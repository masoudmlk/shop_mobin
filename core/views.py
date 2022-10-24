from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models.aggregates import Avg
from django.db.models import F
from django.db.models import Q


from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from core.serializers import UserRegisterSerializer, UserSerializer, UserLoginSerializer, UserChangePassSerializer
from core.serializers import ProductSerializer, OpinionSerializer, ScoreSerializer, CartItemSerializer, \
    removeCartItemSerializer, TrackSerializer, CartSerializer
from core.models import AuthToken, User
from core.models import Product, ProductItem, Score, Opinion, Cart, CartItem, Shop
from core.handler import create_token, logout, create_update_score


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        del serializer.validated_data['password_repeat']
        with transaction.atomic():
            user = User.objects.create_user(**serializer.validated_data)
            token, token_key = create_token(user, request)
            return Response({'token_key': token_key}, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get data from serializer
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = get_object_or_404(User, username=username)
        isLogin = user.check_password(password)

        if isLogin:
            token, token_key = create_token(user, request)
            return Response({'token_key': token_key}, status=status.HTTP_200_OK)

        return Response({"Error": "there are not any user with this username and password"},
                        status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserChangePassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data.get('old_password')
        password = serializer.validated_data.get('password')

        current_user = request.user
        if current_user.check_password(old_password):

            with transaction.atomic():
                current_user.set_password(password)
                current_user.save()

                logout(request)

                AuthToken.objects.filter(user=current_user).delete()
                token, token_key = create_token(current_user, request)

                return Response({'token_key': token_key}, status=status.HTTP_200_OK)

        return Response({"Error": "password is not correct"}, status=status.HTTP_401_UNAUTHORIZED)


class UserInfo(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProductView(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    serializer_class = ProductSerializer
    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # use for search pattern None use for exact search
    __VALID_FILTER_PARAMS = {"name": 'icontains', 'brand': 'icontains', 'type': None}

    def get_queryset(self):
        products = Product.objects.select_related("productitem").filter(productitem__status_show=ProductItem.STATUS_SHOW)
        filter_params = self._get_valid_filter_options()
        if filter_params is not None:
            products = products.filter(**filter_params)
        return products

    def _get_valid_filter_options(self):
        dict_query_params = {}
        for param, value in self.request.query_params.items():

            if str(value).strip() == "" or value is None:
                continue

            if param in self.__VALID_FILTER_PARAMS.keys():
                if self.__VALID_FILTER_PARAMS[param] is None:
                    dict_query_params[param] = value
                else:
                    dict_query_params[f'{param}__{self.__VALID_FILTER_PARAMS[param]}'] = value

        result = dict_query_params if len(dict_query_params) > 0 else None
        return result


class OpinionView(GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = OpinionSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        product_exists = ProductItem.objects.filter(product_id=product_id, status_show=ProductItem.STATUS_SHOW).exists()
        if product_exists:
            queryset = Opinion.objects.filter(product_id=product_id, status_show=Opinion.STATUS_SHOW)
        else:
            queryset = []
        return queryset

    def add(self, request, product_id: str):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        productItemInfo = {"product_id": product_id, "status_show": ProductItem.STATUS_SHOW}
        get_object_or_404(ProductItem, **productItemInfo)

        description = serializer.validated_data.get("description")
        opinion = Opinion.objects.create(user_id=request.user.pk, product_id=product_id, description=description)

        return Response(self.get_serializer(opinion).data, status=status.HTTP_201_CREATED)


class ScoreView(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ScoreSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        product_exists = ProductItem.objects.filter(product_id=product_id, status_show=ProductItem.STATUS_SHOW).exists()
        if product_exists:
            queryset = Score.objects.filter(product_id=product_id)
        else:
            queryset = []

        return queryset

    def add(self, request, product_id: int):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        productItemInfo = {"product_id": product_id, "status_show": ProductItem.STATUS_SHOW}
        get_object_or_404(ProductItem, **productItemInfo)

        score = serializer.validated_data.get("score")
        score_object = create_update_score(request.user.pk, product_id, score)

        return Response(self.get_serializer(score_object).data, status=status.HTTP_201_CREATED)

    def avg_score(self, request, product_id: int):
        productItemInfo = {"product_id": product_id, "status_show": ProductItem.STATUS_SHOW}
        get_object_or_404(ProductItem, **productItemInfo)

        qs = Score.objects.filter(product_id=product_id)

        if qs is not None and len(qs) > 0:
            score = qs.aggregate(avg_score=Avg('score'))
            return Response(score, status=status.HTTP_200_OK)
        return Response({"avg_score": 0}, status=status.HTTP_200_OK)


class CartAction(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def add_list(self, request):
        serializer = CartItemSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        # step one get or create cart
        cart = Cart.objects.filter(status=Cart.CURRENT_STATUS, user_id=request.user.pk).first()
        if cart is None:
            cart = Cart.objects.create(user_id=request.user.pk)

        # step two create cart Items
        if len(serializer.validated_data) > 0:
            response_list = []
            for item in serializer.validated_data:
                with cache.lock(ProductItem.get_unique_key(item.get('id'))):

                    with transaction.atomic():
                        productItem = ProductItem.objects.filter(product_id=item.get('id'),
                                                                 quantity__gte=item.get('quantity'),
                                                                 status_show=ProductItem.STATUS_SHOW).first()

                        # check if productItem exists we can order items on the other hand we can not buy items
                        if productItem is not None:
                            cartItem = CartItem.objects.filter(product_id=item.get("id"), cart_id=cart.pk).first()

                            # create or update cart items
                            if cartItem is None:
                                CartItem.objects.create(product_id=item.get("id"), cart_id=cart.pk,
                                                        quantity=item.get('quantity'))
                            else:
                                cartItem.quantity += item.get("quantity")
                                cartItem.save()

                            productItem.quantity -= item.get("quantity")
                            productItem.save()

                            response_list.append({'id': item.get('id'), "success": True,
                                                  "message": "The product are added to the cart"})
                        else:
                            response_list.append({'id': item.get('id'), "success": False,
                                                  "message": "The product does not exists or quantity lower than your requirement"})

            return Response(response_list, status=status.HTTP_200_OK)
        else:
            return Response({'list': "This list is required"}, status=status.HTTP_400_BAD_REQUEST)

    def remove_list(self, request):
        stringAll = "all"
        input_ids = request.data.get("ids")
        cart = Cart.objects.filter(status=Cart.CURRENT_STATUS).first()

        if cart is not None:
            if isinstance(input_ids, str) and str.lower(input_ids) == stringAll:
                ids_tuple = CartItem.objects.filter(cart_id=cart.pk).values_list("product_id")
                ids = [id_item[0] for id_item in ids_tuple]
            else:
                serializer = removeCartItemSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                ids = serializer.validated_data.get("ids")

            list_report = []

            for product_id in ids:
                with transaction.atomic():
                    cartItem = CartItem.objects.filter(cart_id=cart.pk, product_id=product_id).first()
                    if cartItem is not None:
                        ProductItem.objects.filter(product_id=product_id).update(quantity=F('quantity') + cartItem.quantity)
                        cartItem.delete()
                        list_report.append({'product_id': product_id, 'status_remove': 'success'})
                    else:
                        list_report.append({'product_id': product_id, 'status_remove': 'failed'})

            return Response(list_report, status=status.HTTP_200_OK)

        else:
            Cart.objects.create(status=Cart.CURRENT_STATUS, user_id=request.user.pk)

        return Response({"detail": "something wrong"}, status=status.HTTP_404_NOT_FOUND)


class TrackViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = TrackSerializer
    lookup_field = 'track'
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Shop.objects.filter(user=self.request.user)


class ShopView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with transaction.atomic():
            # change status current cart
            cart = Cart.objects.filter(user_id=request.user.pk, status=Cart.CURRENT_STATUS).first()

            if cart is None:
                cart = Cart.objects.create(user_id=request.user.pk, status=Cart.CURRENT_STATUS)

            countItems = CartItem.objects.filter(cart=cart).count()

            if countItems > 0:
                cart.status = Cart.FINISHED_STATUS
                cart.save()
                # create a new cart
                Shop.objects.create(user_id=request.user.pk, cart=cart)

                return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

            return Response({"detail": "Your cart is empty"}, status=status.HTTP_409_CONFLICT)
