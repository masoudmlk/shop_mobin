
from django.db import transaction


from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from core.serializers import UserRegisterSerializer, UserSerializer, UserLoginSerializer, UserChangePassSerializer

from django_filters.rest_framework import DjangoFilterBackend
from core.filter import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from core.serializers import ProductSerializer, OpinionSerializer, ScoreSerializer, CartItemSerializer, \
    removeCartItemSerializer, TrackSerializer, CartSerializer

from core.models import AuthToken, User
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from core.models import Product, ProductItem, Score, Opinion, Cart, CartItem, Shop
from django.db.models.aggregates import Avg
from django.db.models import F
from core.handler import UserHandler


class RegisterViewSet(GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer

    # renderer_classes = BrowsableAPIRenderer

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        del serializer.validated_data['password_repeat']
        with transaction.atomic():
            user = User.objects.create_user(**serializer.validated_data)
            user.save()
            token, token_key = UserHandler.create_token(user, request)
            token.save()
            return Response({'token_key': token_key}, status=status.HTTP_200_OK)

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get data from serializer
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        # get user info and check conditions
        user = User.objects.filter(username=username).first()
        isLogin = False
        if user is not None and isinstance(user, User):
            isLogin = user.check_password(password)

        if isLogin:
            token, token_key = UserHandler.create_token(user, request)
            return Response({'token_key': token_key}, status=status.HTTP_200_OK)

        return Response({"Error": "there are not any user with this username and password"},
                        status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        UserHandler.logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangeUserInfo(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    def change_password(self, request):

        serializer = UserChangePassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data.get('old_password')
        password = serializer.validated_data.get('password')

        current_user = request.user
        if current_user.check_password(old_password):
            current_user.set_password(password)
            current_user.save()

            AuthToken.objects.filter(user=current_user).delete()
            UserHandler.logout(request)
            token, token_key = UserHandler.create_token(current_user, request)
            return Response({'token_key': token_key}, status=status.HTTP_200_OK)

        return Response({"Error": "password is not correct or user not login"}, status=status.HTTP_401_UNAUTHORIZED)

    def get_user_info(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def set_user_info(self, request):
        serializer = UserSerializer(request.user, request.data)
        serializer.is_valid(raise_exception=True)
        User.objects.filter(pk=request.user.pk).update(**serializer.validated_data)
        user = User.objects.get(pk=request.user.pk)
        outputSerializer = UserSerializer(user)
        return Response(outputSerializer.data, status=status.HTTP_200_OK)


class ProductView(GenericViewSet, ListModelMixin):
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.select_related("productitem").filter(productitem__status_show=ProductItem.STATUS_SHOW)

    def get(self, request, product_id: int):
        product = Product.objects.select_related("productitem").filter(productitem__status_show=ProductItem.STATUS_SHOW, id=product_id).first()
        if product is not None and isinstance(product, Product):
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': "Not found"}, status=status.HTTP_404_NOT_FOUND)


class OpinionView(GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = OpinionSerializer

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        print(product_id)
        product_exists = ProductItem.objects.filter(product_id=product_id, status_show=ProductItem.STATUS_SHOW).exists()
        if product_exists:
            queryset = Opinion.objects.filter(product_id=product_id, status_show=Opinion.STATUS_SHOW)
        else:
            queryset = []
        return queryset

    def add(self, request, product_id: str):
        if request.user.is_active:
            serializer = OpinionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product_exists = ProductItem.objects.filter(product_id=product_id, status_show=ProductItem.STATUS_SHOW).exists()
            if product_exists:
                description = serializer.validated_data.get("description")
                opinion = Opinion.objects.create(user_id=request.user.pk, product_id=product_id, description=description)
                opinion.save()
                return Response(OpinionSerializer(opinion).data, status=status.HTTP_201_CREATED)
            return Response({'detail': "the product are not exists"}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({'detail': "Your can not add new opinion"}, status=status.HTTP_401_UNAUTHORIZED)


class ScoreView(GenericViewSet, ListModelMixin):
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
        if request.user.is_active:
            product_exists = Product.objects.select_related('productitem').filter(id=product_id, productitem__status_show=ProductItem.STATUS_SHOW).exists()
            if product_exists:
                serializer = ScoreSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                score = serializer.validated_data.get("score")
                scoreObj = Score.objects.filter(user_id=request.user.pk, product_id=product_id).first()

                if scoreObj is not None and isinstance(scoreObj, Score):
                    scoreObj.score = score
                    scoreObj.save()
                else:
                    scoreObj = Score.objects.create(user_id=request.user.pk, product_id=product_id, score=score)

                return Response(ScoreSerializer(scoreObj).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "This product does not exists"}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({'detail': "Your  can not add score"}, status=status.HTTP_401_UNAUTHORIZED)

    def avg_score(self, request, product_id: int):
        productItem_exists = ProductItem.objects.filter(product_id=product_id, status_show=ProductItem.STATUS_SHOW).exists()
        if productItem_exists:
            qs = Score.objects.filter(product_id=product_id)

            if qs is not None and len(qs) > 0:
                score = qs.aggregate(avg_score=Avg('score'))
                return Response(score, status=status.HTTP_200_OK)
            return Response({"avg_score":  0}, status=status.HTTP_200_OK)

        return Response({"detail": "this product does not exists or deactive"}, status=status.HTTP_409_CONFLICT)


class AddListItemTOCart(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def add_list(self, request):
        if request.user.is_active:
            serializer = CartItemSerializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            # step one create cart
            cart = Cart.objects.filter(status=Cart.CURRENT_STATUS, user_id=request.user.pk).first()
            if cart is None:
                cart = Cart.objects.create(user_id=request.user.pk)
            # step two create cart Items
            if len(serializer.validated_data) > 0:
                response_list = []
                with transaction.atomic():
                    for item in serializer.validated_data:

                        productItem = ProductItem.objects.filter(product_id=item.get('id'),
                                                                 quantity__gte=item.get('quantity')).first()
                        # check if productItem exists we can order items on the other hand we can not buy items
                        if productItem is not None and isinstance(productItem, ProductItem):
                            cartItem = CartItem.objects.filter(product_id=item.get("id"), cart_id=cart.pk).first()
                            if cartItem is None:
                                cartItem = CartItem.objects.create(product_id=item.get("id"), cart_id=cart.pk,
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
        else:
            return Response({'detail': "Your can not add items to your Cart"}, status=status.HTTP_401_UNAUTHORIZED)

    def remove_list(self, request):
        stringAll = "all"
        input_ids = request.data.get("ids")
        cart = Cart.objects.filter(status=Cart.CURRENT_STATUS).first()

        if cart is not None and isinstance(cart, Cart):
            if isinstance(input_ids, str) and str.lower(input_ids) == stringAll:
                ids_tuple = CartItem.objects.filter(cart_id=cart.pk).values_list("product_id")
                ids = [id_item[0] for id_item in ids_tuple]
            else:
                serializer = removeCartItemSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                ids = serializer.validated_data.get("ids")

            list_report = []

            for product_id in ids:
                cartItem = CartItem.objects.filter(cart_id=cart.pk, product_id=product_id).first()
                if cartItem is not None and isinstance(cartItem, CartItem):
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


class shopViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    def shop(self, request):
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
