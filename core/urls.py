from core import views
from django.urls import path, include


urlpatterns = [
    path(r"auth/register/", views.RegisterView.as_view()),
    path(r"auth/login/", views.LoginView.as_view()),
    path(r"auth/logout/", views.LogoutView.as_view()),
    path(r"auth/get-profile/", views.UserInfo.as_view({'get': 'retrieve'})),
    path(r"auth/set-profile/", views.UserInfo.as_view({'patch': 'partial_update'})),
    path(r"auth/change-password/", views.ChangePasswordView.as_view()),
]
