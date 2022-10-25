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
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.views import APIView


from core.serializers import UserRegisterSerializer, UserSerializer, UserLoginSerializer, UserChangePassSerializer

from core.models import AuthToken, User
from core.handler import create_token, logout


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
        return Response(status=status.HTTP_200_OK)


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

        return Response({"Error": "password is incorrect"}, status=status.HTTP_409_CONFLICT)


class UserInfo(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

