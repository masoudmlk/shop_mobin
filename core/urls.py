from core import views
from django.urls import path, include



urlpatterns = [
    path(r"auth/register/", views.RegisterViewSet.as_view({"post": 'post'})),
    path(r"auth/login/", views.LoginView.as_view()),
    path(r"auth/logout/", views.LogoutView.as_view()),
    path(r"auth/get-profile/", views.ChangeUserInfo.as_view({'get': 'get_user_info'})),
    path(r"auth/set-profile/", views.ChangeUserInfo.as_view({'patch': 'set_user_info'})),
    path(r"auth/change-password/", views.ChangeUserInfo.as_view({'post': 'change_password'})),

    path(r"product/get/<int:product_id>/", views.ProductView.as_view({'get': 'get'})),
    path(r"product/list/", views.ProductView.as_view({'get': 'list'})),

    path(r"opinion/add/<int:product_id>/", views.OpinionView.as_view({'post': 'add'})),
    path(r"opinion/list/<int:product_id>/", views.OpinionView.as_view({'get': 'list'})),

    path(r"score/add/<int:product_id>/", views.ScoreView.as_view({'post': 'add'})),
    path(r"score/get/<int:product_id>/", views.ScoreView.as_view({'get': 'avg_score'})),

    path(r"cart/add/", views.AddListItemTOCart.as_view({'post': 'add_list'})),
    path(r"cart/remove/", views.AddListItemTOCart.as_view({'delete': 'remove_list'})),

    path(r"track/list/", views.TrackViewSet.as_view({'get': 'list'})),
    path(r"track/get/<str:track>/", views.TrackViewSet.as_view({'get': 'retrieve'})),

    # path(r"track/get/<str:track>/", views.TrackViewSet.as_view({'get': 'retrieve'})),

    path(r"shop/", views.shopViewSet.as_view({'get': 'shop'}))

]
